# PRB-0025 — Tool argument error aborted the live attempt without a run record

- Status: resolved
- Detected: 2026-09-12
- Scope: GateLLM/MAF Data Engineer live execution

## Reproduction

Run `uv run python -m runtime.data_engineer_live --scenario net-revenue
--model meta-llama/llama-3.1-8b-instruct`. The model completed `dbt_parse`, then
submitted schema-invalid arguments to another tool. MAF stopped after the first
function error and the CLI returned `ModelInvocationError`; no terminal run record
was retained.

## Cause and decision

The function loop allowed only one consecutive tool error. The live runner also
persisted only domain-level `AutonomousExecutionError`, although provider and
framework failures are valid terminal outcomes.

Allow at most three consecutive errors and return only the facade's sanitized
error detail to the model so it can correct its call. State the actual `raw` and
`analytics` database allowlist and the expected tool sequence in the trusted role
instructions. Persist a redacted terminal record for every exception after a
workflow ID exists. Unknown model usage is recorded as unavailable, never guessed;
the already-sanitized provider fingerprint is retained for diagnosis.

## Regression check

`tests/unit/test_model_provider.py` locks the bounded MAF configuration. Live
reproduction must either recover or retain `agent_cycle_ModelInvocationError`
with completed tool-call metadata.
