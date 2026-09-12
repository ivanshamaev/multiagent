# EXP-0002 — Autonomous Data Engineer live capability gates

Status: active

Date: 2026-09-12

## Hypothesis and fixed configuration

A cost-first GateLLM CHAT model that passes strict schema and forced tool-call probes can complete
the frozen Net Revenue scenario through the bounded MAF/MCP runtime. Baseline fingerprint:
`7dec9da8ca60…`; source: `a7efb5e594fa…`; data: `3823d7b57996…`. The worktree contains STEP-0009;
the successful probe/run configuration fingerprints are retained in private `.scenario-state/runs`.
Temperature was zero, output was capped at 2048 tokens, and prompts/raw responses/API credentials
were not retained.

## Runs and observations

- IBM Granite 4.0 H Micro passed strict schema but its forced tool call returned HTTP 404. This
  disproved treating structured-output support as tool support.
- Llama 3.1 8B passed both micro-gates. A prose-only completion consumed 3652 input and 169 output
  tokens (3821 total), cost approximately `0.058836` ₽, and correctly failed with zero tool evidence.
- After enabling normal tool mode, one run completed `clickhouse.list_databases`; invalid database
  calls were denied before execution. The terminal record retained three tool outcomes.
- A later run completed `dbt.parse` and `dbt.compile`, then GateLLM returned HTTP 400. A minimal
  independent `ping` dialogue reproduced success for two tool rounds and HTTP 400 on round three.
- A bounded search for an alternative schema+tool model encountered HTTP 429 and stopped; it did
  not bypass rate limiting or continue paid probing.
- The first phased run exposed parallel fan-out: 80 requested calls were contained by the gateway,
  with invalid no-`LIMIT` queries denied. Disabling parallel calls produced exactly one successful
  `TASK.md` read. Provider schema mode on the final tool-history request caused HTTP 400 and was
  removed while preserving local Pydantic validation. The next exact-one-read attempt reached that
  final boundary but stopped on HTTP 429, so no blind retry was made.

## Conclusion and follow-up

Schema, tool, policy, and full-dialogue reliability are distinct gates. The hypothesis is rejected
for a monolithic conversation on the current cheapest capable route. Fresh-conversation phases now
pass offline integration with cumulative evidence/usage. Resume the live candidate after rate-limit
recovery and only afterward begin the planned 10-run reliability sample.
