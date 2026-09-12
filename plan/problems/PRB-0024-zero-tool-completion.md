# PRB-0024 — zero-tool completion escaped as an untyped runtime error

Status: closed
Detected: 2026-09-12
Resolved: 2026-09-12

## Symptom and reproduction

The first tool-capable Llama Data Engineer run returned a structured draft without invoking tools.
No evidence or workspace change existed, and the workflow escaped with `TypeError` rather than a
classified attempt result.

## Root cause

The executor computed the artifact timestamp with the one-argument form of `max()` when the tool
evidence tuple was empty. That form expects an iterable. The zero-tool case also lacked a persistent
failure record even though model usage was available.

## Accepted fix

Reject an empty evidence stream before artifact assembly using `AutonomousExecutionError` carrying
only safe model metadata and tool evidence. The live boundary persists a private redacted
`run_failed` record with usage, hashes, latency, cost, and a stable error code.

## Regression check

An offline model returns a valid `DataEngineerDraft` without tools. The MAF workflow must raise the
typed failure with 20 measured tokens and no evidence; the workspace is reset afterward.
