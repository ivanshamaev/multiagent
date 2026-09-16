# TODO — Лекция 26. Deployment extension: Kubernetes и tenancy

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0026-deployment-theory.md` (ещё не написан).

Track: extension; исходная тема init: 24.

## Цель и уникальная область

Объяснить tenancy deployment model; namespace vs tenant isolation; deployment resource governance: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [08](LECTURE-0008-isolation.md), [19](LECTURE-0019-security-authority.md).

## Что писать — todo

- [ ] Сравнить shared namespace/virtual control plane/cluster boundary как deployment alternatives.
- [ ] Объяснить ServiceAccount, resource bounds/cgroups, network policy и seccomp на уровне theory.
- [ ] Отделить orchestration policy от deployment substrate и shared kernel risks.
- [ ] Показать наши host Bubblewrap/Compose boundaries; Kubernetes явно не реализован.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [08](LECTURE-0008-isolation.md), [19](LECTURE-0019-security-authority.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

Extension only; ADR-0001/0031.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Three Tenancy Models For Kubernetes](https://kubernetes.io/blog/2021/04/15/three-tenancy-models-for-kubernetes/) (Kubernetes authors, S22). Идея для этого ракурса: Сравнение tenancy models.
- [Beyond permission prompts: making Claude Code more secure and autonomous](https://www.anthropic.com/engineering/claude-code-sandboxing) (Anthropic, S10). Идея для этого ракурса: Filesystem/network isolation как необходимая часть containment.

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
