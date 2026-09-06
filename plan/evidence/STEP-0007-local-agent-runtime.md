# STEP-0007 — Local Agent Runtime Evidence

Date: 2026-09-06

Status: PASS

## Verified result

The local Python 3.12 runtime uses pinned MAF core 1.17.0, MAF OpenAI adapter 1.14.2, OpenAI SDK
3.8.0 and GateLLM Chat Completions. `API_TOKEN` is loaded only as a non-serializable `SecretStr`;
the endpoint is fixed to HTTPS GateLLM, retries/timeouts/output are bounded, and no LLM setting is
passed to Data Platform containers.

A MAF graph executor receives content-addressed context only after disposable workspace
verification. The PM role returns a strict `SpecificationDraft`; workflow-owned IDs/timestamps are
added in code, and only the STEP-0006 reducer may accept the artifact or charge its measured usage.
The live result contained two verified hash-chained events and no prompt or raw response.

## Commands and outcomes

- Targeted Ruff and runtime/provider/context/workflow/policy pytest — exit `0`; 27 checks passed
  before the structured capability extension, then 19 affected checks passed.
- `LLM_DEFAULT_MODEL=meta-llama/llama-3.1-8b-instruct make llm-smoke` — exit `0`; schema probe
  HTTP 200, controlled result contract-valid, state `blocked`, 1415 full-call tokens, 3710 ms.
  Request/response hashes start `b8ea47cefbeb`/`58fe4a060173`; measured probe plus run cost was
  approximately 0.02583 ₽. Raw content was not persisted.
- `make scenario-repro-test && make scenario-grade-baseline-test` — exit `0`; baseline
  `53bf4b7d…`, source `798def11…`, data `3823d7b5…`; grader returned expected `INCOMPLETE`.
- `make platform-test` — exit `0`; Airflow run
  `api_smoke_20260906T071510813594Z_5fc409df` passed 11/11 tasks; dbt 68/68 and independent
  ClickHouse checks passed.
- Final `make check && git diff --check` — exit `0`; Ruff PASS, 47 files formatted, 129 pytest
  checks PASS, Compose configuration valid, no whitespace errors.

## Failures and residual risks

PRB-0013–0016 preserve SDK, catalog and model failures. EXP-0001 records the cost-ordered model
comparison: catalog/routing alone did not predict structured quality. One valid run is a plumbing
gate, not a quality benchmark. Events remain in memory; invalid-response usage is not yet a durable
workflow failure event. The agent has no platform tools, file writer or network capability, which
is intentionally deferred to STEP-0008.
