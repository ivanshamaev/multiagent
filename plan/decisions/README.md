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
