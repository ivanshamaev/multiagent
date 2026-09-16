# TODO — Лекция 17. Recovery: checkpoints, receipts и пределы exactly-once

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0017-recovery-idempotency.md` (ещё не написан).

Track: core; исходная тема init: 18.

## Цель и уникальная область

Объяснить checkpoint commit boundary; operation idempotency; receipt crash windows: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [06](LECTURE-0006-strict-workflow.md), [04](LECTURE-0004-state-memory.md).

## Что писать — todo

- [ ] Разобрать kill до/после role receipt и durable checkpoint; разные окна повторного исполнения.
- [ ] Дать определения at-most/at-least/exactly-once относительно наблюдаемого эффекта.
- [ ] Объяснить request IDs, reconciliation и почему checkpoint не гарантирует exactly-once внешнего side effect.
- [ ] Показать staged 0600 publication и receipt-backed restart; не превращать в fault-injection lab.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [18](LECTURE-0018-airflow-operations.md), [06](LECTURE-0006-strict-workflow.md), [04](LECTURE-0004-state-memory.md), [22](LECTURE-0022-failure-taxonomy.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/checkpoints.py; runtime/role_receipts.py; STEP-0018/0024; PRB-0052.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) (AWS Builders’ Library, S12). Идея для этого ракурса: Idempotent request identity и повторные эффекты.
- [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) (Anthropic, S27). Идея для этого ракурса: Durability session и исполняемая среда как разные lifecycles.

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
