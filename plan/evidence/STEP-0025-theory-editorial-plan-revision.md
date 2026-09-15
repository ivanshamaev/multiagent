# STEP-0025 — Theory-only and editorial requirements revision

Date: 2026-09-15

Status: planning PASS; scaffold and lectures not implemented

## Result

Revised STEP-0025 to deep theoretical lectures without labs/practical assignments, student setup,
grading or capstone submissions. Our implemented platform is an illustrative case, not student work.
The old 89-hour estimate is withdrawn; original planning evidence remains explicitly historical.
ADR-0034 supersedes ADR-0007 practice/grading requirements while preserving evidence provenance.

Listed available `technical-markdown-lectures`, preparation tool `skill-creator`, conditional
`openai-docs` and two explicitly unavailable planned editorial/fact-check skills. No new skills were
created/installed or claimed as applied. The available lecture skill informed structure and wording;
the user's deep-theory requirement overrides its default 101 depth.

Every future lecture requires post-writing full proofreading, source/claim verification, corrections
and recheck. Review records bind content hashes; missing/stale records or unresolved material issues
block reviewed. Separate author passes are not represented as independent review.

## Verification

- `make plan-check`: exit 0; PASS.
- `uv run pytest -q tests/policy/test_plan_governance.py`: exit 0; three PASS.
- STEP-0025 local Markdown link scan: no missing targets.
- `git diff --check`: exit 0.

No lectures, course scaffold, runtime changes, paid LLM calls or Docker operations were performed.
Next: implement the theory scaffold; prepare the planned editorial skills before lecture authoring.
