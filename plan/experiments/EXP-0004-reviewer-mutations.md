# EXP-0004 — Reviewer mutation evaluation

Date: 2026-09-12

## Hypothesis and protocol

A separate read-only Reviewer can approve the validated/QA-passed canonical Net Revenue candidate
and reject maintainability risks that preserve public semantics. Each run used the same scenario
version, full four-gate validator, immutable public semantic probe, two exact file reads, closed
Pydantic output, and a content-addressed configuration fingerprint. Large/raw model content was not
retained. Private run records are mode 0600 under `.scenario-state/runs/`.

## Results

`openai/gpt-5.6-luna` approved canonical and requested changes for 4/4 mutations: hard-coded
relation, wildcard/dead CTE, nondeterministic attribution, and misleading test intent. False
approval was `0/4`; canonical false rejection was `0/1`. The five runs used 13,895–15,201 tokens,
cost 1.227000–1.592700 ₽ each, and made exactly two read-only Reviewer calls.

`openai/gpt-5.4-nano` was cheaper in capability terms but rejected canonical in repeated attempts,
including after protocol clarification. `poolside/laguna-xs.2` failed the strict tool/schema
workflow closed. Current catalog reasoning-oriented alternatives worth future bounded comparison
are `arcee-ai/trinity-mini` (13.5/45 ₽ per 1M input/output tokens) and
`openai/gpt-oss-120b` (11.1/51 ₽); catalog metadata alone is not a capability guarantee.

## Conclusion

Use GPT-5.6 Luna for Reviewer until a cheaper candidate passes the same canonical plus mutation
gate. A single live pass is evidence for this configuration, not a general reliability claim.
