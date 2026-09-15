# TODO — Лекция 26. Workflow vs agent-orchestrator: сценарии, trade-offs и гибрид

Status: planned

Updated: 2026-09-15

Текст: `course/lectures/LECTURE-0026-orchestration-comparison.md` (ещё не написан).

Track: core; исходная тема init: новое архитектурное сравнение.

## Цель и уникальная область

Объяснить scenario architecture selection; hybrid orchestration envelope; risk/adaptivity decision matrix: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [15](LECTURE-0015-strict-workflow.md), [16](LECTURE-0016-agent-orchestrator.md), [19](LECTURE-0019-security-authority.md), [21](LECTURE-0021-evaluation.md), [23](LECTURE-0023-cost-performance.md).

## Что писать — todo

- [ ] Сравнить ownership plan/routing/stopping, predictability, audit/replay, адаптивность, cost/latency и риски.
- [ ] Показать для каждого подхода преимущества/недостатки и cases, где он оправдан или избыточен.
- [ ] Разобрать минимум восемь data-engineering scenarios по единой rubric, включая alternative single agent/no agent.
- [ ] Описать hybrid: dynamic read investigation внутри static permission/quality/write gates; не считать любой orchestrator безграничным.
- [ ] Сопоставить Anthropic и Cognition без ложного универсального победителя; дать критерии выбора, а не vendor recommendation.
- [ ] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [ ] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [01](LECTURE-0001-organization.md), [15](LECTURE-0015-strict-workflow.md), [16](LECTURE-0016-agent-orchestrator.md), [19](LECTURE-0019-security-authority.md), [21](LECTURE-0021-evaluation.md), [23](LECTURE-0023-cost-performance.md), [25](LECTURE-0025-architecture-synthesis.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Центральное сравнение — todo для раскрытия

- [ ] Workflow: code-owned допустимые пути, versioned policy, стабильные acceptance/approval gates;
  преимущества auditability и контроля side effects, недостатки при неизвестных subtasks/новых ситуациях.
- [ ] Agent-orchestrator: динамическая декомпозиция/worker selection/replanning; преимущества в
  discovery/open-ended research, недостатки planner error propagation, budget variance и coordination cost.
- [ ] Уточнить: fixed graph допускает parallelism/branching/loops; deterministic control не делает
  вывод LLM детерминированным. Dynamic routing допускает audit logs и hard bounds, но не гарантирует их.
- [ ] Hybrid: code-owned outer policy и write/quality gates, model-directed read investigation внутри;
  объяснить стоимость двух уровней и условия, когда простой fixed workflow/один agent лучше.
- [ ] Сравнить agent-as-tool/subworkflow/handoff без отождествления transport и control ownership.

## Матрица применимости — раскрыть каждый scenario

Это проектируемые аналитические выводы, не экспериментальные результаты нашей платформы.
Для каждого объяснить задачу, известность subtasks, coupling/write risk, rationale, преимущество,
недостаток и условие смены архитектуры; опираться на статьи ниже и owners 01/15/16/19/21/23.

| Scenario | Кандидат для обсуждения | Основной вопрос выбора |
| --- | --- | --- |
| Регулярная ingestion/типовые schema checks | Обычный deterministic data workflow, возможно без LLM | Есть ли здесь reasoning, который оправдывает agent? |
| Net Revenue по принятому spec | Fixed role workflow | Как сохранить независимые quality gates и bounded repair? |
| Неизвестная причина падения revenue | Read-only agent-orchestrator | Какие ветки расследования возникают только после observations? |
| Неясный business request/неполный lineage | Hybrid discovery + fixed PM readiness | Как не заменить неизвестные business semantics догадкой planner? |
| Миграция множества связанных dbt моделей | Hybrid read decomposition + controlled single writer | Насколько subtasks связаны и где конфликтуют решения? |
| Сравнение источников/схем/подходов | Manager с independent read workers | Достаточно ли независимости subtasks для parallel reasoning? |
| Регламентное изменение с audit/release requirements | Fixed acceptance/approval workflow | Что обязано оставаться code-owned независимо от reasoning? |
| Incident diagnosis с опасным remediation | Dynamic investigation + fixed write approval | Где заканчивается гипотеза и начинается разрешённый side effect? |
| Поиск regressions/разбор нескольких failures | Fixed checks + optional manager diagnosis | Как избежать LLM override фактического non-zero verdict? |
| Небольшая одношаговая bounded задача | Single agent или обычная функция | Окупается ли management/communication overhead? |

- [ ] Не выдавать mapping за универсальную рекомендацию: раскрыть counterexample каждой группы.
- [ ] Разделить преимущества архитектуры и преимущества конкретной модели/бюджета/dataset.

## Иллюстрация нашей системой

Our workflow as implemented baseline; dynamic/hybrid variants explicitly hypothetical; ADR-0035.

- [ ] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [ ] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Anthropic, S01). Идея для этого ракурса: Архитектурная граница predefined vs model-directed flow.
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (Anthropic, S02). Идея для этого ракурса: Применимость динамического исследования.
- [Don’t Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) (Cognition, S03). Идея для этого ракурса: Ограничения разделения зависимых действий.
- [Multi-Agents: What’s Actually Working](https://cognition.com/blog/multi-agents-working) (Cognition, S04). Идея для этого ракурса: Managed intellectual parallelism при single writer.

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
