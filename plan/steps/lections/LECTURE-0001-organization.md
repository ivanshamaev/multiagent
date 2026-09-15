# TODO — Лекция 01. Декомпозиция ответственности и организация команды

Status: completed; content and reader verified; published through STEP-0031

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0001-organization.md`.

Track: core; исходная тема init: 01.

## Цель и уникальная область

Объяснить role decomposition; task coupling; separation of duties: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [00](LECTURE-0000-agentic-baseline.md).

## Что писать — todo

- [x] Сформулировать критерии разделения задачи: связность, разнородность знаний и ownership результата.
- [x] Развести role name и действительную ответственность/capability; не считать число агентов мерой качества.
- [x] Объяснить конфликт решений при разделении зависимого engineering work.
- [x] Показать Analyst/PM/DE/QA/Reviewer как различные полномочия, не подробно разбирать их алгоритмы.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [10](LECTURE-0010-pm-specification.md), [11](LECTURE-0011-analyst-provenance.md), [13](LECTURE-0013-qa-evidence.md), [14](LECTURE-0014-review-authority.md), [26](LECTURE-0026-orchestration-comparison.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

policies/profiles/; ADR-0003/0006; STEP-0008.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [x] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Data Mesh Principles and Logical Architecture](https://martinfowler.com/articles/data-mesh-principles.html) (Zhamak Dehghani / Martin Fowler, S14). Идея для этого ракурса: Ownership данных как аналогия, не доказательство Data Mesh.
- [Don’t Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) (Cognition, S03). Идея для этого ракурса: Согласованность решений при разделении инженерной работы.

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

2026-09-15: полный текст написан, отдельно вычитан и проверен по первичным статьям,
четырём profiles, ADR-0003/0006 и историческому STEP-0008. Добавлен Cognition S04
как обязательное уточнение S03. Исправлены претензия на исчерпывающую типологию
и лишние английские формулировки; весь исправленный текст перечитан.
Авторские passes не являются независимой экспертизой. SVG/browser gate выполнен: desktop/mobile, no-JS, keyboard, print geometry,
AX name/description, CSP/subpath/links и семь визуально проверенных screenshots.
Реальный screen reader, аппаратный touch и cross-browser не проверялись.
Content и publication receipts фиксируют отдельные passes; публикация разрешена только
при актуальных hashes обоих records.
