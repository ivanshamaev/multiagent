import asyncio
import json
from datetime import UTC, datetime

import httpx2 as httpx
import pytest
from agent_framework import tool
from agent_framework.openai import OpenAIChatCompletionClient
from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict, ValidationError

from runtime.model_provider import (
    MAFModelProvider,
    ModelCatalogError,
    ModelCatalogSnapshot,
    ModelInvocationError,
    ModelOutputValidationError,
    ModelsResponse,
    _validate_structured_text,
    fetch_model_catalog,
    probe_model_tool_calling,
    select_cheapest_agent_model,
    select_cheapest_available_chat_model,
    select_cheapest_chat_model,
)
from tests.fakes import TEST_API_TOKEN, StaticChatClient, gate_settings


class SyntheticResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    task_id: str
    summary: str


def test_structured_text_accepts_one_decorated_object_and_rejects_ambiguity() -> None:
    decorated = 'Result:\n```json\n{"task_id":"TASK-001","summary":"done"}\n```'
    parsed = _validate_structured_text(SyntheticResult, decorated)

    assert parsed.summary == "done"
    with pytest.raises(ValueError):
        _validate_structured_text(
            SyntheticResult,
            ('{"task_id":"TASK-001","summary":"first"}\n{"task_id":"TASK-001","summary":"second"}'),
        )


def catalog_payload() -> dict:
    common = {
        "object": "model",
        "created": 1,
        "owned_by": "provider",
        "description": "test model",
        "category": "CHAT",
    }
    return {
        "object": "list",
        "data": [
            {
                **common,
                "id": "~provider/latest",
                "name": "Virtual latest alias",
                "context_length": 100_000,
                "pricing": {"prompt": 100, "completion": 100},
            },
            {
                **common,
                "id": "model/expensive",
                "name": "Expensive",
                "context_length": 100_000,
                "pricing": {"prompt": 10, "completion": 20},
            },
            {
                **common,
                "id": "model/cheap-b",
                "name": "Cheap B",
                "context_length": 100_000,
                "pricing": {"prompt": 2, "completion": 3},
            },
            {
                **common,
                "id": "model/cheap-a",
                "name": "Cheap A",
                "context_length": 50_000,
                "pricing": {"prompt": 1, "completion": 4},
            },
        ],
    }


def test_settings_redact_and_exclude_token() -> None:
    config = gate_settings()

    assert TEST_API_TOKEN not in repr(config)
    assert TEST_API_TOKEN not in config.model_dump_json()
    assert "api_token" not in config.model_dump()
    with pytest.raises(ValidationError, match="API_TOKEN"):
        gate_settings(api_token="")
    with pytest.raises(ValidationError, match="GateLLM"):
        gate_settings(base_url="https://example.com/v1")


def test_catalog_fetch_authenticates_and_selects_deterministically() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == f"Bearer {TEST_API_TOKEN}"
        return httpx.Response(200, json=catalog_payload())

    snapshot = asyncio.run(
        fetch_model_catalog(gate_settings(), transport=httpx.MockTransport(handler))
    )

    assert select_cheapest_chat_model(snapshot).id == "model/cheap-a"
    assert select_cheapest_chat_model(snapshot, minimum_context_length=75_000).id == "model/cheap-b"
    assert select_cheapest_chat_model(snapshot, requested_model="model/expensive").id == (
        "model/expensive"
    )


def test_explicit_vision_model_is_probe_eligible_but_not_auto_selected() -> None:
    payload = catalog_payload()
    requested = next(model for model in payload["data"] if model["id"] == "model/expensive")
    requested["category"] = "VISION"
    requested["pricing"] = {"prompt": 0, "completion": 0}
    snapshot = ModelCatalogSnapshot(
        retrieved_at=datetime(2026, 9, 6, tzinfo=UTC),
        catalog=ModelsResponse.model_validate(payload),
    )

    assert select_cheapest_chat_model(snapshot).id == "model/cheap-a"
    assert (
        select_cheapest_chat_model(snapshot, requested_model="model/expensive").id
        == "model/expensive"
    )


