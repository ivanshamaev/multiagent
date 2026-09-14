# ADR-0029 — Code-owned stage routing and durable role receipts

Status: accepted

Date: 2026-09-14

## Context

Линейный STEP-0019 принимает только successful stages. Реальный reducer также имеет terminal
`BLOCKED`/`FAILED` и bounded `REWORK`. Кроме того, MAF сохраняет checkpoint после superstep: процесс
может погибнуть после завершённого write-capable handler, но до фиксации его outgoing message.

## Decision

Маршрутизировать canonical JSON только именованными code-owned predicates, которые сначала
полностью декодируют snapshot и затем сравнивают `Stage`. Terminal состояния получает отдельный
output executor; `REWORK` возвращается только в DE. Reducer остаётся единственным владельцем
разрешённых переходов и rework budget, а MAF `max_iterations` служит вторым hard stop.

Перед вызовом роли вычисляется deterministic operation ID из workflow ID, executor ID, входной
revision и SHA-256 входного JSON. После успешной boundary validation executor атомарно сохраняет
canonical output в owner-only create-only receipt store и лишь затем отправляет MAF message. При
повторном входе тот же executor загружает receipt и не вызывает handler.

Receipt закрывает crash window **после возврата handler**. Side effect, оборванный до записи
receipt, должен принимать тот же operation ID либо иметь собственную reconciliation семантику;
универсальное exactly-once поверх неидемпотентного внешнего API невозможно.

## Alternatives

- Routing из model prose: отклонён как control-plane bypass.
- Бесконечный graph loop: отклонён; reducer budget и MAF iteration cap обязательны.
- Записать receipt до side effect: отклонено, потому что crash оставил бы ложный success.
- Полагаться только на MAF checkpoint: отклонено из-за post-handler/pre-checkpoint окна.

## Consequences and validation

Повтор после receipt является deterministic cache hit; collision или несовпадающий input/output
отклоняется. Artifact history увеличивает checkpoint, поэтому сохраняется bounded payload limit.
Branch, exhaustion, adversarial storage и SIGKILL/new-process recovery проверяются автоматически.
