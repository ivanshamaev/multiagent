# PRB-0029 — Cheap model decorated an otherwise structured phase response

- Status: resolved
- Detected: 2026-09-12
- Scope: local validation of tool-phase final output

## Evidence and cause

After one successful bounded `TASK.md` read, Llama's investigation final consumed 8550 input and
1065 output tokens but failed JSON parsing. The run safely retained usage, cost (`0.153810` ₽),
latency and hashes without storing raw output. Tool-history requests cannot use GateLLM's provider
schema mode (PRB-0028), so smaller phase models alone cannot prevent Markdown/prose decoration.

## Fix

Try direct JSON first. If it fails, scan the response for schema-valid JSON objects and accept only
when exactly one object validates against the closed Pydantic model. Zero or multiple valid objects
remain a failure. Surrounding text never enters artifacts or prompts and raw output is not retained.

## Regression check

Unit tests accept one fenced object and reject two individually valid objects as ambiguous. All
field, enum, extra-field, and size constraints remain enforced by the same Pydantic model.