def test_catalog_rejects_http_and_schema_failures_without_leaking_token() -> None:
    for response in (
        httpx.Response(401, json={"error": "unauthorized"}),
        httpx.Response(200, json={"object": "list", "data": []}),
    ):
        snapshot_call = fetch_model_catalog(
            gate_settings(),
            transport=httpx.MockTransport(lambda request, response=response: response),
        )
        with pytest.raises(ModelCatalogError) as captured:
            asyncio.run(snapshot_call)
        assert TEST_API_TOKEN not in str(captured.value)


def test_selection_rejects_missing_or_incapable_model() -> None:
    payload = catalog_payload()
    next(model for model in payload["data"] if model["id"] == "model/expensive")["category"] = (
        "IMAGE"
    )
    snapshot = ModelCatalogSnapshot(
        retrieved_at=datetime(2026, 9, 6, tzinfo=UTC),
        catalog=ModelsResponse.model_validate(payload),
    )

    with pytest.raises(ModelCatalogError, match="absent"):
        select_cheapest_chat_model(snapshot, requested_model="model/expensive")
    with pytest.raises(ModelCatalogError, match="no CHAT"):
        select_cheapest_chat_model(snapshot, minimum_context_length=200_000)


def test_live_capability_gate_skips_unroutable_cheapest_model() -> None:
    attempts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == f"Bearer {TEST_API_TOKEN}"
        request_payload = json.loads(request.read())
        assert request_payload["response_format"]["type"] == "json_schema"
        assert request_payload["max_tokens"] == 8
        model_id = request_payload["model"]
        if model_id == "model/cheap-a":
            attempts.append("model/cheap-a")
            return httpx.Response(404, json={"error": {"message": "not routed"}})
        attempts.append("model/cheap-b")
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": '{"ok":true}'}}],
                "usage": {"prompt_tokens": 6, "completion_tokens": 1, "total_tokens": 7},
            },
        )

    snapshot = ModelCatalogSnapshot(
        retrieved_at=datetime(2026, 9, 6, tzinfo=UTC),
        catalog=ModelsResponse.model_validate(catalog_payload()),
    )
    selected, probes = asyncio.run(
        select_cheapest_available_chat_model(
            gate_settings(),
            snapshot,
            transport=httpx.MockTransport(handler),
        )
    )

    assert selected.id == "model/cheap-b"
    assert attempts == ["model/cheap-a", "model/cheap-b"]
    assert [probe.available for probe in probes] == [False, True]
    assert probes[-1].usage.total_tokens == 7


def test_live_capability_gate_skips_schema_invalid_200_and_records_usage() -> None:
    attempts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        model_id = json.loads(request.read())["model"]
        attempts.append(model_id)
        if model_id == "model/cheap-a":
            return httpx.Response(
                200,
                json={
                    "choices": [{"message": {"content": "not-json"}}],
                    "usage": {"prompt_tokens": 6, "completion_tokens": 2, "total_tokens": 8},
                },
            )
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": '{"ok":true}'}}],
                "usage": {"prompt_tokens": 6, "completion_tokens": 1, "total_tokens": 7},
            },
        )

    snapshot = ModelCatalogSnapshot(
        retrieved_at=datetime(2026, 9, 6, tzinfo=UTC),
        catalog=ModelsResponse.model_validate(catalog_payload()),
    )
    selected, probes = asyncio.run(
        select_cheapest_available_chat_model(
            gate_settings(),
            snapshot,
            max_candidates=2,
            transport=httpx.MockTransport(handler),
        )
    )

    assert selected.id == "model/cheap-b"
    assert attempts == ["model/cheap-a", "model/cheap-b"]
    assert [probe.available for probe in probes] == [False, True]
    assert probes[0].usage.total_tokens == 8


