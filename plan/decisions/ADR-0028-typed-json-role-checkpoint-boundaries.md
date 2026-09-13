# ADR-0028 — Typed JSON boundaries between checkpointable role executors

Status: accepted

Date: 2026-09-13

## Context

Существующие Analyst, PM, Data Engineer, QA и Reviewer workflows объединяют работу каждой роли
в крупный executor. MAF поэтому не может сохранить прогресс между бизнес-ролями. Прямая запись
Pydantic-объектов в checkpoint также потребовала бы расширить allowlist декодера прикладными
типами и увеличила бы поверхность доверия.

## Decision

Собрать стабильный MAF graph из шести executors. Между ними передаётся только канонический JSON
одного strict `RolePipelineSnapshot`; каждый executor заново валидирует snapshot, event hash chain,
workflow/task identity, ожидаемую входную и выходную стадии. Фактическая реализация роли подаётся
как типизированный async stage handler, поэтому существующие autonomous workflows можно подключать
адаптерами, а recovery проверять детерминированными handlers без LLM-затрат.

`Validator` является самостоятельным executor, а не скрытым шагом Data Engineer. Успешный путь
оканчивается только после независимых QA и Reviewer gates. Branching rework будет отдельным решением.

## Alternatives

- Один orchestration executor: отклонён, потому что checkpoint не видит бизнес-границы.
- Передавать Pydantic instances напрямую: отклонено из-за расширения checkpoint decoder allowlist.
- Сразу реализовать все циклы rework: отложено, чтобы сначала доказать линейное восстановление и
  не смешивать recovery semantics с routing policy.

## Consequences and validation

Checkpoint после каждого superstep становится завершённой role boundary; новый процесс может не
повторять предыдущие роли. JSON добавляет сериализацию, но делает payload переносимым и проверяемым.
Оборванная текущая роль всё ещё обязана быть idempotent. Topology, hostile snapshots и SIGKILL/new
process resume проверяются автоматически.
