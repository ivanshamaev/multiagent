# TODO — Лекция 23. Cost/performance: budgets, critical path и эффективность

Status: lecture written; text-only reviewed

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0023-cost-performance.md`.

Track: core; исходная тема init: 23.

## Цель и уникальная область

Объяснить budget allocation; critical-path cost trade-off; tool context overhead: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [21](LECTURE-0021-evaluation.md), [07](LECTURE-0007-agent-orchestrator.md).

## Что писать — todo

- [x] Дать модель total cost с retries/manager/synthesis/tool output, не только price per token.
- [x] Разобрать parallel read benefits vs synchronization/write conflict и rate constraints.
- [x] Объяснить cost-first capability gate и контроль качества при уменьшении бюджета.
- [x] Показать dated GateLLM accounting; не обещать актуальные цены, caching или model router, которых нет.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [03](LECTURE-0003-harness-context.md), [07](LECTURE-0007-agent-orchestrator.md), [21](LECTURE-0021-evaluation.md), [24](LECTURE-0024-orchestration-comparison.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/model_provider.py; STEP-0009 sample; EXP-0001.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [x] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Code execution with MCP: Building more efficient agents](https://www.anthropic.com/engineering/code-execution-with-mcp) (Anthropic, S26). Идея для этого ракурса: Tool definitions/results как расход контекста.
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (Anthropic, S02). Идея для этого ракурса: Экономическая граница multi-agent research.

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
