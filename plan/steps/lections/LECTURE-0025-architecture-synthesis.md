# TODO — Лекция 25. Итоговый синтез: наш мультиагент как система

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0025-architecture-synthesis.md` (ещё не написан).

Track: core; исходная тема init: 25.

## Цель и уникальная область

Объяснить integrated architecture rationale; evidence-bounded system claims; cross-layer change impact: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [24](LECTURE-0024-orchestration-comparison.md), [22](LECTURE-0022-failure-taxonomy.md), [13](LECTURE-0013-pm-specification.md), [14](LECTURE-0014-data-engineer.md).

## Что писать — todo

- [ ] Собрать существующие concepts в четыре слоя и один Net Revenue architecture walkthrough.
- [ ] Проследить known facts → requirements → implementation → independent quality → terminal outcome.
- [ ] Отдельно показать доказанное offline/live, NEEDS_USER и оставшиеся integration gaps.
- [ ] Сформулировать последствия смены одного layer, не повторяя определения/сравнение из 24.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [13](LECTURE-0013-pm-specification.md), [06](LECTURE-0006-strict-workflow.md), [07](LECTURE-0007-agent-orchestrator.md), [21](LECTURE-0021-evaluation.md), [24](LECTURE-0024-orchestration-comparison.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

STEP-0010/0013/0020/0024; ADR/PRB/EXP anchors.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Multi-Agents: What’s Actually Working](https://cognition.com/blog/multi-agents-working) (Cognition, S04). Идея для этого ракурса: Согласованность действий при расширении интеллектуальной команды.
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (Anthropic, S09). Идея для этого ракурса: Прогресс и evidence завершения как итоговое чтение.

- [ ] Перед авторством перечитать выбранные разделы; точные claims/API details проверить по первичным источникам.
- [ ] Переиспользовать концепции своими словами с attribution; не копировать текст, полный перевод или чужую схему.
- [ ] Различить утверждение статьи, наш пример и авторское обобщение; source caveats — в [SOURCES](SOURCES.md).

## Авторство, редактура и фактчекинг — обязательные todo

- [ ] Соблюсти [технические требования](../../../course/technical-requirements.md): Markdown и Mermaid с подписью, accTitle/accDescr и текстовым эквивалентом.
- [ ] Проверить текстовую семантику Mermaid source, подписи и текстового эквивалента; не делать скриншоты и визуальную вычитку SVG/HTML.
- [ ] Сохранить text-only review и static-build fingerprints; не проставлять visual/AX/browser PASS и не повторять UI-код zoom/pan/fullscreen в лекции.

- [ ] Применить `technical-markdown-lectures` с deep-theory depth; созданные editorial skills прочитать перед review и записать версии/usage.
- [ ] После написания выполнить полную вычитку: язык, терминология, структура, повторы внутри лекции и по соседним темам.
- [ ] Отдельно перепроверить существенные claims, числа/даты/версии, соответствие схем тексту и code/evidence.
- [ ] Исправить findings и повторно проверить затронутый текст; существенная переработка требует полной вычитки.
- [ ] Сохранить per-lecture review record с content hash и source anchors; missing/stale review запрещает reviewed.
- [ ] Перед публикацией сверить topic ownership/cross-links и отсутствие unresolved существенных замечаний.
