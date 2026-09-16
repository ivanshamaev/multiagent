# TODO — Лекция 11. dbt, lineage и семантика аналитической модели

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0011-dbt-semantics.md` (ещё не написан).

Track: core; исходная тема init: 08.

## Цель и уникальная область

Объяснить model grain; transformation lineage; dbt validation stages: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [10](LECTURE-0010-analytical-sql.md).

## Что писать — todo

- [ ] Определить grain и зависимость staging/intermediate/marts без курса общего SQL.
- [ ] Разобрать lineage и parse/compile/build/test: разные kinds of evidence.
- [ ] Развести warehouse model graph, Airflow DAG и multi-agent control graph.
- [ ] Показать Cosmos как интеграцию dbt в data orchestration, не писать инструкции развёртывания.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [18](LECTURE-0018-airflow-operations.md), [12](LECTURE-0012-analyst-provenance.md), [14](LECTURE-0014-data-engineer.md), [15](LECTURE-0015-qa-evidence.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

platform/dbt/; platform/airflow/dags/cosmos_pipeline.py; STEP-0004.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [What is analytics engineering?](https://www.getdbt.com/blog/what-is-analytics-engineering) (dbt Labs, S17). Идея для этого ракурса: Analytics transformation как инженерная ответственность.
- [Why data testing is essential for analytics engineering](https://www.getdbt.com/blog/data-testing) (dbt Labs, S18). Идея для этого ракурса: Data assertions в transformation lifecycle.

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
