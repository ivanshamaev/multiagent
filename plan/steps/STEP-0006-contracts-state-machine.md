# STEP-0006 — Typed contracts и deterministic state machine

Status: completed
Owner: primary agent
Updated: 2026-09-06
Current step: gate закрыт; следующий active step — STEP-0007

## Goal

Реализовать Phase C: строгие Pydantic-контракты артефактов и детерминированный workflow core,
который принимает переходы только по проверенным gates/evidence, ограничивает rework и сохраняет
append-only events. Компонент не делает LLM calls и не исполняет platform tools.

## Non-goals and affected paths

На этом шаге нет Microsoft Agent Framework adapter, GateLLM client, prompts, MCP, agent roles,
checkpoint database или Net Revenue implementation. Разрешены `contracts/`, `orchestrator/`,
подходящие `runtime/`, `tests/{unit,workflow,policy,adversarial}`, dependency locks, Make/docs и
`plan/**`. Scenario fixture, hidden oracle и golden Data Platform неизменяемы.

## Acceptance criteria

- [x] Versioned models существуют для TaskRequest, TaskSpecification, AnalysisReport,
  ImplementationResult, QAReport, ReviewReport и Evidence.
- [x] Contracts запрещают extra fields, пустые IDs, naive timestamps, неизвестные statuses и
  evidence без command/query source, exit code и artifact reference.
- [x] Code-owned state machine задаёт допустимые stages/transitions, terminal
  `DONE/BLOCKED/FAILED` и bounded `REWORK`; role output не может перескочить gate.
- [x] Retry/rework/tool/time/token budgets изменяются только deterministic кодом и не уходят ниже 0.
- [x] Автор implementation не может approve себя; QA/reviewer failures требуют evidence.
- [x] Append-only events имеют sequence, correlation IDs и проверяемый previous-event hash.
- [x] Unit/workflow/adversarial tests покрывают happy path, каждый illegal transition, missing
  evidence, self-approval, replay/tampering и exhaustion.
- [x] `make check` и scenario/platform regression gates остаются зелёными.

## Risks and decisions required

Нужно проверить актуальный Pydantic v2 API и Microsoft Agent Framework contract boundary по
официальной документации, но MAF dependency пока не добавлять. До кода принять ADR о разделении
domain contracts, workflow state и serialized event envelope. Нельзя использовать LLM output как
источник transition truth или связывать domain models с provider SDK.

## Implementation steps

1. Инвентаризировать artifact/status definitions в `init/` и убрать противоречия.
2. Зафиксировать ADR, schema versioning, UTC/time/ID policy и error taxonomy.
3. Добавить pinned Pydantic dependency через `uv`, реализовать contracts и serialization tests.
4. Реализовать pure transition reducer, budgets и event hash chain.
5. Добавить workflow/property-like/adversarial matrix без внешних сервисов.
6. Прогнать regression gates, записать evidence и только затем открыть local runtime step.

## Planned verification

`make check`, targeted contract/workflow tests, JSON round-trip fixtures, transition matrix,
tamper/replay/self-approval adversarial tests, `make scenario-repro-test`, `make platform-test` и
`git diff --check`.

## Work log

- 2026-09-05: проверены официальные Pydantic 2.13.5 и MAF workflow state/samples; MAF dependency
  отложена до adapter phase.
- 2026-09-05: принят ADR-0014 — strict frozen contracts, pure reducer, deterministic budgets и
  canonical hash chain.
- 2026-09-06: закрыты все artifact gates и ветви transition table; rework exhaustion завершается
  `FAILED`, не превышая budget.
- 2026-09-06: `make check` — exit `0`, 101 tests; scenario reproducibility/isolated grader — PASS.
- 2026-09-06: `make platform-test` — exit `0`; Airflow/Cosmos 11/11, dbt 68/68 и SQL PASS.

Persistent evidence: [`../evidence/STEP-0006-contracts-state-machine.md`](../evidence/STEP-0006-contracts-state-machine.md).
