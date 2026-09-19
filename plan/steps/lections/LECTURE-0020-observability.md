# TODO — Лекция 20. Observability: trace causality и границы наблюдения

Status: lecture written; text-only reviewed

Updated: 2026-09-19

Текст: `course/lectures/LECTURE-0020-observability.md`.

Track: core; исходная тема init: 20.

## Цель и уникальная область

Объяснить trace context propagation; telemetry cardinality; sampling/retention design: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [06](LECTURE-0006-strict-workflow.md), [07](LECTURE-0007-agent-orchestrator.md), [17](LECTURE-0017-recovery-idempotency.md).

## Что писать — todo

- [x] Развести event log, trace, metric и artifact provenance; не путать trace с private model reasoning.
- [x] Объяснить workflow/role/model/tool/artifact span hierarchy и carrier across restart.
- [x] Разобрать sampling, cardinality, retention и потерю observability signal.
- [x] Показать content-free Collector/Tempo/Prometheus/Grafana; методику оценивания оставить 21.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [17](LECTURE-0017-recovery-idempotency.md), [21](LECTURE-0021-evaluation.md), [22](LECTURE-0022-failure-taxonomy.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/telemetry.py; observability/; STEP-0021/0023.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [x] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Dapper, a Large-Scale Distributed Systems Tracing Infrastructure](https://research.google/pubs/dapper-a-large-scale-distributed-systems-tracing-infrastructure/) (Google Research, original research paper, S29). Идея для этого ракурса: Trace context и sampling в распределённой системе.
- [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) (Anthropic, S27). Идея для этого ракурса: Session/harness/sandbox boundaries как observation boundaries.

- [x] Перед авторством перечитать выбранные разделы; точные claims/API details проверить по первичным источникам.
- [x] Переиспользовать концепции своими словами с attribution; не копировать текст, полный перевод или чужую схему.
- [x] Различить утверждение статьи, наш пример и авторское обобщение; source caveats — в [SOURCES](SOURCES.md).

## Авторство, редактура и фактчекинг — обязательные todo

- [x] Соблюсти [технические требования](../../../course/technical-requirements.md): Markdown и Mermaid с подписью, accTitle/accDescr и текстовым эквивалентом.
- [x] Проверить текстовую семантику Mermaid source, подписи и текстового эквивалента; не делать скриншоты и визуальную вычитку SVG/HTML.
- [x] Сохранить text-only review и static-build fingerprints; не проставлять visual/AX/browser PASS и не повторять UI-код zoom/pan/fullscreen в лекции.

- [x] Применить `technical-markdown-lectures` с deep-theory depth; созданные editorial skills прочитать перед review и записать версии/usage.
- [x] После написания выполнить полную вычитку: язык, терминология, структура, повторы внутри лекции и по соседним темам.
- [x] Отдельно перепроверить существенные claims, числа/даты/версии, соответствие схем тексту и code/evidence.
- [x] Исправить findings и повторно проверить затронутый текст; существенная переработка требует полной вычитки.
- [x] Сохранить per-lecture review record с content hash и source anchors; missing/stale review запрещает reviewed.
- [x] Перед публикацией сверить topic ownership/cross-links и отсутствие unresolved существенных замечаний.
