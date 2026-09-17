# Todo-планы лекций: маршрут, ownership и согласованность

Updated: 2026-09-17

Status: planning reviewed; lectures 00–12 published; other 14 lecture texts not written

## Размещение и формат

27 планов `LECTURE-NNNN-*.md` лежат в этой директории; тексты предназначены исключительно для
`course/lectures/`. Todo означает задачи автора, не лабораторные задания студенту.
26 core lectures с последовательными IDs 00–25; optional Kubernetes extension — 26.
Соответствие прежним тематическим номерам зафиксировано в [STEP-0034](../STEP-0034-course-sequential-numbering.md).
Реестр: [lecture-map.json](lecture-map.json); статьи: [SOURCES.md](SOURCES.md).
Обязательны [технические требования](../../../course/technical-requirements.md): Markdown,
Mermaid-схемы, доступность, static HTML и проверка отрендеренных диаграмм.
Согласованность плана проверена, но отсутствие повторов в ещё не написанных лекциях не заявляется.
Каждый текст должен отдельно пройти duplication/content review ADR-0034.

## Порядок чтения и зависимости

Core IDs совпадают с порядком изучения. Основной маршрут:

`00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17 → 18 → 19 → 20 → 21 → 22 → 23 → 24 → 25`.

26 — optional после 08/19. Ссылки на последующие лекции — navigation, не prerequisite.
При первом упоминании будущего термина дать только краткую интуицию и forward reference.
Каноническое определение даётся primary owner один раз; остальные лекции применяют его,
не копируя абзацы, рисунки или разбор того же примера.

## Карта единственного владения теорией

| План | Primary concepts | Не переписывать |
| --- | --- | --- |
| [00 Агентная система: agency, reasoning и среда](LECTURE-0000-agentic-baseline.md) | agency; agent loop; reasoning/action/observation | 01, 06, 07 |
| [01 Декомпозиция ответственности и организация команды](LECTURE-0001-organization.md) | role decomposition; task coupling; separation of duties | 13, 12, 15, 16, 24 |
| [02 Контракты, артефакты и границы доверия](LECTURE-0002-contracts.md) | artifact schema; contract invariants; cross-task binding | 13, 14, 06 |
| [03 Harness и инженерия контекста одного вызова](LECTURE-0003-harness-context.md) | per-turn context selection; model-provider abstraction; structured response boundary | 04, 17, 23 |
| [04 Состояние и память мультиагентной системы](LECTURE-0004-state-memory.md) | state lifecycle; artifact visibility; durable vs ephemeral knowledge | 02, 03, 12, 17 |
| [05 MAF: executors, edges и runtime графа](LECTURE-0005-maf-executors.md) | executor semantics; edge message delivery; runtime graph signature | 02, 06, 17 |
| [06 Жёсткий workflow: reducer, branching и convergence](LECTURE-0006-strict-workflow.md) | code-owned transition policy; terminal convergence; bounded rework routing | 05, 07, 17, 24 |
| [07 Agent-orchestrator: planning, delegation и replanning](LECTURE-0007-agent-orchestrator.md) | model-directed delegation; task/progress ledger; planner/executor separation | 09, 06, 19, 24 |
| [08 Изоляция среды исполнения](LECTURE-0008-isolation.md) | filesystem containment; network containment; process namespace boundary | 19, 26 |
| [09 MCP как интерфейс, а не политика координации](LECTURE-0009-mcp-interface.md) | MCP host/client/server; protocol capability negotiation; tool interface ergonomics | 10, 11, 18, 19 |
| [10 Аналитический SQL и ограниченные data capabilities](LECTURE-0010-analytical-sql.md) | analytical query scope; SQL resource envelope; read capability composition | 11, 12, 19 |
| [11 dbt, lineage и семантика аналитической модели](LECTURE-0011-dbt-semantics.md) | model grain; transformation lineage; dbt validation stages | 18, 12, 14, 15 |
| [12 Analyst: discovery, lineage и provenance фактов](LECTURE-0012-analyst-provenance.md) | data fact provenance; semantic discovery; facts/assumptions distinction | 11, 13, 04 |
| [13 PM: формальная спецификация и пределы знания](LECTURE-0013-pm-specification.md) | business metric definition; requirements readiness; needs-user semantics | 12, 14, 06 |
| [14 DE: ограниченная автономия изменения данных](LECTURE-0014-data-engineer.md) | implementation authority; candidate change boundary; semantic repair | 11, 15, 06, 17 |
| [15 QA: независимые проверки и принятие дефекта](LECTURE-0015-qa-evidence.md) | QA independent probes; mutation detection; accepted defect evidence | 16, 06, 21 |
| [16 Reviewer: quality judgment и separation от автора](LECTURE-0016-review-authority.md) | review authority; false approval; maintainability judgment | 01, 15, 21 |
| [17 Recovery: checkpoints, receipts и пределы exactly-once](LECTURE-0017-recovery-idempotency.md) | checkpoint commit boundary; operation idempotency; receipt crash windows | 18, 06, 04, 22 |
| [18 Airflow API: наблюдение и контролируемые операции](LECTURE-0018-airflow-operations.md) | data orchestration boundary; operation approval binding; observer/trigger separation | 06, 17, 19 |
| [19 Security: untrusted content, identity и enforcement](LECTURE-0019-security-authority.md) | indirect prompt injection; authentication/authorization distinction; capability escalation control | 08, 09, 07, 26, 24 |
| [20 Observability: trace causality и границы наблюдения](LECTURE-0020-observability.md) | trace context propagation; telemetry cardinality; sampling/retention design | 17, 21, 22 |
| [21 Evaluation: outcome, baseline и статистическая неопределённость](LECTURE-0021-evaluation.md) | task/trial distinction; quality vs invariant evaluation; baseline comparison uncertainty | 15, 16, 20, 22, 23, 24 |
| [22 Failure modes: причины, propagation и retry amplification](LECTURE-0022-failure-taxonomy.md) | failure root-cause taxonomy; retry amplification; shared-fixture correlation | 06, 07, 17, 21 |
| [23 Cost/performance: budgets, critical path и эффективность](LECTURE-0023-cost-performance.md) | budget allocation; critical-path cost trade-off; tool context overhead | 03, 07, 21, 24 |
| [24 Workflow vs agent-orchestrator: сценарии, trade-offs и гибрид](LECTURE-0024-orchestration-comparison.md) | scenario architecture selection; hybrid orchestration envelope; risk/adaptivity decision matrix | 01, 06, 07, 19, 21, 23, 25 |
| [25 Итоговый синтез: наш мультиагент как система](LECTURE-0025-architecture-synthesis.md) | integrated architecture rationale; evidence-bounded system claims; cross-layer change impact | 13, 06, 07, 21, 24 |
| [26 Deployment extension: Kubernetes и tenancy](LECTURE-0026-deployment-theory.md) | tenancy deployment model; namespace vs tenant isolation; deployment resource governance | 08, 19 |

