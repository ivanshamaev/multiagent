# TODO — Лекция 15. QA: независимые проверки и принятие дефекта

Status: lecture written; text-only reviewed

Updated: 2026-09-18

Текст: `course/lectures/LECTURE-0015-qa-evidence.md`.

Track: core; исходная тема init: 13.

## Цель и уникальная область

Объяснить QA independent probes; mutation detection; accepted defect evidence: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [14](LECTURE-0014-data-engineer.md).

## Что писать — todo

- [x] Развести public validator success и независимую semantic probe.
- [x] Объяснить mutation/false pass и authority QA сообщать defect, не исправлять candidate.
- [x] Разобрать code-owned immutable SQL probes и fresh assessment.
- [x] Применить один QA mutation как case; механическое rework routing и статистику вынести владельцам.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [16](LECTURE-0016-review-authority.md), [06](LECTURE-0006-strict-workflow.md), [21](LECTURE-0021-evaluation.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/qa_workflow.py; tests/fixtures/qa_mutants/; STEP-0010; EXP-0003.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [x] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Why data testing is essential for analytics engineering](https://www.getdbt.com/blog/data-testing) (dbt Labs, S18). Идея для этого ракурса: Data assertions и доверие к результату.
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (Anthropic, S20). Идея для этого ракурса: Несколько проверяющих аспектов результата.

- [x] Перед авторством перечитать выбранные разделы; точные claims/API details проверить по первичным источникам.
- [x] Переиспользовать концепции своими словами с attribution; не копировать текст, полный перевод или чужую схему.
- [x] Различить утверждение статьи, наш пример и авторское обобщение; source caveats — в [SOURCES](SOURCES.md).

## Авторство, редактура и фактчекинг — обязательные todo

- [x] Соблюсти [технические требования](../../../course/technical-requirements.md): Markdown и Mermaid с подписью, accTitle/accDescr и текстовым эквивалентом.
- [x] Проверить текстовую семантику Mermaid source, подписи и текстового эквивалента; не делать скриншоты и визуальную вычитку SVG/HTML.
- [x] Сохранить text-only review и static-build fingerprints; не проставлять visual/AX/browser PASS и не повторять UI-код zoom/pan/fullscreen в лекции.

- [x] Применить `technical-markdown-lectures` с deep-theory depth; созданные editorial skills прочитать перед review и записать версии/usage.
- [x] После написания выполнить полную вычитку: язык, терминология, структура, повторы внутри лекции и по соседним темам.
- [x] Отдельно перепроверить существенные claims, числа/даты/версии, соответствие схем тексту и code/evidence.
- [x] Исправить findings и повторно проверить затронутый текст; существенная переработка требует полной вычитки.
- [x] Сохранить per-lecture review record с content hash и source anchors; missing/stale review запрещает reviewed.
- [x] Перед публикацией сверить topic ownership/cross-links и отсутствие unresolved существенных замечаний.
