"""Cost-aware GateLLM catalog and Microsoft Agent Framework model adapter."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal
from hashlib import sha256
from time import monotonic
from typing import Annotated, Literal, Protocol, TypeVar, cast

import httpx2 as httpx
from agent_framework import Agent, AgentResponse, BaseChatClient, FunctionTool
from agent_framework.openai import OpenAIChatCompletionClient
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, StringConstraints, ValidationError

from contracts.common import (
    FrozenModel,
    NonNegativeInt,
    PositiveInt,
    Sha256,
    ShortText,
    UtcDateTime,
)
from runtime.settings import GateLLMSettings, ModelIdentifier

PromptText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=50_000),
]
ResponseT = TypeVar("ResponseT", bound=BaseModel)


def _validate_structured_text[StructuredT: BaseModel](
    response_model: type[StructuredT], text: str
) -> StructuredT:
    """Accept direct JSON or one unambiguous schema-valid object inside model decoration."""

    try:
        return response_model.model_validate_json(text)
    except ValueError as direct_error:
        candidates: list[StructuredT] = []
        decoder = json.JSONDecoder()
        for index, character in enumerate(text):
            if character != "{":
                continue
            try:
                payload, _ = decoder.raw_decode(text[index:])
                candidate = response_model.model_validate(payload)
            except (TypeError, ValueError):
                continue
            candidates.append(candidate)
            if len(candidates) > 1:
                break
        if len(candidates) == 1:
            return candidates[0]
        raise direct_error


class ModelCatalogError(RuntimeError):
    """A catalog could not be retrieved, validated, or selected safely."""


class ModelInvocationError(RuntimeError):
    """A provider/transport failure safe to expose without request details."""


def _safe_error_fingerprint(error: BaseException) -> str:
    pending: list[BaseException] = [error]
    seen: set[int] = set()
    names: list[str] = []
    statuses: set[int] = set()
    provider_codes: set[str] = set()
    provider_types: set[str] = set()
    while pending and len(seen) < 8:
        current = pending.pop(0)
        if id(current) in seen:
            continue
        seen.add(id(current))
        names.append(type(current).__name__)
        status = getattr(current, "status_code", None)
        if isinstance(status, int):
            statuses.add(status)
        body = getattr(current, "body", None)
        if isinstance(body, dict):
            for key, destination in (("code", provider_codes), ("type", provider_types)):
                value = body.get(key)
                if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", value):
                    destination.add(value)
        pending.extend(
            nested
            for nested in (current.__cause__, current.__context__, *current.args)
            if isinstance(nested, BaseException)
        )
    status_text = ",".join(str(status) for status in sorted(statuses)) or "none"
    code_text = ",".join(sorted(provider_codes)) or "none"
    provider_type_text = ",".join(sorted(provider_types)) or "none"
    return (
        f"types={','.join(names)};http_status={status_text};"
        f"provider_code={code_text};provider_type={provider_type_text}"
    )


class ModelPricing(FrozenModel):
    prompt: Decimal = Field(ge=0)
    completion: Decimal = Field(ge=0)

    @property
    def cost_first_score(self) -> Decimal:
        return self.prompt + self.completion


class AvailableModel(FrozenModel):
    id: ModelIdentifier
    object: Literal["model"]
    created: NonNegativeInt
    owned_by: ShortText
    name: ShortText
    description: str = Field(max_length=5_000)
    context_length: PositiveInt
    category: ShortText
    pricing: ModelPricing


class ModelsResponse(FrozenModel):
    object: Literal["list"]
    data: tuple[AvailableModel, ...] = Field(min_length=1, max_length=1_000)


class ModelCatalogSnapshot(FrozenModel):
    retrieved_at: UtcDateTime
    source: Literal["https://gatellm.ru/v1/models"] = "https://gatellm.ru/v1/models"
    catalog: ModelsResponse


def _is_chat_candidate(model: AvailableModel, requested_model: str | None) -> bool:
    """Treat an explicitly requested VISION model as chat-capable after live probes."""

    return model.category == "CHAT" or (requested_model == model.id and model.category == "VISION")


class ModelUsage(FrozenModel):
    input_tokens: NonNegativeInt = 0
    output_tokens: NonNegativeInt = 0
    total_tokens: NonNegativeInt = 0


class ModelCapabilityProbe(FrozenModel):
    model_id: ModelIdentifier
    status_code: PositiveInt
    available: bool
    usage: ModelUsage = Field(default_factory=ModelUsage)


class ModelInvocation[ValueT: BaseModel](FrozenModel):
    """Validated value plus safe metadata; raw prompts and completions are excluded."""

    value: ValueT = Field(repr=False)
    model_id: ModelIdentifier
    usage: ModelUsage
    latency_ms: NonNegativeInt
    finish_reason: ShortText | None = None
    request_sha256: Sha256
    response_sha256: Sha256


class ModelCallRecord(FrozenModel):
    """Safe persistent metadata extracted from a model invocation."""

    model_id: str = Field(min_length=1, max_length=200)
    usage: ModelUsage
    latency_ms: NonNegativeInt
    finish_reason: str | None = Field(default=None, min_length=1, max_length=512)
    request_sha256: Sha256
    response_sha256: Sha256


class ModelOutputValidationError(ModelInvocationError):
    """A response failed local schema validation; raw output remains excluded."""

    def __init__(self, codes: tuple[str, ...], model_call: ModelCallRecord) -> None:
        super().__init__(f"model output failed closed validation: codes={','.join(codes)}")
        self.codes = codes
        self.model_call = model_call


def model_call_record(invocation: ModelInvocation[BaseModel]) -> ModelCallRecord:
    return ModelCallRecord(
        model_id=invocation.model_id,
        usage=invocation.usage,
        latency_ms=invocation.latency_ms,
        finish_reason=invocation.finish_reason,
        request_sha256=invocation.request_sha256,
        response_sha256=invocation.response_sha256,
    )


class StructuredModelProvider(Protocol):
    async def generate(
        self,
        response_model: type[ResponseT],
        *,
        system_prompt: PromptText,
        user_prompt: PromptText,
    ) -> ModelInvocation[ResponseT]: ...


class ToolEnabledStructuredModelProvider(StructuredModelProvider, Protocol):
    async def generate_with_tools(
        self,
        response_model: type[ResponseT],
        *,
        system_prompt: PromptText,
        user_prompt: PromptText,
        tools: Sequence[FunctionTool],
    ) -> ModelInvocation[ResponseT]: ...


async def fetch_model_catalog(
    settings: GateLLMSettings,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> ModelCatalogSnapshot:
    """Fetch model metadata without exposing the bearer token in raised errors."""

    try:
        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds,
            transport=transport,
        ) as client:
            response = await client.get(
                f"{settings.base_url}/models",
                headers={"Authorization": f"Bearer {settings.api_token.get_secret_value()}"},
            )
    except httpx.HTTPError as error:
        raise ModelCatalogError(
            f"GateLLM model catalog transport failed: {type(error).__name__}"
        ) from None

    if not 200 <= response.status_code < 300:
        raise ModelCatalogError(f"GateLLM model catalog returned HTTP {response.status_code}")
    try:
        catalog = ModelsResponse.model_validate(response.json())
    except (ValueError, TypeError) as error:
        raise ModelCatalogError(
            f"GateLLM model catalog is invalid: {type(error).__name__}"
        ) from None
    return ModelCatalogSnapshot(retrieved_at=datetime.now(UTC), catalog=catalog)


def select_cheapest_chat_model(
    snapshot: ModelCatalogSnapshot,
    *,
    minimum_context_length: int = 1,
    requested_model: str | None = None,
) -> AvailableModel:
    """Select a chat-capable model using a deterministic cost-first ordering."""

    candidates = tuple(
        model
        for model in snapshot.catalog.data
        if _is_chat_candidate(model, requested_model)
        and model.context_length >= minimum_context_length
    )
    if requested_model is not None:
        candidates = tuple(model for model in candidates if model.id == requested_model)
        if not candidates:
            raise ModelCatalogError(
                "requested model is absent or does not satisfy chat/context gates"
            )
    if not candidates:
        raise ModelCatalogError("catalog has no CHAT model satisfying the context gate")
    return min(candidates, key=lambda model: (model.pricing.cost_first_score, model.id))


async def select_cheapest_available_chat_model(
    settings: GateLLMSettings,
    snapshot: ModelCatalogSnapshot,
    *,
    max_candidates: int = 10,
    requested_model: str | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> tuple[AvailableModel, tuple[ModelCapabilityProbe, ...]]:
    """Probe schema mode in cost order, or validate one requested chat-capable model."""

    if isinstance(max_candidates, bool) or not 1 <= max_candidates <= 20:
        raise ModelCatalogError("max_candidates must be an integer between 1 and 20")
    candidates = sorted(
        (
            model
            for model in snapshot.catalog.data
            if _is_chat_candidate(model, requested_model)
            and (requested_model is None or model.id == requested_model)
        ),
        key=lambda model: (model.pricing.cost_first_score, model.id),
    )[:max_candidates]
    if not candidates:
        qualifier = "requested " if requested_model is not None else ""
        raise ModelCatalogError(f"catalog has no {qualifier}chat-capable model to probe")
    probes: list[ModelCapabilityProbe] = []
    try:
        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds,
            transport=transport,
        ) as client:
            for model in candidates:
                response = await client.post(
                    f"{settings.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {settings.api_token.get_secret_value()}"},
                    json={
                        "model": model.id,
                        "messages": [
                            {"role": "user", "content": "Return JSON with ok set to true"}
                        ],
                        "response_format": {
                            "type": "json_schema",
                            "json_schema": {
                                "name": "capability_probe",
                                "strict": True,
                                "schema": {
                                    "type": "object",
                                    "properties": {"ok": {"type": "boolean"}},
                                    "required": ["ok"],
                                    "additionalProperties": False,
                                },
                            },
                        },
                        "max_tokens": 8,
                        "temperature": 0,
                    },
                )
                if response.status_code in {400, 404}:
                    probes.append(
                        ModelCapabilityProbe(
                            model_id=model.id,
                            status_code=response.status_code,
                            available=False,
                        )
                    )
                    continue
                if not 200 <= response.status_code < 300:
                    raise ModelCatalogError(
                        f"GateLLM capability probe returned HTTP {response.status_code}"
                    )
                try:
                    payload = response.json()
                except ValueError:
                    probes.append(
                        ModelCapabilityProbe(
                            model_id=model.id,
                            status_code=response.status_code,
                            available=False,
                        )
                    )
                    continue
                usage = ModelUsage()
                if isinstance(payload, dict):
                    usage_payload = payload.get("usage") or {}
                    if isinstance(usage_payload, dict):
                        try:
                            usage = ModelUsage(
                                input_tokens=usage_payload.get("prompt_tokens", 0),
                                output_tokens=usage_payload.get("completion_tokens", 0),
                                total_tokens=usage_payload.get("total_tokens", 0),
                            )
                        except ValueError:
                            usage = ModelUsage()
                try:
                    choices = payload["choices"]
                    content = choices[0]["message"]["content"]
                    if not isinstance(content, str):
                        raise ValueError("missing completion")
                    structured = json.loads(content)
                    if not isinstance(structured, dict) or structured.get("ok") is not True:
                        raise ValueError("invalid structured completion")
                except (KeyError, IndexError, TypeError, ValueError):
                    probes.append(
                        ModelCapabilityProbe(
                            model_id=model.id,
                            status_code=response.status_code,
                            available=False,
                            usage=usage,
                        )
                    )
                    continue
                probes.append(
                    ModelCapabilityProbe(
                        model_id=model.id,
                        status_code=response.status_code,
                        available=True,
                        usage=usage,
                    )
                )
                return model, tuple(probes)
    except httpx.HTTPError as error:
        raise ModelCatalogError(
            f"GateLLM capability transport failed: {type(error).__name__}"
        ) from None
    outcomes = ",".join(f"{probe.model_id}=HTTP{probe.status_code}" for probe in probes)
    raise ModelCatalogError(
        f"no CHAT candidate passed the structured capability gate; probes={outcomes}"
    )


async def probe_model_tool_calling(
    settings: GateLLMSettings,
    model_id: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> ModelCapabilityProbe:
    """Verify OpenAI-compatible function calling with one minimal forced tool request."""

    try:
        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds,
            transport=transport,
        ) as client:
            response = await client.post(
                f"{settings.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.api_token.get_secret_value()}"},
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": "Call ping with value ok."}],
                    "tools": [
                        {
                            "type": "function",
                            "function": {
                                "name": "ping",
                                "description": "Return one value.",
                                "parameters": {
                                    "type": "object",
                                    "properties": {"value": {"type": "string"}},
                                    "required": ["value"],
                                    "additionalProperties": False,
                                },
                            },
                        }
                    ],
                    "tool_choice": "required",
                    "max_tokens": 64,
                    "temperature": 0,
                },
            )
    except httpx.HTTPError as error:
        raise ModelCatalogError(
            f"GateLLM tool probe transport failed: {type(error).__name__}"
        ) from None
    if response.status_code in {400, 404}:
        return ModelCapabilityProbe(
            model_id=model_id,
            status_code=response.status_code,
            available=False,
        )
    if not 200 <= response.status_code < 300:
        raise ModelCatalogError(f"GateLLM tool probe returned HTTP {response.status_code}")
    usage = ModelUsage()
    valid = False
    try:
        payload = response.json()
        usage_payload = payload.get("usage") or {}
        usage = ModelUsage(
            input_tokens=usage_payload.get("prompt_tokens", 0),
            output_tokens=usage_payload.get("completion_tokens", 0),
            total_tokens=usage_payload.get("total_tokens", 0),
        )
        calls = payload["choices"][0]["message"].get("tool_calls") or []
        function = calls[0]["function"]
        arguments = json.loads(function["arguments"])
        valid = function["name"] == "ping" and isinstance(arguments.get("value"), str)
    except (AttributeError, KeyError, IndexError, TypeError, ValueError):
        valid = False
    return ModelCapabilityProbe(
        model_id=model_id,
        status_code=response.status_code,
        available=valid,
        usage=usage,
    )


async def select_cheapest_agent_model(
    settings: GateLLMSettings,
    snapshot: ModelCatalogSnapshot,
    *,
    max_candidates: int = 10,
    requested_model: str | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> tuple[
    AvailableModel,
    tuple[ModelCapabilityProbe, ...],
    tuple[ModelCapabilityProbe, ...],
]:
    """Select the cheapest chat-capable model passing schema and tool-calling gates."""

    if isinstance(max_candidates, bool) or not 1 <= max_candidates <= 20:
        raise ModelCatalogError("max_candidates must be an integer between 1 and 20")
    remaining = sorted(
        (
            model
            for model in snapshot.catalog.data
            if _is_chat_candidate(model, requested_model)
            and (requested_model is None or model.id == requested_model)
        ),
        key=lambda model: (model.pricing.cost_first_score, model.id),
    )[:max_candidates]
    if not remaining:
        raise ModelCatalogError("catalog has no requested chat-capable model to probe")
    schema_probes: list[ModelCapabilityProbe] = []
    tool_probes: list[ModelCapabilityProbe] = []
    while remaining:
        narrowed = snapshot.model_copy(
            update={"catalog": snapshot.catalog.model_copy(update={"data": tuple(remaining)})}
        )
        selected, current_schema_probes = await select_cheapest_available_chat_model(
            settings,
            narrowed,
            max_candidates=len(remaining),
            requested_model=requested_model,
            transport=transport,
        )
        schema_probes.extend(current_schema_probes)
        tool_probe = await probe_model_tool_calling(
            settings,
            selected.id,
            transport=transport,
        )
        tool_probes.append(tool_probe)
        if tool_probe.available:
            return selected, tuple(schema_probes), tuple(tool_probes)
        remaining = [model for model in remaining if model.id != selected.id]
        if requested_model is not None:
            break
    outcomes = ",".join(f"{probe.model_id}=HTTP{probe.status_code}" for probe in tool_probes)
    raise ModelCatalogError(f"no schema-capable chat model passed the tool gate; probes={outcomes}")


class MAFModelProvider:
    """Run one structured MAF agent against GateLLM Chat Completions."""

    def __init__(
        self,
        settings: GateLLMSettings,
        *,
        model_id: str | None = None,
        client: BaseChatClient | None = None,
        max_tool_iterations: int = 12,
        max_function_calls: int = 80,
        require_initial_tool_call: bool = False,
    ) -> None:
        selected_model = model_id or settings.default_model
        if selected_model is None:
            raise ValueError("a model must be selected before creating the provider")
        self.settings = settings
        self.model_id = cast(ModelIdentifier, selected_model)
        self._client = client
        self._require_initial_tool_call = require_initial_tool_call
        if isinstance(max_tool_iterations, bool) or not 1 <= max_tool_iterations <= 40:
            raise ValueError("max_tool_iterations must be between 1 and 40")
        if isinstance(max_function_calls, bool) or not 1 <= max_function_calls <= 256:
            raise ValueError("max_function_calls must be between 1 and 256")
        self._function_invocation_configuration = {
            "max_iterations": max_tool_iterations,
            "max_function_calls": max_function_calls,
            # Cheap models may need one bounded retry to correct tool arguments.
            "max_consecutive_errors_per_request": 3,
            "terminate_on_unknown_calls": True,
            # Facade/gateway exceptions are deliberately sanitized before MAF sees them.
            "include_detailed_errors": True,
        }

    def __repr__(self) -> str:
        return f"MAFModelProvider(model_id={self.model_id!r}, base_url={self.settings.base_url!r})"

    def _get_client(self) -> BaseChatClient:
        if self._client is None:
            openai_client = AsyncOpenAI(
                api_key=self.settings.api_token.get_secret_value(),
                base_url=self.settings.base_url,
                timeout=self.settings.request_timeout_seconds,
                max_retries=self.settings.max_retries,
            )
            self._client = OpenAIChatCompletionClient(
                model=self.model_id,
                async_client=openai_client,
                function_invocation_configuration=self._function_invocation_configuration,
            )
        return self._client

    async def generate(
        self,
        response_model: type[ResponseT],
        *,
        system_prompt: PromptText,
        user_prompt: PromptText,
    ) -> ModelInvocation[ResponseT]:
        return await self._generate(
            response_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=(),
        )

    async def generate_with_tools(
        self,
        response_model: type[ResponseT],
        *,
        system_prompt: PromptText,
        user_prompt: PromptText,
        tools: Sequence[FunctionTool],
    ) -> ModelInvocation[ResponseT]:
        """Run a bounded MAF function loop using only caller-supplied safe tools."""

        if not tools:
            raise ValueError("tool-enabled generation requires at least one tool")
        return await self._generate(
            response_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=tuple(tools),
        )

    async def _generate(
        self,
        response_model: type[ResponseT],
        *,
        system_prompt: PromptText,
        user_prompt: PromptText,
        tools: Sequence[FunctionTool],
    ) -> ModelInvocation[ResponseT]:
        effective_user_prompt = user_prompt
        default_options: dict[str, object] = {
            "max_tokens": self.settings.max_output_tokens,
            "temperature": 0.0,
        }
        if tools:
            schema = json.dumps(
                response_model.model_json_schema(),
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            effective_user_prompt = (
                f"{user_prompt}\nWhen all tool work is complete, return only JSON matching "
                f"this schema: {schema}"
            )
            if self._require_initial_tool_call:
                # MAF resets `required` after the first tool batch and then requests
                # a final response with tools disabled.
                default_options["tool_choice"] = "required"
                default_options["parallel_tool_calls"] = False
        else:
            default_options["response_format"] = response_model
        tool_names = ",".join(sorted(item.name for item in tools))
        request_sha256 = sha256(
            f"{system_prompt}\x00{effective_user_prompt}\x00{tool_names}".encode()
        ).hexdigest()
        started = monotonic()
        try:
            agent = Agent(
                client=self._get_client(),
                name="controlled-structured-agent",
                instructions=system_prompt,
                tools=tools or None,
                default_options=default_options,
            )
            response = await agent.run(effective_user_prompt)
        except Exception as error:
            raise ModelInvocationError(
                f"GateLLM model invocation failed: {_safe_error_fingerprint(error)}"
            ) from None
        if not isinstance(response, AgentResponse):  # pragma: no cover - guarded by stream=False
            raise TypeError("MAF returned a streaming response for a non-streaming invocation")

        usage_details = response.usage_details or {}
        input_tokens = usage_details.get("input_token_count") or 0
        output_tokens = usage_details.get("output_token_count") or 0
        total_tokens = usage_details.get("total_token_count")
        usage = ModelUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens if total_tokens is not None else input_tokens + output_tokens,
        )
        finish_reason = response.finish_reason
        normalized_finish_reason = (
            str(getattr(finish_reason, "value", finish_reason))
            if finish_reason is not None
            else None
        )
        record = ModelCallRecord(
            model_id=self.model_id,
            usage=usage,
            latency_ms=max(0, round((monotonic() - started) * 1_000)),
            finish_reason=normalized_finish_reason,
            request_sha256=request_sha256,
            response_sha256=sha256(response.text.encode("utf-8")).hexdigest(),
        )
        try:
            parsed = response.value
            if parsed is None:
                value = _validate_structured_text(response_model, response.text)
            else:
                value = response_model.model_validate(parsed)
        except (TypeError, ValueError) as error:
            codes = (
                tuple(sorted({str(item["type"]) for item in error.errors()}))
                if isinstance(error, ValidationError)
                else (type(error).__name__,)
            )
            raise ModelOutputValidationError(codes, record) from None
        return ModelInvocation(
            value=value,
            model_id=self.model_id,
            usage=usage,
            latency_ms=record.latency_ms,
            finish_reason=normalized_finish_reason,
            request_sha256=request_sha256,
            response_sha256=record.response_sha256,
        )
