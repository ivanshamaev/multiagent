# TODO — Лекция 06. Жёсткий workflow: reducer, branching и convergence

Status: reviewed; publication gate complete

Updated: 2026-09-17

Текст: `course/lectures/LECTURE-0006-strict-workflow.md`.

Track: core; исходная тема init: 15.

## Цель и уникальная область

Объяснить code-owned transition policy; terminal convergence; bounded rework routing: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [05](LECTURE-0005-maf-executors.md).

## Что писать — todo

- [x] Дать модель workflow transition relation и разделить safety/liveness.
- [x] Объяснить fixed graph с branching, parallel edges и bounded loops: жёсткий не значит только linear DAG.
- [x] Разобрать reducer-owned BLOCKED/FAILED/DONE, acceptance gates и rework invalidation.
- [x] Показать six-role code path; model reasoning внутри стадии не передаёт LLM право менять transitions.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [05](LECTURE-0005-maf-executors.md), [07](LECTURE-0007-agent-orchestrator.md), [17](LECTURE-0017-recovery-idempotency.md), [24](LECTURE-0024-orchestration-comparison.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/role_pipeline.py; orchestrator/transitions.py; STEP-0020.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Anthropic, S01). Идея для этого ракурса: Предопределённые пути управления.
- [LangGraph: Multi-Agent Workflows](https://www.langchain.com/blog/langgraph-multi-agent-workflows) (LangChain, S05). Идея для этого ракурса: Graph и возможные cycles как runtime model.

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
