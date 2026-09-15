# Источники и provenance

[init syllabus](../init/init_cource_plan.md) — исходная thematic map, не implementation evidence.
IDs 00–25 сохранены; 26 — отдельное сравнение. Practice requirements init superseded
[ADR-0034](../plan/decisions/ADR-0034-theory-course-and-editorial-gates.md).

[SOURCES](../plan/steps/lections/SOURCES.md) — 30 первичных статей и caveats;
[sources.json](sources.json) — registry. Отбор качественный, без fabricated popularity counts.

| ID | Primary concepts | Статьи | Implementation boundary |
| --- | --- | --- | --- |
| [0](modules/module-00-agentic-baseline/README.md) | agency; agent loop; reasoning/action/observation | S23, S01 | offline-proven |
| [1](modules/module-01-organization/README.md) | role decomposition; task coupling; separation of duties | S14, S03 | offline-proven |
| [2](modules/module-02-maf-executors/README.md) | executor semantics; edge message delivery; runtime graph signature | S06, S05 | offline-proven |
| [3](modules/module-03-contracts/README.md) | artifact schema; contract invariants; cross-task binding | S08, S20 | offline-proven |
| [4](modules/module-04-harness-context/README.md) | per-turn context selection; model-provider abstraction; structured response boundary | S07, S30 | offline-proven |
| [5](modules/module-05-isolation/README.md) | filesystem containment; network containment; process namespace boundary | S10, S27 | offline-proven |
| [6](modules/module-06-mcp-interface/README.md) | MCP host/client/server; protocol capability negotiation; tool interface ergonomics | S11, S08 | offline-proven |
| [7](modules/module-07-analytical-sql/README.md) | analytical query scope; SQL resource envelope; read capability composition | S08, S16 | offline-proven |
| [8](modules/module-08-dbt-semantics/README.md) | model grain; transformation lineage; dbt validation stages | S17, S18 | offline-proven |
| [9](modules/module-09-airflow-operations/README.md) | data orchestration boundary; operation approval binding; observer/trigger separation | S28, S12 | offline-proven |
| [10](modules/module-10-pm-specification/README.md) | business metric definition; requirements readiness; needs-user semantics | S15, S14 | offline-proven |
| [11](modules/module-11-analyst-provenance/README.md) | data fact provenance; semantic discovery; facts/assumptions distinction | S14, S07 | offline-proven |
| [12](modules/module-12-data-engineer/README.md) | implementation authority; candidate change boundary; semantic repair | S17, S09 | offline-proven |
| [13](modules/module-13-qa-evidence/README.md) | QA independent probes; mutation detection; accepted defect evidence | S18, S20 | offline-proven |
| [14](modules/module-14-review-authority/README.md) | review authority; false approval; maintainability judgment | S19, S04 | offline-proven |
| [15](modules/module-15-strict-workflow/README.md) | code-owned transition policy; terminal convergence; bounded rework routing | S01, S05 | offline-proven |
| [16](modules/module-16-agent-orchestrator/README.md) | model-directed delegation; task/progress ledger; planner/executor separation | S24, S02 | not-implemented |
| [17](modules/module-17-state-memory/README.md) | state lifecycle; artifact visibility; durable vs ephemeral knowledge | S07, S03 | offline-proven |
| [18](modules/module-18-recovery-idempotency/README.md) | checkpoint commit boundary; operation idempotency; receipt crash windows | S12, S27 | offline-proven |
| [19](modules/module-19-security-authority/README.md) | indirect prompt injection; authentication/authorization distinction; capability escalation control | S25, S10 | offline-proven |
| [20](modules/module-20-observability/README.md) | trace context propagation; telemetry cardinality; sampling/retention design | S29, S27 | offline-proven |
| [21](modules/module-21-evaluation/README.md) | task/trial distinction; quality vs invariant evaluation; baseline comparison uncertainty | S20, S21 | offline-proven |
| [22](modules/module-22-failure-taxonomy/README.md) | failure root-cause taxonomy; retry amplification; shared-fixture correlation | S13, S21 | offline-proven |
| [23](modules/module-23-cost-performance/README.md) | budget allocation; critical-path cost trade-off; tool context overhead | S26, S02 | offline-proven |
| [24](extensions/module-24-deployment-theory/README.md) | tenancy deployment model; namespace vs tenant isolation; deployment resource governance | S22, S10 | not-implemented |
| [25](modules/module-25-architecture-synthesis/README.md) | integrated architecture rationale; evidence-bounded system claims; cross-layer change impact | S04, S09 | offline-proven |
| [26](modules/module-26-orchestration-comparison/README.md) | scenario architecture selection; hybrid orchestration envelope; risk/adaptivity decision matrix | S01, S02, S03, S04 | offline-proven |

Code/dated evidence anchors находятся в outlines. Offline PASS не доказывает fresh model quality;
historical observations не становятся текущими автоматически. Не расширять evidence до fully-live
six-role READY/merge, manager, semantic memory или Kubernetes. Статьи пересказываются своими словами
с attribution; registry не является списком уже проверенных claims будущих лекций.
