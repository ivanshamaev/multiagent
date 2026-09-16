# TODO — Лекция 21. Evaluation: outcome, baseline и статистическая неопределённость

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0021-evaluation.md` (ещё не написан).

Track: core; исходная тема init: 21.

## Цель и уникальная область

Объяснить task/trial distinction; quality vs invariant evaluation; baseline comparison uncertainty: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [15](LECTURE-0015-qa-evidence.md), [16](LECTURE-0016-review-authority.md), [20](LECTURE-0020-observability.md).

## Что писать — todo

- [ ] Определить task/trial/grader/outcome и единицу измерения reliability.
- [ ] Развести offline invariants, dated live model rates и статистическое сравнение fresh samples.
- [ ] Разобрать false pass/false approval, выборку/доверие, contamination и ограничения малого N.
- [ ] Показать 17×3 harness и DE historical sample; путь dynamic manager оценивать не по идентичности trajectory.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [15](LECTURE-0015-qa-evidence.md), [16](LECTURE-0016-review-authority.md), [20](LECTURE-0020-observability.md), [22](LECTURE-0022-failure-taxonomy.md), [23](LECTURE-0023-cost-performance.md), [24](LECTURE-0024-orchestration-comparison.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

evals/phase_k/; STEP-0024; STEP-0009 sample.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (Anthropic, S20). Идея для этого ракурса: Outcome-oriented multi-turn evaluation.
- [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise) (Anthropic, S21). Идея для этого ракурса: Контроль инфраструктурных переменных эксперимента.

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