def test_agent_model_selection_continues_after_tool_gate_failure() -> None:
    attempts: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.read())
        model_id = payload["model"]
        if "tools" not in payload:
            attempts.append((model_id, "schema"))
            return httpx.Response(
                200,
                json={
                    "choices": [{"message": {"content": '{"ok":true}'}}],
                    "usage": {"total_tokens": 2},
                },
            )
        attempts.append((model_id, "tools"))
        if model_id == "model/cheap-a":
            return httpx.Response(404, json={"error": {"message": "tools unavailable"}})
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "tool_calls": [
                                {
                                    "function": {
                                        "name": "ping",
                                        "arguments": '{"value":"ok"}',
                                    }
                                }
                            ]
                        }
                    }
                ],
                "usage": {"total_tokens": 3},
            },
        )

    snapshot = ModelCatalogSnapshot(
        retrieved_at=datetime(2026, 9, 6, tzinfo=UTC),
        catalog=ModelsResponse.model_validate(catalog_payload()),
    )
    selected, schema_probes, tool_probes = asyncio.run(
        select_cheapest_agent_model(
            gate_settings(),
            snapshot,
            transport=httpx.MockTransport(handler),
        )
    )

    assert selected.id == "model/cheap-b"
    assert attempts == [
        ("model/cheap-a", "schema"),
        ("model/cheap-a", "tools"),
        ("model/cheap-b", "schema"),
        ("model/cheap-b", "tools"),
    ]
    assert [probe.available for probe in schema_probes] == [True, True]
    assert [probe.available for probe in tool_probes] == [False, True]


def test_tool_capability_probe_requires_valid_forced_function_call() -> None:
    def valid_handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.read())
        assert payload["tool_choice"] == "required"
        assert payload["max_tokens"] == 64
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "tool_calls": [
                                {
                                    "function": {
                                        "name": "ping",
                                        "arguments": '{"value":"ok"}',
                                    }
                                }
                            ]
                        }
                    }
                ],
                "usage": {"prompt_tokens": 9, "completion_tokens": 3, "total_tokens": 12},
            },
        )

    valid = asyncio.run(
        probe_model_tool_calling(
            gate_settings(),
            "model/cheap-a",
            transport=httpx.MockTransport(valid_handler),
        )
    )
    unavailable = asyncio.run(
        probe_model_tool_calling(
            gate_settings(),
            "model/cheap-a",
            transport=httpx.MockTransport(lambda request: httpx.Response(404)),
        )
    )
    malformed = asyncio.run(
        probe_model_tool_calling(
            gate_settings(),
            "model/cheap-a",
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json={"choices": [{"message": {}}]})
            ),
        )
    )

    assert valid.available and valid.usage.total_tokens == 12
    assert not unavailable.available and unavailable.status_code == 404
    assert not malformed.available and malformed.status_code == 200


def test_tool_capability_probe_aborts_on_account_or_transient_failure() -> None:
    for status_code in (401, 402, 429, 500):
        with pytest.raises(ModelCatalogError, match=str(status_code)):
            asyncio.run(
                probe_model_tool_calling(
                    gate_settings(),
                    "model/cheap-a",
                    transport=httpx.MockTransport(
                        lambda request, status_code=status_code: httpx.Response(status_code)
                    ),
                )
            )


def test_live_capability_gate_validates_configured_model_only() -> None:
    attempts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        model_id = json.loads(request.read())["model"]
        attempts.append(model_id)
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": '{"ok":true}'}}],
                "usage": {"prompt_tokens": 8, "completion_tokens": 5, "total_tokens": 13},
            },
        )

    snapshot = ModelCatalogSnapshot(
        retrieved_at=datetime(2026, 9, 6, tzinfo=UTC),
        catalog=ModelsResponse.model_validate(catalog_payload()),
    )
    selected, probes = asyncio.run(
        select_cheapest_available_chat_model(
            gate_settings(),
            snapshot,
            requested_model="model/expensive",
            transport=httpx.MockTransport(handler),
        )
    )

    assert selected.id == "model/expensive"
    assert attempts == ["model/expensive"]
    assert probes[0].available


def test_live_capability_gate_does_not_mask_transient_or_account_failure() -> None:
    snapshot = ModelCatalogSnapshot(
        retrieved_at=datetime(2026, 9, 6, tzinfo=UTC),
        catalog=ModelsResponse.model_validate(catalog_payload()),
    )
    for status_code in (401, 402, 429, 500):
        with pytest.raises(ModelCatalogError, match=str(status_code)):
            asyncio.run(
                select_cheapest_available_chat_model(
                    gate_settings(),
                    snapshot,
                    transport=httpx.MockTransport(
                        lambda request, status_code=status_code: httpx.Response(
                            status_code, json={"error": {"message": "failure"}}
                        )
                    ),
                )
            )