## Проверка спорных пересечений

| Близкие темы | Разделение объяснения |
| --- | --- |
| 00 / 01 / 06 / 07 / 24 | Agent loop → role decomposition → fixed control mechanics → model-directed management → сценарный выбор |
| 05 / 06 / 17 | Runtime executor/message mechanics → business transition relation → durable commit/recovery semantics |
| 02 / 13 / 12 | Artifact contract → business readiness → provenance data facts |
| 03 / 04 / 23 | Отбор текущего контекста → lifetime/visibility durable state → стоимость и resource allocation |
| 08 / 19 / 26 | Local physical containment → threat/auth/capability policy → deployment/tenancy alternatives |
| 09 / 10 / 11 / 18 | Общий protocol/interface → bounded SQL access → transformations/lineage → data scheduling operations |
| 11 / 14 / 15 / 16 | Grain/validation semantics → implementation authority → independent defect evidence → quality approval |
| 15 / 16 / 21 / 22 | QA/reviewer roles → измерения качества → failure causes; metrics и root causes не дублировать |
| 06 / 18 | Multi-agent control graph не равен Airflow data execution DAG; authority над переходами различна |
| 20 / 21 | Наблюдаемость поведения не равна оцениванию качества; trace не раскрывает private reasoning |
| 24 / 25 | Матрица выбора альтернатив → синтез уже реализованной платформы; не два повторных architecture surveys |

## Редакторский протокол согласованности

- [x] У каждой темы есть один primary owner и явные prerequisites/out-of-scope links.
- [x] Жёсткий workflow и agent-orchestrator рассмотрены отдельно; supervisor не приравнен к A2A.
- [x] В каждом плане есть минимум две первичные статьи и конкретный ракурс переиспользования идеи.
- [x] Теория отделена от фактических claims нашей реализации и historical live rates.
- [ ] При авторстве каждой лекции сверить словарь, definitions и входные знания с prerequisites.
- [ ] После написания вычитать всю лекцию и отдельно сверить claims/sources и схемы.
- [ ] Сравнить текст с primary owners и соседями: полные повторные объяснения заменить cross-links.
- [ ] Проверить переход к следующей теме и сохранение единого meaning слов workflow/agent/orchestrator.
- [ ] Исправить findings, выполнить recheck и сохранить review receipt, привязанный к content hash.
- [ ] При изменении canonical definition переоценить все ссылки-потребители и их review status.

Skills: `technical-markdown-lectures`, `technical-editorial-review` и
`technical-claim-verification` доступны; versioned packages — в `course/skills`,
локальные copies подготовлены и validated. Перед каждой лекцией читать инструкции и записывать usage.
Ни semantic text verification, ни независимый reviewer не заявляются без фактической проверки.
