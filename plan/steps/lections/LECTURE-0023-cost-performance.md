# TODO — Лекция 23. Cost/performance: budgets, critical path и эффективность

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0023-cost-performance.md` (ещё не написан).

Track: core; исходная тема init: 23.

## Цель и уникальная область

Объяснить budget allocation; critical-path cost trade-off; tool context overhead: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [21](LECTURE-0021-evaluation.md), [16](LECTURE-0016-agent-orchestrator.md).

## Что писать — todo

- [ ] Дать модель total cost с retries/manager/synthesis/tool output, не только price per token.
- [ ] Разобрать parallel read benefits vs synchronization/write conflict и rate constraints.
- [ ] Объяснить cost-first capability gate и контроль качества при уменьшении бюджета.
- [ ] Показать dated GateLLM accounting; не обещать актуальные цены, caching или model router, которых нет.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [04](LECTURE-0004-harness-context.md), [16](LECTURE-0016-agent-orchestrator.md), [21](LECTURE-0021-evaluation.md), [26](LECTURE-0026-orchestration-comparison.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/model_provider.py; STEP-0009 sample; EXP-0001.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Code execution with MCP: Building more efficient agents](https://www.anthropic.com/engineering/code-execution-with-mcp) (Anthropic, S26). Идея для этого ракурса: Tool definitions/results как расход контекста.
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (Anthropic, S02). Идея для этого ракурса: Экономическая граница multi-agent research.

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
