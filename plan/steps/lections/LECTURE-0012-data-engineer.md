# TODO — Лекция 12. DE: ограниченная автономия изменения данных

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0012-data-engineer.md` (ещё не написан).

Track: core; исходная тема init: 12.

## Цель и уникальная область

Объяснить implementation authority; candidate change boundary; semantic repair: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [10](LECTURE-0010-pm-specification.md), [08](LECTURE-0008-dbt-semantics.md).

## Что писать — todo

- [ ] Разделить утверждённую спецификацию и пространство допустимых implementation choices.
- [ ] Объяснить isolated candidate и authority только над editable dbt subtree.
- [ ] Показать Net Revenue payment/refund attribution как применение grain/semantics из 08/10.
- [ ] Рассмотреть semantic repair по validator evidence; не переобъяснять QA, reducer budget и checkpoint.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [08](LECTURE-0008-dbt-semantics.md), [13](LECTURE-0013-qa-evidence.md), [15](LECTURE-0015-strict-workflow.md), [18](LECTURE-0018-recovery-idempotency.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/data_engineer.py; runtime/data_engineer_workflow.py; STEP-0009.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [What is analytics engineering?](https://www.getdbt.com/blog/what-is-analytics-engineering) (dbt Labs, S17). Идея для этого ракурса: Transformation work как инженерная дисциплина.
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (Anthropic, S09). Идея для этого ракурса: Инкрементальный прогресс без необоснованного completion.

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
