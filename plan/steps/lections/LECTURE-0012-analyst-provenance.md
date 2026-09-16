# TODO — Лекция 12. Analyst: discovery, lineage и provenance фактов

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0012-analyst-provenance.md` (ещё не написан).

Track: core; исходная тема init: 11.

## Цель и уникальная область

Объяснить data fact provenance; semantic discovery; facts/assumptions distinction: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [11](LECTURE-0011-dbt-semantics.md), [04](LECTURE-0004-state-memory.md).

## Что писать — todo

- [ ] Разобрать schema/lineage/profile как разные источники знания.
- [ ] Объяснить evidence-backed fact и ограничение вывода из sampled/aggregate data.
- [ ] Показать three fresh read phases и synthesis; не определять business metric вместо PM.
- [ ] Сопоставить доступность данных и достаточность для требования; не обещать anomaly investigation corpus.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [11](LECTURE-0011-dbt-semantics.md), [13](LECTURE-0013-pm-specification.md), [04](LECTURE-0004-state-memory.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/analyst.py; tests/fixtures/analyst_cases.json; STEP-0012.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Data Mesh Principles and Logical Architecture](https://martinfowler.com/articles/data-mesh-principles.html) (Zhamak Dehghani / Martin Fowler, S14). Идея для этого ракурса: Discoverability/understandability данных.
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Anthropic, S07). Идея для этого ракурса: Отбор релевантной информации для synthesis.

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
