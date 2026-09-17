# TODO — Лекция 07. Agent-orchestrator: planning, delegation и replanning

Status: reviewed; publication gate complete

Updated: 2026-09-17

Текст: `course/lectures/LECTURE-0007-agent-orchestrator.md`.

Track: core; исходная тема init: 16.

## Цель и уникальная область

Объяснить model-directed delegation; task/progress ledger; planner/executor separation: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [06](LECTURE-0006-strict-workflow.md).

## Что писать — todo

- [x] Разобрать manager → bounded worker → synthesis → replanning и критерии достаточности результата.
- [x] Объяснить task/progress ledgers, рабочую очередь, scope worker и завершение dynamic subtask.
- [x] Развести dynamic routing, workers-as-tools, hierarchical teams и A2A transport.
- [x] Сопоставить план модели с code-owned permission/approval shell; обозначить отсутствие реализации у нас.
- [x] Показать research/schema investigation как мысленный пример, не как выполненный pipeline.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [09](LECTURE-0009-mcp-interface.md), [06](LECTURE-0006-strict-workflow.md), [19](LECTURE-0019-security-authority.md), [24](LECTURE-0024-orchestration-comparison.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

External architecture only; ours remains code-owned workflow; ADR-0035.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [x] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Magentic-One: A Generalist Multi-Agent System for Solving Complex Tasks](https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/) (Microsoft Research, S24). Идея для этого ракурса: Task/progress ledgers и replanning.
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (Anthropic, S02). Идея для этого ракурса: Делегирование исследовательских subtasks с явными boundaries.

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
