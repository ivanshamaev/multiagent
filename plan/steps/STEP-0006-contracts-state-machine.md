# STEP-0006 — Typed contracts и deterministic state machine

Status: active
Owner: primary agent
Updated: 2026-09-05
Current step: определить versioned contract schemas и transition invariants

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

- [ ] Versioned models существуют для TaskRequest, TaskSpecification, AnalysisReport,
  ImplementationResult, QAReport, ReviewReport и Evidence.
- [ ] Contracts запрещают extra fields, пустые IDs, naive timestamps, неизвестные statuses и
  evidence без command/query source, exit code и artifact reference.
- [ ] Code-owned state machine задаёт допустимые stages/transitions и terminal
  `DONE/REWORK/BLOCKED/FAILED`; role output не может перескочить gate.
- [ ] Retry/rework/tool/time/token budgets уменьшаются только deterministic кодом и не уходят ниже 0.
- [ ] Автор implementation не может approve себя; QA/reviewer failures требуют evidence.
- [ ] Append-only events имеют sequence, correlation IDs и проверяемый previous-event hash.
- [ ] Unit/workflow/adversarial tests покрывают happy path, каждый illegal transition, missing
  evidence, self-approval, replay/tampering и exhaustion.
- [ ] `make check` и scenario/platform regression gates остаются зелёными.

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
