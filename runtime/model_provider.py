"""Cost-aware GateLLM catalog and Microsoft Agent Framework model adapter."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from hashlib import sha256
from time import monotonic
from typing import Annotated, Literal, Protocol, TypeVar, cast

import httpx2 as httpx
from agent_framework import Agent, AgentResponse, BaseChatClient
from agent_framework.openai import OpenAIChatCompletionClient
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, StringConstraints

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


class ModelCatalogError(RuntimeError):
    """A catalog could not be retrieved, validated, or selected safely."""


class ModelInvocationError(RuntimeError):
    """A provider/transport failure safe to expose without request details."""


def _safe_error_fingerprint(error: BaseException) -> str:
    pending: list[BaseException] = [error]
    seen: set[int] = set()
    names: list[str] = []
    statuses: set[int] = set()
    while pending and len(seen) < 8:
        current = pending.pop(0)
        if id(current) in seen:
            continue
        seen.add(id(current))
        names.append(type(current).__name__)
        status = getattr(current, "status_code", None)
        if isinstance(status, int):
            statuses.add(status)
        pending.extend(
            nested
            for nested in (current.__cause__, current.__context__, *current.args)
            if isinstance(nested, BaseException)
        )
    status_text = ",".join(str(status) for status in sorted(statuses)) or "none"
    return f"types={','.join(names)};http_status={status_text}"


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


class StructuredModelProvider(Protocol):
    async def generate(
        self,
        response_model: type[ResponseT],
        *,
        system_prompt: PromptText,
        user_prompt: PromptText,
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
    """Select a capable CHAT model using a deterministic cost-first ordering."""

    candidates = tuple(
        model
        for model in snapshot.catalog.data
        if model.category == "CHAT" and model.context_length >= minimum_context_length
    )
    if requested_model is not None:
        candidates = tuple(model for model in candidates if model.id == requested_model)
        if not candidates:
            raise ModelCatalogError(
                "requested model is absent or does not satisfy CHAT/context gates"
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
    """Probe schema mode in cost order, or validate one configured CHAT model."""

    if isinstance(max_candidates, bool) or not 1 <= max_candidates <= 20:
        raise ModelCatalogError("max_candidates must be an integer between 1 and 20")
    candidates = sorted(
        (
            model
            for model in snapshot.catalog.data
            if model.category == "CHAT" and (requested_model is None or model.id == requested_model)
        ),
        key=lambda model: (model.pricing.cost_first_score, model.id),
    )[:max_candidates]
    if not candidates:
        qualifier = "requested " if requested_model is not None else ""
        raise ModelCatalogError(f"catalog has no {qualifier}CHAT model to probe")
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
                    choices = payload["choices"]
                    content = choices[0]["message"]["content"]
                    usage_payload = payload.get("usage") or {}
                    if not isinstance(content, str):
                        raise ValueError("missing completion")
                    structured = json.loads(content)
                    if not isinstance(structured, dict) or structured.get("ok") is not True:
                        raise ValueError("invalid structured completion")
                    usage = ModelUsage(
                        input_tokens=usage_payload.get("prompt_tokens", 0),
                        output_tokens=usage_payload.get("completion_tokens", 0),
                        total_tokens=usage_payload.get("total_tokens", 0),
                    )
                except (KeyError, IndexError, TypeError, ValueError):
                    raise ModelCatalogError("GateLLM capability response is invalid") from None
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


class MAFModelProvider:
    """Run one structured MAF agent against GateLLM Chat Completions."""

    def __init__(
        self,
        settings: GateLLMSettings,
        *,
        model_id: str | None = None,
        client: BaseChatClient | None = None,
    ) -> None:
        selected_model = model_id or settings.default_model
        if selected_model is None:
            raise ValueError("a model must be selected before creating the provider")
        self.settings = settings
        self.model_id = cast(ModelIdentifier, selected_model)
        self._client = client

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
            )
        return self._client

    async def generate(
        self,
        response_model: type[ResponseT],
        *,
        system_prompt: PromptText,
        user_prompt: PromptText,
    ) -> ModelInvocation[ResponseT]:
        request_sha256 = sha256(f"{system_prompt}\x00{user_prompt}".encode()).hexdigest()
        started = monotonic()
        try:
            agent = Agent(
                client=self._get_client(),
                name="controlled-structured-agent",
                instructions=system_prompt,
                default_options={
                    "max_tokens": self.settings.max_output_tokens,
                    "response_format": response_model,
                    "temperature": 0.0,
                },
            )
            response = await agent.run(user_prompt)
        except Exception as error:
            raise ModelInvocationError(
                f"GateLLM model invocation failed: {_safe_error_fingerprint(error)}"
            ) from None
        if not isinstance(response, AgentResponse):  # pragma: no cover - guarded by stream=False
            raise TypeError("MAF returned a streaming response for a non-streaming invocation")

        parsed = response.value
        if parsed is None:
            parsed = response_model.model_validate_json(response.text)
        value = response_model.model_validate(parsed)
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
        return ModelInvocation(
            value=value,
            model_id=self.model_id,
            usage=usage,
            latency_ms=max(0, round((monotonic() - started) * 1_000)),
            finish_reason=normalized_finish_reason,
            request_sha256=request_sha256,
            response_sha256=sha256(response.text.encode("utf-8")).hexdigest(),
        )
