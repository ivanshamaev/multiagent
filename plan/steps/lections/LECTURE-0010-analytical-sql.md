# TODO — Лекция 10. Аналитический SQL и ограниченные data capabilities

Status: reviewed; publication gate complete

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0010-analytical-sql.md`.

Track: core; исходная тема init: 07.

## Цель и уникальная область

Объяснить analytical query scope; SQL resource envelope; read capability composition: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [09](LECTURE-0009-mcp-interface.md).

## Что писать — todo

- [x] Объяснить metadata/profile/aggregate access и минимально достаточный SQL surface.
- [x] Развести SELECT syntax, фактические side effects и использование функций/таблиц вне scope.
- [x] Показать AST/policy query checks, row/time/output bounds и read-only database identity.
- [x] Кратко связать materialization с видом наблюдаемых данных, не преподавать dbt или query tuning заново.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [11](LECTURE-0011-dbt-semantics.md), [12](LECTURE-0012-analyst-provenance.md), [19](LECTURE-0019-security-authority.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

policies/tool_policy.py; platform/clickhouse/security/; STEP-0008.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [x] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (Anthropic, S08). Идея для этого ракурса: Специализированный tool вместо чрезмерно общего интерфейса.
- [Using Materialized Views in ClickHouse](https://clickhouse.com/blog/using-materialized-views-in-clickhouse) (ClickHouse, S16). Идея для этого ракурса: Materialized analytical result как контекст наблюдения.

- [x] Перед авторством перечитать выбранные разделы; точные claims/API details проверить по первичным источникам.
- [x] Переиспользовать концепции своими словами с attribution; не копировать текст, полный перевод или чужую схему.
- [x] Различить утверждение статьи, наш пример и авторское обобщение; source caveats — в [SOURCES](SOURCES.md).

## Авторство, редактура и фактчекинг — обязательные todo

- [x] Соблюсти [технические требования](../../../course/technical-requirements.md): Markdown и Mermaid с подписью, accTitle/accDescr и текстовым эквивалентом.
- [x] При готовом сборщике проверить SVG/HTML визуально: стрелки, кириллицу, mobile/desktop, no-JS и доступность; не отмечать render PASS до фактической проверки.
- [x] В review учесть diagram config/toolchain/assets; не повторять UI-код zoom/pan/fullscreen в тексте лекции.

- [x] Применить `technical-markdown-lectures` с deep-theory depth; созданные editorial skills прочитать перед review и записать версии/usage.
- [x] После написания выполнить полную вычитку: язык, терминология, структура, повторы внутри лекции и по соседним темам.
- [x] Отдельно перепроверить существенные claims, числа/даты/версии, соответствие схем тексту и code/evidence.
- [x] Исправить findings и повторно проверить затронутый текст; существенная переработка требует полной вычитки.
- [x] Сохранить per-lecture review record с content hash и source anchors; missing/stale review запрещает reviewed.
- [x] Перед публикацией сверить topic ownership/cross-links и отсутствие unresolved существенных замечаний.
