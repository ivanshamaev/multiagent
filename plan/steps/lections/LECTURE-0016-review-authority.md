# TODO — Лекция 16. Reviewer: quality judgment и separation от автора

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0016-review-authority.md` (ещё не написан).

Track: core; исходная тема init: 14.

## Цель и уникальная область

Объяснить review authority; false approval; maintainability judgment: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [15](LECTURE-0015-qa-evidence.md).

## Что писать — todo

- [ ] Развести semantic QA и architecture/maintainability review.
- [ ] Объяснить право принять/отклонить изменение и запрет self-approval.
- [ ] Показать fresh read-only reviewer context и четыре retained mutations.
- [ ] Обсудить correlated blind spots: отдельная роль не гарантирует статистическую независимость.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [01](LECTURE-0001-organization.md), [15](LECTURE-0015-qa-evidence.md), [21](LECTURE-0021-evaluation.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/reviewer_workflow.py; STEP-0011; EXP-0004.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Code Health: Google’s Internal Code Quality Efforts](https://testing.googleblog.com/2017/04/code-health-googles-internal-code.html) (Google Testing Blog, S19). Идея для этого ракурса: Code health сверх бинарного test result.
- [Multi-Agents: What’s Actually Working](https://cognition.com/blog/multi-agents-working) (Cognition, S04). Идея для этого ракурса: Дополнительный интеллектуальный review при сохранении single writer.

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