def test_live_capability_gate_reports_only_safe_statuses_when_all_models_fail() -> None:
    snapshot = ModelCatalogSnapshot(
        retrieved_at=datetime(2026, 9, 6, tzinfo=UTC),
        catalog=ModelsResponse.model_validate(catalog_payload()),
    )

    with pytest.raises(ModelCatalogError) as captured:
        asyncio.run(
            select_cheapest_available_chat_model(
                gate_settings(),
                snapshot,
                requested_model="model/cheap-a",
                transport=httpx.MockTransport(
                    lambda request: httpx.Response(400, json={"error": {"message": TEST_API_TOKEN}})
                ),
            )
        )

    assert str(captured.value).endswith("probes=model/cheap-a=HTTP400")
    assert TEST_API_TOKEN not in str(captured.value)


def test_maf_provider_parses_structured_output_and_records_safe_metadata() -> None:
    client = StaticChatClient('{"task_id":"TASK-001","summary":"done"}')
    provider = MAFModelProvider(gate_settings(), client=client)

    invocation = asyncio.run(
        provider.generate(
            SyntheticResult,
            system_prompt="Return strict JSON.",
            user_prompt="Return the synthetic result.",
        )
    )

    assert invocation.value == SyntheticResult(task_id="TASK-001", summary="done")
    assert invocation.usage.total_tokens == 15
    assert invocation.finish_reason == "stop"
    assert len(invocation.request_sha256) == 64
    assert len(invocation.response_sha256) == 64
    assert client.messages[-1].text == "Return the synthetic result."
    assert client.options["response_format"] is SyntheticResult
    assert TEST_API_TOKEN not in repr(provider)
    assert TEST_API_TOKEN not in invocation.model_dump_json()


def test_maf_provider_exposes_only_explicit_tools_for_bounded_generation() -> None:
    @tool(name="safe_read", approval_mode="never_require")
    async def safe_read(path: str) -> str:
        return path

    client = StaticChatClient('{"task_id":"TASK-001","summary":"done"}')
    provider = MAFModelProvider(
        gate_settings(),
        client=client,
        max_tool_iterations=3,
        max_function_calls=4,
    )

    invocation = asyncio.run(
        provider.generate_with_tools(
            SyntheticResult,
            system_prompt="Return strict JSON.",
            user_prompt="Use only the safe tool when needed.",
            tools=(safe_read,),
        )
    )

    assert invocation.value.summary == "done"
    assert [item.name for item in client.options["tools"]] == ["safe_read"]
    assert "response_format" not in client.options
    assert "matching this schema" in client.messages[0].text
    assert len(invocation.request_sha256) == 64


def test_phased_provider_requires_one_initial_tool_without_provider_schema_mode() -> None:
    @tool(name="safe_read", approval_mode="never_require")
    async def safe_read(path: str) -> str:
        return path

    client = StaticChatClient('{"task_id":"TASK-001","summary":"done"}')
    provider = MAFModelProvider(
        gate_settings(),
        client=client,
        max_tool_iterations=1,
        require_initial_tool_call=True,
    )

    asyncio.run(
        provider.generate_with_tools(
            SyntheticResult,
            system_prompt="Use the tool, then return strict JSON.",
            user_prompt="Inspect the task.",
            tools=(safe_read,),
        )
    )

    assert client.options["tool_choice"] == "required"
    assert client.options["parallel_tool_calls"] is False
    assert "response_format" not in client.options
    assert "matching this schema" in client.messages[0].text


@pytest.mark.parametrize(
    ("iterations", "calls"),
    ((0, 1), (41, 1), (1, 0), (1, 257), (True, 1)),
)
def test_maf_provider_rejects_unbounded_tool_loop(iterations: int, calls: int) -> None:
    with pytest.raises(ValueError):
        MAFModelProvider(
            gate_settings(),
            client=StaticChatClient("{}"),
            max_tool_iterations=iterations,
            max_function_calls=calls,
        )


