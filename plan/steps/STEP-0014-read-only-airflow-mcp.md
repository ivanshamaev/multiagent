# STEP-0014 — Read-only Airflow MCP over `/api/v2`

Status: in progress

Date: 2026-09-13

## Goal

Start Phase I with an auditable, read-only Airflow tool boundary. A local stdio MCP server must use
only the stable Airflow 3 `/api/v2` API and expose bounded DAG, run, task-instance, and log metadata
through the existing deny-by-default policy/evidence layer.

## Scope

- Add strict Airflow tool contracts for DAG listing/details, run listing/details, task instances,
  and one task-attempt log.
- Add an `airflow-observer-v1` capability profile with exact tools, local DAG IDs, pagination,
  wall-time, call-count, and output-byte limits.
- Implement a local FastMCP stdio server backed by authenticated `GET /api/v2`; credentials and JWT
  remain process-private and never enter model arguments, output, evidence, or logs.
- Connect the server through `MCPStdioTool`, the deterministic gateway, and a role-bound MAF facade.
- Provision a dedicated local FAB `Viewer` identity rather than reuse the admin identity.
- Add an opt-in live smoke that reads the Cosmos DAG, recent runs, task instances, and a bounded log
  without changing DAG or run state.

## Non-goals

- DAG trigger, pause/unpause, clear, retry, backfill, config mutation, variable/connection access,
  XCom values, direct metadata DB access, production Airflow, or autonomous diagnosis by an LLM.
- Replacing the existing write-capable deterministic Airflow acceptance smoke.
- General URL fetching or model-selected API paths/query parameters.

## Implementation sequence

1. Record transport, authentication, endpoint, and permission decisions in ADR-0024.
2. Inspect the running pinned Airflow 3.3.1 OpenAPI document and lock exact paths/response shapes.
3. Add contracts and extend pure policy with DAG allowlist checks.
4. Implement the bounded API client and FastMCP tools; sanitize errors and cap response bytes before
   returning data to the MCP client.
5. Add stdio client, gateway routing, Airflow-only facade, evidence retention, and Viewer bootstrap.
6. Add unit, policy, integration, and adversarial tests for path encoding, auth secrecy, wrong role,
   unknown DAG/tool, write-shaped requests, pagination/output budgets, invalid JSON, and poisoning.
7. Run offline gates, live read-only smoke, complete platform regressions, persist evidence, and stop
   containers without deleting named volumes.

## Acceptance criteria

- Every exposed operation maps to one fixed `GET /api/v2` path; callers cannot supply methods,
  arbitrary URLs, headers, auth data, or request bodies.
- The MCP role cannot trigger, pause, clear, retry, mutate configuration, read connections/variables,
  query PostgreSQL, or access DAG IDs absent from its exact allowlist.
- Inputs are closed/versioned and bounded; identifiers are URL-encoded; page size, log attempt, map
  index, response bytes, calls, and elapsed time are code-enforced.
- Authentication uses a dedicated Viewer identity and short-lived JWT. Secret values are redacted
  from exceptions, retained evidence, CLI output, and MCP/model-visible content.
- Successful and denied calls produce same-task typed evidence through the existing gateway.
- Live smoke reads the Cosmos DAG and a real completed run/task/log through MCP while before/after
  pause/run metadata remain unchanged.
- `make check`, MCP/scenario/platform regression gates and `git diff --check` pass; Docker services
  are stopped with volumes preserved.

## Risks and mitigations

- **API drift:** pin Airflow image and verify exact operations against its served OpenAPI document.
- **Viewer permission mismatch:** test the dedicated identity live; do not silently fall back to admin.
- **Log leakage/size:** one explicit task attempt only, strict byte cap, no XCom/config/connection API.
- **URL injection:** contracts reject unsafe identifiers and the adapter percent-encodes every path
  component; no raw path is accepted.
- **Read endpoint side effects:** fixed GET-only dispatcher and before/after live state comparison.
- **MCP output poisoning:** output remains untrusted evidence; policy cannot be modified by content.

## Planned verification

```bash
uv run pytest -q tests/unit/test_airflow_mcp.py tests/unit/test_tool_contracts.py
uv run pytest -q tests/policy/test_airflow_profile.py tests/adversarial/test_airflow_mcp_guards.py
make airflow-mcp-smoke
make check
make mcp-smoke
make scenario-repro-test
make scenario-grade-baseline-test
make platform-test
git diff --check
make platform-down
```

