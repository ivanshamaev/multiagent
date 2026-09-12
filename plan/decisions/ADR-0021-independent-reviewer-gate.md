# ADR-0021 — Independent Reviewer owns final approval

Status: accepted

Date: 2026-09-12

## Context

Validator proves deterministic gates and QA searches for semantic counterexamples, but neither owns final acceptance coverage, maintainability, or operational-risk approval. Letting DE or QA approve would collapse separation of duties; letting prose directly select `DONE` would bypass typed artifact and reducer gates.

## Decision

Reviewer is a third identity with a deny-by-default read-only profile. It starts only from `QA_PASSED` and receives the frozen specification, accepted QA report, and content-addressed reads of the candidate model and contract test. It cannot write, execute SQL/dbt/shell, access grader, secrets, or production, and cannot share identity with implementation or QA authors.

The model returns only criterion assessments, findings, risks, and a proposed decision. Code validates exact criterion coverage, creates IDs and evidence references, assembles `ReviewReport`, charges measured resources, and asks the reducer for `DONE`, `REWORK`, or `BLOCKED`. Approval requires every criterion PASS, successful evidence, and no HIGH/CRITICAL finding.

`REQUEST_CHANGES` consumes the shared rework budget. Only DE receives the accepted public report. Any repair invalidates prior validator and QA evidence, so the only return path is `DE → full validator → fresh QA → fresh Reviewer`. Hidden grader output never becomes feedback.

## Alternatives

- Merge QA and Reviewer — rejected because correctness and approval need separate identities and metrics.
- Use a style linter alone — rejected because acceptance rationale requires bounded judgment.
- Let Reviewer fix findings — rejected because approval and implementation authority conflict.
- Require zero findings — rejected because LOW/MEDIUM residual risks need not block approval.

## Consequences and validation

The workflow gains a final approval boundary and one measured model/tool cost. Tests must prove exact criterion coverage, identity separation, read-only enforcement, invalid-output closure, shared-budget exhaustion, and mandatory validator/QA reruns. Mutation evaluation reports false approval separately from QA false pass.
