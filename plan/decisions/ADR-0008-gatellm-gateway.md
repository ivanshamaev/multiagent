# ADR-0008 — GateLLM gateway и cost-first model policy

Status: accepted  
Date: 2026-09-04

## Context

Проекту нужен единый LLM interface, модельная независимость и контролируемая стоимость. Пользователь предоставил OpenAI-совместимый GateLLM gateway и `API_TOKEN` в локальном `.env`. Референс `ivanshamaev/research-agent` использует provider factory, custom `base_url`, bounded retries и normalized response.

## Decision

Все LLM-запросы выполняются через `https://gatellm.ru/v1`; секрет читается только из `API_TOKEN`. Внутренний provider abstraction не зависит от конкретной модели. `/v1/models` используется для versioned pricing snapshot. Default model — самый дешёвый CHAT-вариант, прошедший минимальные capability tests; на 2026-09-04 это `inclusionai/ling-2.6-flash` (262,144 context; 3 ₽ input и 9 ₽ output за 1M tokens по ответу gateway).

Unit tests не выполняют live calls. Live smoke/evals opt-in и обязаны записывать model, usage, latency и cost. Role-specific upgrade допускается только после зафиксированного quality failure и сравнительного эксперимента.

## Alternatives

- Прямые provider API отклонены: усложняют secrets, accounting и замену модели.
- Одна дорогая модель для всех ролей отклонена: стоимость не обоснована до evals.
- Автоматический выбор исключительно по цене без capability gate отклонён: дешёвая модель может не поддерживать structured output/tool calls.

## Consequences and validation

Нужны fake HTTP transport, error mapping для 400/401/402/429/500, bounded retries только для retryable failures и cost evidence. Gate: settings не раскрывают token; mocked client использует правильный URL/Auth; cheapest model проходит tool/structured-output smoke перед agent tasks.

