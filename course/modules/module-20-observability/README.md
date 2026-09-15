# 20 — Observability: trace causality и границы наблюдения

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0020-observability.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[15](../../modules/module-15-strict-workflow/README.md), [16](../../modules/module-16-agent-orchestrator/README.md), [18](../../modules/module-18-recovery-idempotency/README.md)

## Теоретические outcomes

- Объяснить trace context propagation, предпосылки и ограничения.
- Объяснить telemetry cardinality, предпосылки и ограничения.
- Объяснить sampling/retention design, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `trace context propagation`, `telemetry cardinality`, `sampling/retention design`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Развести event log, trace, metric и artifact provenance; не путать trace с private model reasoning.
- Объяснить workflow/role/model/tool/artifact span hierarchy и carrier across restart.
- Разобрать sampling, cardinality, retention и потерю observability signal.
- Показать content-free Collector/Tempo/Prometheus/Grafana; методику оценивания оставить 21.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/telemetry.py; observability/; STEP-0021/0023

- [runtime/telemetry.py](../../../runtime/telemetry.py)
- [plan/evidence/STEP-0021-opentelemetry-trace-chain.md](../../../plan/evidence/STEP-0021-opentelemetry-trace-chain.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Dapper, a Large-Scale Distributed Systems Tracing Infrastructure](https://research.google/pubs/dapper-a-large-scale-distributed-systems-tracing-infrastructure/) — Trace context и sampling в распределённой системе.
- [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) — Session/harness/sandbox boundaries как observation boundaries.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0020-observability.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
