# PRB-0026 — GateLLM route rejects the third tool-dialogue round

- Status: closed; accepted upstream limitation with phased execution implemented
- Detected: 2026-09-12
- Scope: `meta-llama/llama-3.1-8b-instruct` through GateLLM Chat Completions

## Reproduction and evidence

A live Data Engineer attempt completed two successful dbt calls, then the next provider request
returned HTTP 400. A minimal direct API reproduction used only a harmless forced `ping`: rounds
one and two returned valid tool calls; round three returned HTTP 400 with the provider message
`Provider returned error`. This excludes MCP, workspace policy, dbt output, and task prompt as the
cause. Prompts and raw completions were not retained.

## Impact and next decision

A single MAF auto-invocation conversation cannot safely implement a task that requires more than
two sequential observe/act rounds on this route. Increasing local tool/retry budgets cannot fix an
upstream deterministic 400 and would waste tokens.

Split the role into bounded fresh conversations with code-owned phase transitions: investigation,
implementation, then deterministic validation. Each phase must preserve measured usage and tool
evidence; no phase may infer success from a model claim. Keep the one-conversation path covered for
providers that support it, but do not retry this failure blindly.

## Regression check

Add a fake-provider workflow test proving phase continuation uses a fresh model call and cumulative
budgets. Re-run the minimal live scenario only after that implementation or a provider route change.
