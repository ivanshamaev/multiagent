# PRB-0023 — structured-output capability did not imply tool calling

Status: closed
Detected: 2026-09-12
Resolved: 2026-09-12

## Symptom and reproduction

`ibm-granite/granite-4.0-h-micro` passed the strict JSON schema probe, but the first full Data
Engineer run failed before any tool evidence or workspace change. A minimal forced `ping` request
with OpenAI-compatible `tools` returned HTTP 404.

## Root cause

Model selection validated structured output only. The autonomous Data Engineer requires both
strict structured final output and function calling; catalog category `CHAT` proves neither.

## Accepted fix

Add a minimal forced-tool probe and require both gates before constructing the expensive MAF
workflow. Candidate-level 400/404 or malformed 2xx responses mark tool calling unavailable;
authentication, balance, rate-limit, server, and transport failures remain fatal.

## Regression check

Fake transport covers a valid tool call with usage, HTTP 404, malformed HTTP 200, and fatal
401/402/429/500 responses. Live microprobes confirmed Granite unavailable and
`meta-llama/llama-3.1-8b-instruct` available for tool calling.
