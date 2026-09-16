# TODO — Лекция 02. Контракты, артефакты и границы доверия

Status: completed; content and reader verified; published through STEP-0032

Updated: 2026-09-16

Текст: `course/lectures/LECTURE-0002-contracts.md`.

Track: core; исходная тема init: 03.

## Цель и уникальная область

Объяснить artifact schema; contract invariants; cross-task binding: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [01](LECTURE-0001-organization.md).

## Что писать — todo

- [x] Дать строгую модель input/output contract: syntax validity не означает semantic correctness.
- [x] Объяснить versioning, immutable artifacts и task/actor binding.
- [x] Рассмотреть malformed payload, extra fields и ложное утверждение completion как разные нарушения.
- [x] Показать TaskSpecification/ImplementationResult/Evidence без полного обзора workflow состояний.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [13](LECTURE-0013-pm-specification.md), [14](LECTURE-0014-data-engineer.md), [06](LECTURE-0006-strict-workflow.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

contracts/artifacts.py; STEP-0006; ADR-0014.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [x] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (Anthropic, S08). Идея для этого ракурса: Ясные интерфейсы и границы параметров.
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (Anthropic, S20). Идея для этого ракурса: Разница заявленного ответа и outcome.

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

## Результат авторства и отдельных проверок

2026-09-16: текст написан после чтения S08/S20 и Pydantic primary docs,
current contracts/reducer/tests, ADR-0014 и STEP-0006. Выполнены отдельные
полная editorial и technical passes. Уточнено, что trusted provenance
TransitionCommand — архитектурная предпосылка, а не свойство её модели;
заменены ненужные англицизмы в классификации ошибок. Финальный текст перечитан.
Same-author passes не являются независимой экспертизой. Reader gate выполнен: desktop/mobile, no-JS, keyboard, print geometry,
AX semantics, CSP/subpath/links и семь screenshots проверены. Actual screen reader,
hardware touch, printed PDF и cross-browser не проверялись.
