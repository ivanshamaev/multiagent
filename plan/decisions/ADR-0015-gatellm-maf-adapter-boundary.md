# ADR-0015 — GateLLM provider и Microsoft Agent Framework adapter boundary

Status: accepted

Date: 2026-09-06

## Context

GateLLM предоставляет OpenAI-compatible `/v1/models` и `/v1/chat/completions`, использует bearer
token из `API_TOKEN` и не предоставляет Responses API. Microsoft Agent Framework 1.17 разделяет
OpenAI clients: `OpenAIChatClient` использует Responses API, а `OpenAIChatCompletionClient` — Chat
Completions. Domain reducer STEP-0006 не должен зависеть от SDK messages или разрешать framework
менять transition policy.

Проверенный `research-agent` pattern использует lazy `AsyncOpenAI`, custom `base_url`, internal
client protocol и normalized response. Для этой системы нужны дополнительные fail-closed
requirements: secret redaction, typed usage, exact retry classification и budget enforcement.

## Decision

Закрепляем selective dependencies `agent-framework-core==1.17.0` и
`agent-framework-openai==1.14.2`, а не meta-package со всеми integrations. GateLLM adapter использует
`OpenAIChatCompletionClient` с явными `api_key`, `base_url=https://gatellm.ru/v1` и model; никакие
`OPENAI_*` environment fallbacks не являются источником конфигурации.

Внутренний `ModelProvider` boundary владеет validated settings, model selection, timeout/retry
policy и normalized usage/result. MAF владеет только agent/executor message flow. Тонкий adapter
переводит framework response в domain artifact через обычную Pydantic validation; только затем
code workflow вызывает существующий reducer. Ни provider, ни MAF не создают произвольный next
state и не списывают неподтверждённые budget values.

Cheapest CHAT model выбирается из датированного `/models` snapshot по сумме prompt/completion price
с deterministic tie-breaker и optional explicit override. Catalog retrieval не запускается при
обычном import/test. Unit tests используют fake provider; live catalog/completion — отдельные
opt-in targets. Retries ограничены и разрешены для 429 и server/transport failures до получения
response; 400/401/402 и schema failures не повторяются.

`API_TOKEN` хранится как secret type, не сериализуется и не попадает в repr/log/event. Prompt и raw
completion не сохраняются как evidence; сохраняются только model ID, usage, latency, finish reason
и content hash. Framework telemetry не получает секрет, но стандартный package User-Agent остаётся.

## Alternatives

- MAF `OpenAIChatClient` — отклонён: GateLLM не заявляет Responses API.
- Полный `agent-framework` — отклонён: добавляет неиспользуемые providers/integrations.
- Provider SDK models как domain artifacts — отклонено из-за coupling и обхода v1 validators.
- Всегда hard-code одной дешёвой модели — отклонено: catalog и цены меняются.
- Неограниченный generic exception retry — отклонён из-за лишней стоимости и сокрытия auth/schema
  ошибок.

## Consequences and validation

MAF adapter остаётся заменяемым, а offline suite не расходует токены. SDK compatibility проверяется
import/signature probe и fake-client agent workflow до live call. Если конкретная дешёвая модель не
поддерживает native schema mode, adapter принимает только JSON, который проходит наш строгий
Pydantic contract; capability failure фиксируется отдельно и не ослабляет schema.

Источники: MAF [PyPI package](https://pypi.org/project/agent-framework/), official
[core package guide](https://github.com/microsoft/agent-framework/blob/main/python/packages/core/AGENTS.md)
и `research-agent` [LLM client](https://github.com/ivanshamaev/research-agent/blob/main/agent/llm_client.py).
