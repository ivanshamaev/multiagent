# Syllabus и маршрут

Цель — объяснять модели, invariants и trade-offs multi-agent systems, не освоение одного SDK.
Prerequisites: Python/SQL и data/software pipelines. Kubernetes не требуется для core.

## Core: порядок чтения

| Позиция | ID и тема | Prerequisites |
| --- | --- | --- |
| 1 | [00 — Агентная система: agency, reasoning и среда](modules/module-00-agentic-baseline/README.md) | — |
| 2 | [01 — Декомпозиция ответственности и организация команды](modules/module-01-organization/README.md) | 0 |
| 3 | [03 — Контракты, артефакты и границы доверия](modules/module-03-contracts/README.md) | 1 |
| 4 | [04 — Harness и инженерия контекста одного вызова](modules/module-04-harness-context/README.md) | 3 |
| 5 | [17 — Context, durable state, artifacts и knowledge](modules/module-17-state-memory/README.md) | 4 |
| 6 | [02 — MAF: executors, edges и runtime графа](modules/module-02-maf-executors/README.md) | 3, 17 |
| 7 | [15 — Жёсткий workflow: reducer, branching и convergence](modules/module-15-strict-workflow/README.md) | 2 |
| 8 | [16 — Agent-orchestrator: planning, delegation и replanning](modules/module-16-agent-orchestrator/README.md) | 15 |
| 9 | [05 — Изоляция среды исполнения](modules/module-05-isolation/README.md) | 3 |
| 10 | [06 — MCP как интерфейс, а не политика координации](modules/module-06-mcp-interface/README.md) | 5, 4 |
| 11 | [07 — Аналитический SQL и ограниченные data capabilities](modules/module-07-analytical-sql/README.md) | 6 |
| 12 | [08 — dbt, lineage и семантика аналитической модели](modules/module-08-dbt-semantics/README.md) | 7 |
| 13 | [11 — Analyst: discovery, lineage и provenance фактов](modules/module-11-analyst-provenance/README.md) | 8, 17 |
| 14 | [10 — PM: формальная спецификация и пределы знания](modules/module-10-pm-specification/README.md) | 11 |
| 15 | [12 — DE: ограниченная автономия изменения данных](modules/module-12-data-engineer/README.md) | 10, 8 |
| 16 | [13 — QA: независимые проверки и принятие дефекта](modules/module-13-qa-evidence/README.md) | 12 |
| 17 | [14 — Reviewer: quality judgment и separation от автора](modules/module-14-review-authority/README.md) | 13 |
| 18 | [18 — Recovery: checkpoints, receipts и пределы exactly-once](modules/module-18-recovery-idempotency/README.md) | 15, 17 |
| 19 | [09 — Airflow API: наблюдение и контролируемые операции](modules/module-09-airflow-operations/README.md) | 6, 18 |
| 20 | [19 — Security: untrusted content, identity и enforcement](modules/module-19-security-authority/README.md) | 5, 6, 9, 16 |
| 21 | [20 — Observability: trace causality и границы наблюдения](modules/module-20-observability/README.md) | 15, 16, 18 |
| 22 | [21 — Evaluation: outcome, baseline и статистическая неопределённость](modules/module-21-evaluation/README.md) | 13, 14, 20 |
| 23 | [22 — Failure modes: причины, propagation и retry amplification](modules/module-22-failure-taxonomy/README.md) | 21 |
| 24 | [23 — Cost/performance: budgets, critical path и эффективность](modules/module-23-cost-performance/README.md) | 21, 16 |
| 25 | [26 — Workflow vs agent-orchestrator: сценарии, trade-offs и гибрид](modules/module-26-orchestration-comparison/README.md) | 15, 16, 19, 21, 23 |
| 26 | [25 — Итоговый синтез: наш мультиагент как система](modules/module-25-architecture-synthesis/README.md) | 26, 22, 10, 12 |

## Optional extension

[24 — Deployment theory](extensions/module-24-deployment-theory/README.md) — отдельно после prerequisites.

## Границы

15 — code-owned transitions; 16 — model-directed delegation/replanning; 26 — сценарный выбор/
hybrid; 25 — синтез нашего примера. A2A не равно supervisor, topology не равна authority ownership.
Определения имеют primary owner, остальные лекции их применяют и cross-link.
[Полная карта](../plan/steps/lections/README.md). Manifest задаёт canonical paths/status/order;
изменение curriculum синхронизируется с planning map. Вопросы самопроверки только концептуальные.
