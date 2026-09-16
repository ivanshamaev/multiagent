# TODO — Лекция 18. Airflow API: наблюдение и контролируемые операции

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0018-airflow-operations.md` (ещё не написан).

Track: core; исходная тема init: 09.

## Цель и уникальная область

Объяснить data orchestration boundary; operation approval binding; observer/trigger separation: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [09](LECTURE-0009-mcp-interface.md), [17](LECTURE-0017-recovery-idempotency.md).

## Что писать — todo

- [ ] Развести data-task scheduling и orchestration reasoning агентов.
- [ ] Объяснить stable REST /api/v2 vs Task Execution API без смешения двух интерфейсов.
- [ ] Показать observer GET scope и separate approved dev-DAG trigger identity.
- [ ] Применить понятие operation identity из 17; не переобъяснять idempotency protocol и общий threat model.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [06](LECTURE-0006-strict-workflow.md), [17](LECTURE-0017-recovery-idempotency.md), [19](LECTURE-0019-security-authority.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/airflow_mcp_server.py; runtime/airflow_trigger_mcp_server.py; STEP-0014/0015.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Apache Airflow 3 is Generally Available!](https://airflow.apache.org/blog/airflow-three-point-oh-is-here/) (Apache Airflow authors, S28). Идея для этого ракурса: API-first разделение исполнения data tasks.
- [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) (AWS Builders’ Library, S12). Идея для этого ракурса: Operation identity применительно к repeated trigger.

- [ ] Перед авторством перечитать выбранные разделы; точные claims/API details проверить по первичным источникам.
- [ ] Переиспользовать концепции своими словами с attribution; не копировать текст, полный перевод или чужую схему.
- [ ] Различить утверждение статьи, наш пример и авторское обобщение; source caveats — в [SOURCES](SOURCES.md).

## Авторство, редактура и фактчекинг — обязательные todo

- [ ] Соблюсти [технические требования](../../../course/technical-requirements.md): Markdown и Mermaid с подписью, accTitle/accDescr и текстовым эквивалентом.
- [ ] При готовом сборщике проверить SVG/HTML визуально: стрелки, кириллицу, mobile/desktop, no-JS и доступность; не отмечать render PASS до фактической проверки.
- [ ] В review учесть diagram config/toolchain/assets; не повторять UI-код zoom/pan/fullscreen в тексте лекции.

- [ ] Применить `technical-markdown-lectures` с deep-theory depth; созданные editorial skills прочитать перед review и записать версии/usage.
- [ ] После написания выполнить полную вычитку: язык, терминология, структура, повторы внутри лекции и по соседним темам.
- [ ] Отдельно перепроверить существенные claims, числа/даты/версии, соответствие схем тексту и code/evidence.
- [ ] Исправить findings и повторно проверить затронутый текст; существенная переработка требует полной вычитки.
- [ ] Сохранить per-lecture review record с content hash и source anchors; missing/stale review запрещает reviewed.
- [ ] Перед публикацией сверить topic ownership/cross-links и отсутствие unresolved существенных замечаний.
