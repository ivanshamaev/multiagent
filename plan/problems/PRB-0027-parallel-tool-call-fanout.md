# PRB-0027 — Required tool mode produced an oversized parallel batch

- Status: resolved
- Detected: 2026-09-12
- Scope: phased GateLLM/MAF Data Engineer execution

## Reproduction

The first phased live investigation asked Llama 3.1 8B for a required read/query action. The model
returned one batch containing 80 repeated calls, including five SQL queries without the mandatory
top-level `LIMIT`. The deterministic gateway denied those queries and enforced its cumulative
budget, but MAF attempted the full batch because its `max_function_calls` check is documented as
best effort after a parallel batch completes.

## Cause and fix

`tool_choice=required` guaranteed some tool use but did not cap parallel fan-out. Set
`parallel_tool_calls=false` for required first-round calls, expose exactly one investigation tool,
require the exact `TASK.md` read, and cap the live profile at six cumulative calls. Each of the
three current phases must add exactly one evidence record; any fan-out fails closed.

## Regression check

The provider unit test requires `tool_choice=required`, `parallel_tool_calls=false`, and final
schema enforcement together. The phased integration test proves exactly three cumulative calls.
