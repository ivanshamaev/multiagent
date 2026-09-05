# ADR-0014 — Domain contracts, pure reducer и hash-chained events

Status: accepted

Date: 2026-09-05

## Context

Workflow должен принимать недоверенные structured outputs от будущих агентов, но provider SDK и
Microsoft Agent Framework меняются независимо от предметной модели. Mutable dictionaries,
неявное coercion и model-driven transitions не дают доказать gates, authorship и budgets. Для
audit также нужна проверяемая последовательность событий, а не только последний state.

## Decision

Используем pinned `pydantic==2.13.5`. Все внешние domain contracts имеют literal
`schema_version`, discriminator `artifact_type`, `extra="forbid"`, frozen model config,
ограниченные ID/строки и UTC-aware timestamps. Валидация проходит только через обычный
constructor/`model_validate`/`model_validate_json`; `model_construct` на trust boundary запрещён.
Evidence всегда содержит source, invocation, exit code и content-addressed artifact reference.

`orchestrator` не зависит от MAF. Pure reducer принимает текущий immutable `WorkflowState` и
code-created `TransitionCommand`, проверяет exact transition table, artifact type/decision,
task/author identity и budget charge, затем возвращает новый state. Rework расходуется при входе
в `REWORK`; при исчерпании лимита workflow детерминированно переходит в `FAILED`. Tool/token/time
charges сверх лимита отклоняются без отрицательного остатка.

Каждый принятый переход добавляет immutable `WorkflowEvent`: sequence, workflow/task/correlation
IDs, before/after stage, artifact, charge, previous hash и SHA-256 canonical JSON текущего event.
Chain validation обнаруживает reorder, replay, deletion и mutation. Это integrity checksum, не
криптографическая подпись; durable authenticated storage появится в reliability phase.

MAF adapter в Phase D будет переводить typed executor messages в эти contracts и вызывать reducer.
MAF workflow state не становится источником transition policy.

## Alternatives

- Provider/MAF message classes как domain contracts — отклонено из-за coupling и неявной history.
- Mutable state machine с методами на agents — отклонено: роль могла бы пропустить gate.
- Один untyped event payload — отклонено: replay и schema evolution становятся неоднозначными.
- HMAC сейчас — отложено до появления managed signing key и durable store.

## Consequences and validation

Schema evolution требует нового literal version/adapter, а не молчаливого изменения v1. Tests
проверяют JSON round-trip, extra/naive timestamp/path rejection, полный transition matrix,
self-approval, evidence linkage, budget exhaustion и event tampering.

Источники: Pydantic [models](https://docs.pydantic.dev/latest/concepts/models/) и
[validators](https://docs.pydantic.dev/latest/concepts/validators/); Microsoft Agent Framework
[workflow state](https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/state) и
[Python workflow samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows).
