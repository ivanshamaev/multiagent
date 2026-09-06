# STEP-0007 — GateLLM и controlled local agent runtime

Status: completed
Owner: primary agent
Updated: 2026-09-06
Current step: завершён; evidence — `plan/evidence/STEP-0007-local-agent-runtime.md`

## Goal

Реализовать минимальный Phase D vertical slice: один локальный controlled agent через Microsoft
Agent Framework и GateLLM получает bounded context, возвращает строго валидируемый artifact и
передаёт его существующему deterministic workflow. Offline tests не расходуют LLM tokens; live
smoke является отдельным минимальным gate.

## Non-goals and affected paths

На шаге нет dbt/ClickHouse MCP, автономной реализации Net Revenue, multi-agent team, memory,
checkpoint database, A2A, production credentials или container isolation runtime. Разрешены
`runtime/`, один synthetic role в `agents/`, adapter-level `orchestrator/`, tests, dependencies,
Make/config/docs и `plan/**`. Golden platform, scenario oracle и transition policy не меняются.

## Acceptance criteria

- [x] Pinned MAF/OpenAI dependencies выбраны по актуальным official APIs и совместимы с Python 3.12.
- [x] GateLLM settings читают только `API_TOKEN`; base URL/model/timeouts/budgets валидируются,
  token не появляется в repr, logs, exceptions, serialized events или Docker config.
- [x] Provider имеет единый internal request/usage/result contract, bounded timeout/retries и
  fake transport; cheapest capable CHAT model выбирается конфигурацией/catalog snapshot, не
  вечным hard-code.
- [x] Structured output проходит обычную Pydantic validation; malformed/extra/unknown payload
  не может создать artifact или workflow transition.
- [x] MAF code workflow остаётся adapter layer над pure reducer и не владеет transition policy.
- [x] Context builder передаёт только allowlisted files/metadata с size limits; защищённые пути и
  symlinks fail closed.
- [x] Controlled synthetic run работает только в disposable scenario workspace и формирует
  append-only events, usage/latency/model metadata без prompt/secret leakage.
- [x] Unit/integration/policy/adversarial tests покрывают fake success, malformed output,
  timeout/rate-limit retry, exhausted budgets, path escape и protected edit.
- [x] Opt-in GateLLM smoke использует минимальные output tokens и cheapest verified model; затем
  `make check`, scenario и platform regressions остаются зелёными.

## Risks and decisions required

MAF pre-release API и способ подключения custom OpenAI-compatible endpoint могли измениться;
сначала нужны official docs/source и pinned compatibility probe. GateLLM catalog/pricing изменяемы,
поэтому выбор модели должен иметь датированный snapshot и override. Повтор POST после timeout может
дублировать billable completion: retries разрешены только для классифицированных transient ошибок
и ограничены кодом. Agent output, prompt и provider error считаются недоверенными данными.

До runtime-кода принять ADR: границы `ModelProvider`/MAF/domain reducer, ownership usage accounting,
retry policy и правила redaction. Если текущий MAF не позволяет чистый custom endpoint adapter,
зафиксировать problem record и использовать тонкий OpenAI SDK provider без подмены domain workflow.

## Implementation steps

1. Проверить official MAF Python samples/API, PyPI versions и `research-agent` GateLLM pattern.
2. Принять ADR и добавить pinned dependencies через `uv`; выполнить import/compatibility probe.
3. Реализовать redacted settings, typed provider contracts, fake transport и GateLLM adapter.
4. Реализовать bounded context/workspace guards и synthetic structured-output role.
5. Связать MAF executor edges с существующими artifacts/reducer/events без policy duplication.
6. Добавить offline failure/adversarial matrix; live smoke запускать только после всех guards.
7. Выполнить полные regression gates, записать model/cost evidence и остаточные риски.

## Planned verification

`make check`; targeted runtime/provider/workflow tests; secret scan resolved config/log fixtures;
one opt-in GateLLM structured smoke; protected-path and malformed-output adversarial tests;
`make scenario-repro-test`; `make platform-test`; `git diff --check`.

## Work log

- 2026-09-06: STEP-0006 gate закрыт до начала runtime-кода; Phase D разделён на минимальный
  single-agent vertical slice без platform tools и multi-agent orchestration.
- 2026-09-06: official package/source подтвердили MAF 1.17.0 и отдельный Chat Completions client;
  принят ADR-0015 для selective dependencies, GateLLM provider и deterministic reducer boundary.
- 2026-09-06: compatibility probe выявил новый `httpx2` import в OpenAI 3 stack; исправление и
  regression scope записаны в PRB-0013.
- 2026-09-06: functional workflow probe прошёл, но API помечен experimental; production slice
  переведён на graph `Executor`/`WorkflowBuilder` без изменения domain reducer.
- 2026-09-06: live typed catalog выявил `~`-prefixed virtual IDs; узкое schema extension и
  regression fixture записаны в PRB-0014.
- 2026-09-06: catalog-cheapest Ling 2.6 Flash вернул 404 и без MAF schema mode; cost-ordered
  one-token gate выбрал первый routable `mistralai/mistral-nemo` (PRB-0015).
- 2026-09-06: два повторных Mistral full calls дали 504; text probe заменён строгим schema probe.
  Ling 3.0 не прошла probe, Granite Micro вернул schema-invalid artifact, оба fail closed. Измеренный
  Llama 3.1 8B run прошёл provider, Pydantic contract и reducer (PRB-0016, EXP-0001).
- 2026-09-06: `make check` — 129 tests; scenario fingerprints и isolated baseline grader
  воспроизведены; Airflow/Cosmos 11/11, dbt 68/68 и independent SQL прошли. Шаг закрыт.
