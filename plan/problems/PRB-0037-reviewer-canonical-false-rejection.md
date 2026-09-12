# PRB-0037 — Reviewer canonical false rejection

Status: resolved

Date: 2026-09-12

## Symptom and reproduction

`make reviewer-live REVIEW_MUTATION=canonical REVIEW_MODEL=openai/gpt-5.4-nano` completed the full
validator, immutable QA semantic probe, and two Reviewer reads, but did not approve the known-good
candidate. Five private records under `.scenario-state/runs/qa-reviewer-...canonical...json` retain
safe usage and decision metadata; no prompts or raw responses are persisted.

## Root cause and accepted fix

The two fresh phases discarded positive model observations, and the decision phase treated the one
singular contract test as the sole correctness oracle. `ReviewerInspectionDraft` now preserves
bounded positive observations. Instructions explicitly distinguish accepted validator/QA
correctness from the singular test's narrower fields/grain/identity scope.

GPT-5.4 Nano still produced false rejection after clarification, so it is not selected for this
role. GPT-5.6 Luna passed canonical and all four mutation gates. No candidate test, validator,
grader, or acceptance criterion was weakened.

## Regression check

Offline tests require the fresh two-read protocol, exact criterion coverage, invalid-output
closure, identity separation, shared rework bounds, and a complete validator/QA/Reviewer rerun.
The live experiment is recorded in `plan/experiments/EXP-0004-reviewer-mutations.md`.
