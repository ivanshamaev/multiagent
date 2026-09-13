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
