# TODO — Лекция 00. Агентная система: agency, reasoning и среда

Status: authored and reviewed; local publication gate checked in STEP-0030

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0000-agentic-baseline.md`.

Track: core; исходная тема init: 00.

## Цель и уникальная область

Объяснить agency; agent loop; reasoning/action/observation: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: нет; начальная лекция курса.

## Что писать — todo

- [x] Развести LLM-вызов, tool-using agent и multi-agent system, не определяя топологии управления.
- [x] Показать observation как внешний сигнал; отделить план/объяснение от фактического outcome.
- [x] Объяснить ограниченную рациональность и критерии остановки одного agent loop.
- [x] Использовать минимальную схему модели и среды; не публиковать private reasoning.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [01](LECTURE-0001-organization.md), [15](LECTURE-0015-strict-workflow.md), [16](LECTURE-0016-agent-orchestrator.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/agent_runtime.py; STEP-0007.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [x] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) (Yao et al., original research paper, S23). Идея для этого ракурса: Связь действия с наблюдением, без копирования reasoning traces.
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Anthropic, S01). Идея для этого ракурса: Уровень автономии, без обзора всех workflow patterns.

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

## Результат STEP-0029 и оставшийся gate

Текст, подписи и заключение полностью вычитаны автором в отдельных проходах.
ReAct §2 и релевантные определения Anthropic перечитаны 2026-09-15;
PM behavior сопоставлен с кодом и workflow/adversarial tests.
Проверены render и sanitizer, browser preview диаграммы desktop/mobile/dark/no-JS.
Это не полная проверка опубликованной лекции: screen reader и final reader URLs
не проверялись. Поэтому broad visual/publication checkbox выше остаётся открытым.
Receipt и hashes: `course/reviews/LECTURE-0000.json`; независимого reviewer нет.

STEP-0030 дополняет прежний результат: полный reader candidate проверен реально,
включая keyboard/zoom/pan/reset/fullscreen/Escape, print clipping, AX names/descriptions,
mobile/no-JS и loopback `/course/`/CSP/links. Publication receipt отделён от content review.
Screen-reader разметка проверена через AX tree; реальное AT interaction не выполнялось
и остаётся явно записанным interoperability risk по ADR-0039. Прежние открытые
publication checkboxes закрыты только для этой указанной области проверки.
