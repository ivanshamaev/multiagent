# PRB-0034 — QA probe output failed closed JSON validation

- Status: resolved
- Detected: 2026-09-12
- Scope: live GPT-5.6 Luna QA probe phase

## Reproduction and cause

The canonical candidate passed real public validation, and QA inspection completed one authorized
workspace read. The fresh probe conversation then raised `ModelOutputValidationError` with
`json_invalid`. Its 1024-token output cap was lower than the already measured small-model phase
envelope. The error carried safe usage/hashes, but `AutonomousQAError` retained only the earlier
successful invocation, making cost telemetry incomplete.

## Fix

Keep the same one-call/one-tool limits and local closed Pydantic validation, but use the established
2048-token phase cap. When local validation fails, append the exception's `ModelCallRecord` to safe
QA telemetry. Raw response, prompt, credentials, and provider body remain excluded.

## Regression check

Unit coverage asserts that a probe `ModelOutputValidationError` contributes its usage and hashes to
the typed QA failure while no unvalidated draft enters a `QAReport`. A repeated canonical live run
must produce a schema-valid decision or remain fail-closed.

## Follow-up boundary hardening

Two later live attempts exposed different, fail-closed integration faults: model-authored probe SQL
used invalid aggregate aliases, and insignificant whitespace changed the expected query hash. The
probe is now a no-argument QA tool whose implementation invokes the exact code-owned SQL; the
gateway still records and verifies the underlying `clickhouse.run_query` argument hash. This
removes SQL generation and byte-for-byte reproduction from the model's authority.
