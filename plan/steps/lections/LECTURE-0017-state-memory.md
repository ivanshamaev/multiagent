# TODO — Лекция 17. Context, durable state, artifacts и knowledge

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0017-state-memory.md` (ещё не написан).

Track: core; исходная тема init: 17.

## Цель и уникальная область

Объяснить state lifecycle; artifact visibility; durable vs ephemeral knowledge: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [04](LECTURE-0004-harness-context.md).

## Что писать — todo

- [ ] Разделить conversation context, workflow snapshot, task artifact и long-term knowledge.
- [ ] Объяснить lifetime/visibility/consistency и потерю информации при summarization.
- [ ] Сопоставить shared scratchpad с accepted artifact handoff без повторения schemas.
- [ ] Показать текущее context/state; long-term memory описать как альтернативу, не как установленный layer.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [03](LECTURE-0003-contracts.md), [04](LECTURE-0004-harness-context.md), [11](LECTURE-0011-analyst-provenance.md), [18](LECTURE-0018-recovery-idempotency.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/context.py; contracts/artifacts.py; STEP-0019.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Anthropic, S07). Идея для этого ракурса: Compaction/structured notes как способы работы с контекстом.
- [Don’t Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) (Cognition, S03). Идея для этого ракурса: Контекст и согласованность implicit decisions.

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
