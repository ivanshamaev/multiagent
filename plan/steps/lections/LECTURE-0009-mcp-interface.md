# TODO — Лекция 09. MCP как интерфейс, а не политика координации

Status: reviewed; publication gate complete

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0009-mcp-interface.md`.

Track: core; исходная тема init: 06.

## Цель и уникальная область

Объяснить MCP host/client/server; protocol capability negotiation; tool interface ergonomics: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [08](LECTURE-0008-isolation.md), [03](LECTURE-0003-harness-context.md).

## Что писать — todo

- [x] Объяснить роли host/client/server, transport и negotiated capabilities.
- [x] Развести tool call, agent delegation и workflow transition.
- [x] Описать tool names/parameters/results как semantic interface, не произвольный API pass-through.
- [x] Разграничить protocol guarantees и repository-owned authorization; OAuth details сверять отдельно.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [10](LECTURE-0010-analytical-sql.md), [11](LECTURE-0011-dbt-semantics.md), [18](LECTURE-0018-airflow-operations.md), [19](LECTURE-0019-security-authority.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/tools/mcp_gateway.py; runtime/tools/mcp_stdio.py; STEP-0008.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [x] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) (Anthropic, S11). Идея для этого ракурса: Унифицированный интерфейс подключения данных.
- [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (Anthropic, S08). Идея для этого ракурса: Tool ergonomics и понятные boundaries.

- [x] Перед авторством перечитать выбранные разделы и спецификацию 2026-07-28; точные claims/API details проверить по первичным источникам.
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
