# 09 — Airflow API: наблюдение и контролируемые операции

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0009-airflow-operations.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[6](../../modules/module-06-mcp-interface/README.md), [18](../../modules/module-18-recovery-idempotency/README.md)

## Теоретические outcomes

- Объяснить data orchestration boundary, предпосылки и ограничения.
- Объяснить operation approval binding, предпосылки и ограничения.
- Объяснить observer/trigger separation, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `data orchestration boundary`, `operation approval binding`, `observer/trigger separation`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Развести data-task scheduling и orchestration reasoning агентов.
- Объяснить stable REST /api/v2 vs Task Execution API без смешения двух интерфейсов.
- Показать observer GET scope и separate approved dev-DAG trigger identity.
- Применить понятие operation identity из 18; не переобъяснять idempotency protocol и общий threat model.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/airflow_mcp_server.py; runtime/airflow_trigger_mcp_server.py; STEP-0014/0015

- [runtime/airflow_mcp_server.py](../../../runtime/airflow_mcp_server.py)
- [runtime/airflow_trigger_mcp_server.py](../../../runtime/airflow_trigger_mcp_server.py)
- [plan/evidence/STEP-0014-read-only-airflow-mcp.md](../../../plan/evidence/STEP-0014-read-only-airflow-mcp.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Apache Airflow 3 is Generally Available!](https://airflow.apache.org/blog/airflow-three-point-oh-is-here/) — API-first разделение исполнения data tasks.
- [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) — Operation identity применительно к repeated trigger.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0009-airflow-operations.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
