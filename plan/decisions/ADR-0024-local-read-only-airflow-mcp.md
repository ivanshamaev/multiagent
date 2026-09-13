# ADR-0024 — Local read-only Airflow MCP uses public API only

Status: accepted

Date: 2026-09-13

## Context

Phase I needs agent-readable orchestration state without granting UI automation, Airflow CLI,
metadata-database access, or mutation endpoints. The repository already validates Airflow 3.3.1 via
its stable public API, but that acceptance client uses admin credentials and intentionally performs
pause/trigger operations. It is not an appropriate agent capability.

## Decision

Create a repository-owned FastMCP stdio server that exposes only fixed read operations backed by
authenticated `GET /api/v2`: list/get DAGs, list/get DAG runs, list task instances, and get one
task-attempt log. The caller supplies only typed identifiers and bounded pagination/log parameters;
it cannot choose HTTP method, path, origin, headers, token, or body.

The MCP process receives an explicit loopback base URL and dedicated FAB Viewer credentials. It
obtains the JWT internally through `/auth/token`, keeps credentials/token out of repr and returned
content, and emits sanitized error classes/statuses. It never connects to PostgreSQL. Every path
component is percent-encoded and every successful JSON/text response is size-bounded.

The existing local policy gateway remains the primary authorization boundary. A new profile binds
the `airflow-observer` role to exact Airflow tools and exact local DAG IDs, then applies cumulative
call/time/output budgets and content-addressed evidence. Tool output is untrusted data and cannot
expand permissions. The server is a separate stdio process so auth state does not enter the Agent
Framework prompt or tool schema.

Write operations—including trigger, pause, clear, retry, backfill, pools, variables, connections,
configuration, and XCom values—are absent from contracts, policy, facade, and server registration.
The existing deterministic acceptance smoke retains its separate admin-only write path.

## Consequences

We own a small adapter and must regression-test it against the pinned Airflow OpenAPI schema. Viewer
permissions and log shape are verified on the live stack; there is no fallback to administrator.
Controlled dev-DAG trigger can be introduced only by a later ADR, separate role/profile, approval
gate, and idempotency policy.
