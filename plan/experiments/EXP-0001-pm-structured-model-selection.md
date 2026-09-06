# EXP-0001 — PM structured model selection

Status: complete

Date: 2026-09-06

## Hypothesis and fixed configuration

The cheapest catalog model that passes a minimal live schema gate can produce a contract-valid PM
specification without crossing the deterministic workflow boundary. Scenario `net-revenue` used
baseline `53bf4b7d8196…`, source `798def11300f…`, and data `3823d7b57996…`. Code revision was
`0574a7d4a448` plus the uncommitted STEP-0007 worktree. The trusted prompt was
`agents/pm/instructions.md`, SHA-256 `15d5efb48aa480556a7bb70f868311f0ad1a16a8a2064ff1dc6762afb49ddec5`.

Provider: GateLLM Chat Completions through MAF core 1.17.0/OpenAI adapter 1.14.2 and OpenAI SDK
3.8.0. Full calls used temperature `0`, `max_tokens=512`, 30-second client timeout and one SDK
retry. Prompts and raw responses were deliberately not stored.

## Runs and observations

Five full attempts and one probe-only candidate were observed during adapter stabilization.
Mistral Nemo first produced a valid blocked artifact, then two later runs ended in HTTP 504. Ling
3.0 failed the strict schema probe. IBM Granite Micro passed the probe but its full payload failed
Pydantic validation. Llama 3.1 8B passed: 992 input + 423 output tokens, 3710 ms, two valid events,
terminal state `blocked`, request hash `b8ea47cefbeb…`, response hash `58fe4a060173…`. Its probe used
42 + 7 tokens. At catalog prices 15/24 ₽ per million tokens, the measured successful run including
probe cost approximately **0.02583 ₽**.

## Conclusion and follow-up

The runtime, schema validation, fail-closed model comparison, usage capture, and reducer boundary
are proven for one live run. The hypothesis is only partially supported: cheap route availability
did not predict full structured reliability. Llama 3.1 8B is the dated PM default, not a general
winner. Repeat-run quality evaluation is deferred until the agent has controlled data-platform
tools; invalid-response usage must become durable failure telemetry before reliability work closes.
