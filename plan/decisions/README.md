# Архитектурные решения

ADR именуются `ADR-NNNN-short-name.md` и содержат status, context, decision, alternatives, consequences и validation. Принятое решение не редактируется для изменения смысла: создаётся новое ADR с полями `Supersedes`/`Superseded by`.

| ADR | Решение | Status |
| --- | --- | --- |
| [ADR-0001](ADR-0001-hybrid-runtime.md) | Local agent runtime + Docker Data Platform | accepted |
| [ADR-0002](ADR-0002-deterministic-control-plane.md) | Deterministic control plane | accepted |
| [ADR-0003](ADR-0003-artifact-handoffs.md) | Typed artifact handoffs | accepted |
| [ADR-0004](ADR-0004-data-platform-stack.md) | ClickHouse, dbt, Airflow, PostgreSQL | accepted |
| [ADR-0005](ADR-0005-evidence-first-validation.md) | Evidence-first validation | accepted |
| [ADR-0006](ADR-0006-deny-by-default.md) | Deny-by-default capabilities | accepted |
| [ADR-0007](ADR-0007-evidence-based-course.md) | Курс строится после проверенной системы | accepted |
| [ADR-0008](ADR-0008-gatellm-gateway.md) | GateLLM и cost-first model policy | accepted |
| [ADR-0009](ADR-0009-airflow-local-topology.md) | LocalExecutor, FAB auth и public Airflow API boundary | accepted |
| [ADR-0010](ADR-0010-airflow-isolated-dbt.md) | Изолированный dbt venv внутри Airflow Docker image | accepted |
| [ADR-0011](ADR-0011-use-astronomer-cosmos.md) | Astronomer Cosmos управляет dbt-графом и выполнением | accepted |
| [ADR-0012](ADR-0012-disposable-scenario-snapshots.md) | Allowlisted content snapshot создаёт disposable workspace | accepted |
| [ADR-0013](ADR-0013-isolated-hidden-grader.md) | Hidden grader работает в отдельном capability boundary | accepted |
| [ADR-0014](ADR-0014-domain-contracts-and-workflow-events.md) | Strict domain contracts, pure reducer и hash-chained events | accepted |
| [ADR-0015](ADR-0015-gatellm-maf-adapter-boundary.md) | GateLLM provider и MAF adapter boundary | accepted |
| [ADR-0016](ADR-0016-isolated-official-mcp-servers.md) | Official MCP servers in isolated stdio processes behind local policy | accepted |
| [ADR-0017](ADR-0017-clickhouse-query-ast-gate.md) | Strict SQL AST preflight as defense in depth | accepted |
| [ADR-0018](ADR-0018-autonomous-de-control-plane-ownership.md) | Human spec, unified tool ledger and independent validator ownership | accepted |
| [ADR-0019](ADR-0019-phased-agent-conversations.md) | Fresh least-privilege phases with cumulative evidence and usage | accepted |
| [ADR-0020](ADR-0020-independent-qa-boundary.md) | Independent read-only QA and evidence-owned rework gate | accepted |
| [ADR-0021](ADR-0021-independent-reviewer-gate.md) | Reviewer is the sole independent approval gate | accepted |
| [ADR-0022](ADR-0022-pre-pm-requirements-discovery.md) | Analyst discovery precedes PM specification | accepted |
| [ADR-0023](ADR-0023-pm-consumes-only-accepted-requirements.md) | PM consumes only accepted requirements handoff | accepted |
| [ADR-0024](ADR-0024-local-read-only-airflow-mcp.md) | Local read-only Airflow MCP uses public API only | accepted |
| [ADR-0025](ADR-0025-separate-approved-idempotent-airflow-trigger.md) | Separate approved and idempotent dev-DAG trigger | accepted |
| [ADR-0026](ADR-0026-accept-upstream-httpx2.md) | Accept pinned upstream HTTPX2 dependency | accepted |
| [ADR-0027](ADR-0027-maf-native-hardened-checkpoints.md) | MAF-native checkpoints behind hardened local storage | accepted |
| [ADR-0028](ADR-0028-typed-json-role-checkpoint-boundaries.md) | Typed JSON boundaries between checkpointable role executors | accepted |
| [ADR-0029](ADR-0029-stage-routing-and-role-receipts.md) | Code-owned stage routing and durable role receipts | accepted |
| [ADR-0030](ADR-0030-explicit-safe-otel-instrumentation.md) | Explicit safe OpenTelemetry instrumentation | accepted |
| [ADR-0031](ADR-0031-bubblewrap-runners-and-local-mcp-auth.md) | Bubblewrap role runners and local MCP authentication | accepted |
| [ADR-0032](ADR-0032-local-otel-operational-stack.md) | Local OpenTelemetry operational stack | accepted |
| [ADR-0033](ADR-0033-two-layer-evaluation-benchmark.md) | Repeated offline regression plus provenanced live evaluation | accepted |
| [ADR-0034](ADR-0034-theory-course-and-editorial-gates.md) | Theory-only course and mandatory per-lecture editorial verification | accepted |
| [ADR-0035](ADR-0035-dual-orchestration-lecture-boundaries.md) | Dual orchestration theory and non-overlapping lecture plans | accepted |
| [ADR-0036](ADR-0036-markdown-diagrams-static-svg.md) | Markdown diagram sources and build-time SVG for static HTML | accepted |
| [ADR-0037](ADR-0037-local-static-course-prototype.md) | Locked Mermaid renderer and local static course prototype | accepted |
| [ADR-0038](ADR-0038-course-landing-roadmap-reader-design.md) | Cyberpunk landing, SVG roadmap and course/lecture side navigation | accepted |
| [ADR-0039](ADR-0039-per-lecture-publication-receipts.md) | Per-lecture publication receipts and isolated review candidates | accepted |
