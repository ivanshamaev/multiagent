# TODO — Лекция 14. DE: ограниченная автономия изменения данных

Status: reviewed; text-only publication gate

Updated: 2026-09-18

Текст: `course/lectures/LECTURE-0014-data-engineer.md` (написан и проверен).

Track: core; исходная тема init: 12.

## Цель и уникальная область

Объяснить implementation authority; candidate change boundary; semantic repair: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [13](LECTURE-0013-pm-specification.md), [11](LECTURE-0011-dbt-semantics.md).

## Что писать — todo

- [x] Разделить утверждённую спецификацию и пространство допустимых implementation choices.
- [x] Объяснить isolated candidate и authority только над editable dbt subtree.
- [x] Показать Net Revenue payment/refund attribution как применение grain/semantics из 11/13.
- [x] Рассмотреть semantic repair по validator evidence; не переобъяснять QA, reducer budget и checkpoint.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [11](LECTURE-0011-dbt-semantics.md), [15](LECTURE-0015-qa-evidence.md), [06](LECTURE-0006-strict-workflow.md), [17](LECTURE-0017-recovery-idempotency.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/data_engineer.py; runtime/data_engineer_workflow.py; STEP-0009.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [x] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [What is analytics engineering?](https://www.getdbt.com/blog/what-is-analytics-engineering) (dbt Labs, S17). Идея для этого ракурса: Transformation work как инженерная дисциплина.
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (Anthropic, S09). Идея для этого ракурса: Инкрементальный прогресс без необоснованного completion.

- [x] Перед авторством перечитать выбранные разделы; точные claims/API details проверить по первичным источникам.
- [x] Переиспользовать концепции своими словами с attribution; не копировать текст, полный перевод или чужую схему.
- [x] Различить утверждение статьи, наш пример и авторское обобщение; source caveats — в [SOURCES](SOURCES.md).

## Авторство, редактура и фактчекинг — обязательные todo

- [x] Соблюсти [технические требования](../../../course/technical-requirements.md): Markdown и Mermaid с подписью, accTitle/accDescr и текстовым эквивалентом.
- [x] Проверить только текстовую семантику Mermaid source, подписи и текстового эквивалента; не делать скриншоты и визуальную вычитку SVG/HTML.
- [x] Не повторять UI-код zoom/pan/fullscreen в тексте лекции; до публикации согласовать legacy visual publication gate с уточнением пользователя от 2026-09-18, не проставляя фиктивный PASS.

- [x] Применить `technical-markdown-lectures` с deep-theory depth; созданные editorial skills прочитать перед review и записать версии/usage.
- [x] После написания выполнить полную вычитку: язык, терминология, структура, повторы внутри лекции и по соседним темам.
- [x] Отдельно перепроверить существенные claims, числа/даты/версии, соответствие схем тексту и code/evidence.
- [x] Исправить findings и повторно проверить затронутый текст; существенная переработка требует полной вычитки.
- [x] Сохранить per-lecture review record с content hash и source anchors; missing/stale review запрещает reviewed.
- [x] Перед публикацией сверить topic ownership/cross-links и отсутствие unresolved существенных замечаний.
