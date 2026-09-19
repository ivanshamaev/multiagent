# Syllabus и маршрут

Цель — объяснять модели, invariants и trade-offs multi-agent systems, не освоение одного SDK.
Prerequisites: Python/SQL и data/software pipelines. Kubernetes не требуется для core.

## Core: порядок чтения

| Позиция | ID и тема | Prerequisites |
| --- | --- | --- |
| 1 | [00 — Агентная система: agency, reasoning и среда](modules/module-00-agentic-baseline/README.md) | — |
| 2 | [01 — Декомпозиция ответственности и организация команды](modules/module-01-organization/README.md) | 0 |
| 3 | [02 — Контракты, артефакты и границы доверия](modules/module-02-contracts/README.md) | 1 |
| 4 | [03 — Harness и инженерия контекста одного вызова](modules/module-03-harness-context/README.md) | 2 |
| 5 | [04 — Состояние и память мультиагентной системы](modules/module-04-state-memory/README.md) | 3 |
| 6 | [05 — MAF: executors, edges и runtime графа](modules/module-05-maf-executors/README.md) | 2, 4 |
| 7 | [06 — Жёсткий workflow: reducer, branching и convergence](modules/module-06-strict-workflow/README.md) | 5 |
| 8 | [07 — Agent-orchestrator: planning, delegation и replanning](modules/module-07-agent-orchestrator/README.md) | 6 |
| 9 | [08 — Изоляция среды исполнения](modules/module-08-isolation/README.md) | 2 |
| 10 | [09 — MCP как интерфейс, а не политика координации](modules/module-09-mcp-interface/README.md) | 8, 3 |
| 11 | [10 — Аналитический SQL и ограниченные data capabilities](modules/module-10-analytical-sql/README.md) | 9 |
| 12 | [11 — dbt, lineage и семантика аналитической модели](modules/module-11-dbt-semantics/README.md) | 10 |
| 13 | [12 — Analyst: discovery, lineage и provenance фактов](modules/module-12-analyst-provenance/README.md) | 11, 4 |
| 14 | [13 — PM: формальная спецификация и пределы знания](modules/module-13-pm-specification/README.md) | 12 |
| 15 | [14 — DE: ограниченная автономия изменения данных](modules/module-14-data-engineer/README.md) | 13, 11 |
| 16 | [15 — QA: независимые проверки и принятие дефекта](modules/module-15-qa-evidence/README.md) | 14 |
| 17 | [16 — Reviewer: quality judgment и separation от автора](modules/module-16-review-authority/README.md) | 15 |
| 18 | [17 — Recovery: checkpoints, receipts и пределы exactly-once](modules/module-17-recovery-idempotency/README.md) | 6, 4 |
| 19 | [18 — Airflow API: наблюдение и контролируемые операции](modules/module-18-airflow-operations/README.md) | 9, 17 |
| 20 | [19 — Security: untrusted content, identity и enforcement](modules/module-19-security-authority/README.md) | 8, 9, 18, 7 |
| 21 | [20 — Observability: trace causality и границы наблюдения](modules/module-20-observability/README.md) | 6, 7, 17 |
| 22 | [21 — Evaluation: outcome, baseline и статистическая неопределённость](modules/module-21-evaluation/README.md) | 15, 16, 20 |
| 23 | [22 — Failure modes: причины, propagation и retry amplification](modules/module-22-failure-taxonomy/README.md) | 21 |
| 24 | [23 — Cost/performance: budgets, critical path и эффективность](modules/module-23-cost-performance/README.md) | 21, 7 |
| 25 | [24 — Workflow vs agent-orchestrator: сценарии, trade-offs и гибрид](modules/module-24-orchestration-comparison/README.md) | 6, 7, 19, 21, 23 |
| 26 | [25 — Итоговый синтез: наш мультиагент как система](modules/module-25-architecture-synthesis/README.md) | 24, 22, 13, 14 |

## Optional extension

[26 — Kubernetes, tenancy и границы развёртывания](extensions/module-26-deployment-theory/README.md) —
отдельно после лекций 08 и 19; Kubernetes runtime в примере не реализован.

## Границы

06 — code-owned transitions; 07 — model-directed delegation/replanning; 24 — сценарный выбор/
hybrid; 25 — синтез нашего примера. A2A не равно supervisor, topology не равна authority ownership.
Определения имеют primary owner, остальные лекции их применяют и cross-link.
[Полная карта](../plan/steps/lections/README.md). Manifest задаёт canonical paths/status/order;
изменение curriculum синхронизируется с planning map. Вопросы самопроверки только концептуальные.
