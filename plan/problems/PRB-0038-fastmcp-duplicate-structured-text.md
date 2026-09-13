# PRB-0038 — FastMCP duplicated string output as structured text

Status: resolved

Date: 2026-09-13

## Reproduction

The first `make airflow-mcp-smoke` completed the Airflow acceptance run but failed while decoding
the first observer result. A direct safe shape probe showed two text blocks joined by the gateway:
the intended JSON document and a second generated `{"result": "..."}` structured representation.
`json.loads` therefore raised `Extra data` at line 2.

## Cause

FastMCP 1.26 inferred structured output from the annotated `str` return and emitted both legacy text
content and generated structured content. The shared gateway correctly retained all returned text;
silently discarding a block there would weaken handling for other MCP servers.

## Fix and regression

All six repository-owned Airflow tools explicitly set `structured_output=False`, because their
return is already canonical bounded JSON text. The second `make airflow-mcp-smoke` passed with eight
calls, eight evidence records, three allowlisted DAGs, 11 successful task instances, a log hash, and
identical before/after DAG/run metadata. The shared gateway remains unchanged.