def test_maf_provider_rejects_malformed_or_extra_structured_output() -> None:
    for payload in (
        "not-json",
        '{"task_id":"TASK-001","summary":"done","unexpected":true}',
    ):
        provider = MAFModelProvider(gate_settings(), client=StaticChatClient(payload))
        with pytest.raises(ModelOutputValidationError) as captured:
            asyncio.run(
                provider.generate(
                    SyntheticResult,
                    system_prompt="Return strict JSON.",
                    user_prompt="Return the synthetic result.",
                )
            )
        assert captured.value.model_call.usage.total_tokens == 15
        assert len(captured.value.model_call.response_sha256) == 64
        assert payload not in str(captured.value)


def test_openai_transport_retries_429_once_and_normalizes_response() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(
                429,
                headers={"retry-after": "0"},
                json={"error": {"message": "rate limited", "type": "rate_limit_error"}},
            )
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 1_788_653_000,
                "model": "fake/cheap-model",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": '{"task_id":"TASK-001","summary":"done"}',
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            },
        )

    async def invoke():
        http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        openai_client = AsyncOpenAI(
            api_key=TEST_API_TOKEN,
            base_url="https://gatellm.ru/v1",
            max_retries=1,
            http_client=http_client,
        )
        provider = MAFModelProvider(
            gate_settings(max_retries=1),
            client=OpenAIChatCompletionClient(
                model="fake/cheap-model",
                async_client=openai_client,
            ),
        )
        try:
            return await provider.generate(
                SyntheticResult,
                system_prompt="Return strict JSON.",
                user_prompt="Return the synthetic result.",
            )
        finally:
            await openai_client.close()

    invocation = asyncio.run(invoke())

    assert calls == 2
    assert invocation.value.task_id == "TASK-001"
    assert invocation.usage.total_tokens == 15


def test_provider_error_is_sanitized_and_auth_failure_is_not_retried() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            401,
            json={"error": {"message": TEST_API_TOKEN, "type": "authentication_error"}},
        )

    async def invoke() -> None:
        http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        openai_client = AsyncOpenAI(
            api_key=TEST_API_TOKEN,
            base_url="https://gatellm.ru/v1",
            max_retries=1,
            http_client=http_client,
        )
        provider = MAFModelProvider(
            gate_settings(max_retries=1),
            client=OpenAIChatCompletionClient(
                model="fake/cheap-model",
                async_client=openai_client,
            ),
        )
        try:
            await provider.generate(
                SyntheticResult,
                system_prompt="Return strict JSON.",
                user_prompt="Return the synthetic result.",
            )
        finally:
            await openai_client.close()

    with pytest.raises(ModelInvocationError) as captured:
        asyncio.run(invoke())

    assert calls == 1
    assert TEST_API_TOKEN not in str(captured.value)
    assert "AuthenticationError" in str(captured.value)
    assert "http_status=401" in str(captured.value)


def test_provider_retries_timeout_within_bound_and_sanitizes_failure() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout(TEST_API_TOKEN, request=request)

    async def invoke() -> None:
        http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        openai_client = AsyncOpenAI(
            api_key=TEST_API_TOKEN,
            base_url="https://gatellm.ru/v1",
            max_retries=1,
            http_client=http_client,
        )
        provider = MAFModelProvider(
            gate_settings(max_retries=1),
            client=OpenAIChatCompletionClient(
                model="fake/cheap-model",
                async_client=openai_client,
            ),
        )
        try:
            await provider.generate(
                SyntheticResult,
                system_prompt="Return strict JSON.",
                user_prompt="Return the synthetic result.",
            )
        finally:
            await openai_client.close()

    with pytest.raises(ModelInvocationError) as captured:
        asyncio.run(invoke())

    assert calls == 2
    assert TEST_API_TOKEN not in str(captured.value)
    assert "APITimeoutError" in str(captured.value)


def test_provider_allows_bounded_recovery_from_safe_tool_errors() -> None:
    provider = MAFModelProvider(gate_settings(), model_id="fake/cheap-model")

    assert provider._function_invocation_configuration == {
        "max_iterations": 12,
        "max_function_calls": 80,
        "max_consecutive_errors_per_request": 3,
        "terminate_on_unknown_calls": True,
        "include_detailed_errors": True,
    }
