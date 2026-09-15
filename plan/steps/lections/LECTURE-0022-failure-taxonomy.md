# TODO — Лекция 22. Failure modes: причины, propagation и retry amplification

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0022-failure-taxonomy.md` (ещё не написан).

Track: core; исходная тема init: 22.

## Цель и уникальная область

Объяснить failure root-cause taxonomy; retry amplification; shared-fixture correlation: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [21](LECTURE-0021-evaluation.md).

## Что писать — todo

- [ ] Развести infrastructure/tool/workflow/reasoning/policy failures и observational symptoms.
- [ ] Объяснить retry storm, false completion, stale state и propagation через handoffs.
- [ ] Разобрать retained PRB-0035/0051/0052, отделяя причина/исправление/verification.
- [ ] Сравнить ошибочную ветку fixed graph и ошибочный replan; не переопределять recovery protocol или eval metrics.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [15](LECTURE-0015-strict-workflow.md), [16](LECTURE-0016-agent-orchestrator.md), [18](LECTURE-0018-recovery-idempotency.md), [21](LECTURE-0021-evaluation.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

plan/problems/PRB-0035/0051/0052; associated evidence.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) (AWS Architecture Blog, S13). Идея для этого ракурса: Jitter против синхронизированных retries.
- [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise) (Anthropic, S21). Идея для этого ракурса: Infrastructure noise как источник ложных выводов.

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
