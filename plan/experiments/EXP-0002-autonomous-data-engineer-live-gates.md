# EXP-0002 — Autonomous Data Engineer live capability gates

Status: complete

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
- The live catalog contained `CHAT`, `VISION`, and `IMAGE_GENERATION`, but no separate reasoning
  category. Explicitly requested VISION routes were admitted only after schema and tool probes;
  automatic cost-first selection remained CHAT-only. GPT-5.4 Nano and GPT-5.6 Luna passed both
  gates. DeepSeek V4 Flash and several cheaper reasoning routes returned HTTP 200 but failed the
  strict schema gate.
- GPT-5.4 Nano attempts exposed a singular-test semicolon defect, repeated-context token pressure,
  and one self-blocked semantically invalid candidate. Safe run records measured up to 29 455
  tokens and `2.413050` ₽ without accepting a false success.
- After bounded head+tail validator feedback, target-aware repair routing, and phase-specific
  context reduction, GPT-5.6 Luna completed a fresh candidate without repair: 17 370 tokens,
  `1.946100` ₽, 34 209 ms model latency, 3 model calls, and 3 tool calls. All four independent
  validator gates and all five isolated hidden-grader checks passed.

## Conclusion and follow-up

Schema, tool, policy, and full-dialogue reliability are distinct gates. The hypothesis is rejected
for a monolithic conversation and for Llama 3.1 8B as the current DE route. GPT-5.6 Luna is the
selected cost-effective DE model; GPT-5.4 Nano remains a compatible but less reliable fallback.
The fixed sample produced 8/10 public and 7/10 end-to-end hidden passes. After raising the
internally inconsistent 30k ceiling to 42k, a post-fix run passed public and hidden gates after one
repair. Full measurements are retained in `plan/evidence/STEP-0009-reliability-sample.md`.
