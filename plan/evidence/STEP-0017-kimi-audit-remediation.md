# STEP-0017 evidence — Kimi audit remediation

Date: 2026-09-13

Status: PASS

## Finding disposition

| Findings | Disposition |
| --- | --- |
| F-01 | Already fixed by completed STEP-0015 evidence/progress/work log. |
| F-02 | Risk clarified and accepted in ADR-0026: HTTPX2 is Pydantic-maintained and an explicit OpenAI 3.8 dependency; exact version/hashes retained. |
| F-03 | Fixed: `.env` is 0600; `make bootstrap` now enforces mode without reading content. |
| F-04–F-07 | Fixed: PRB-0042, stale statuses, complete indexes and ADR supersession back-links. |
| F-08–F-09 | Confirmed; deferred as cohesive Phase J test-isolation/runtime-helper work. |
| F-10 | One real tuple mismatch fixed; broader validated-update refactor deferred to Phase J. |
| F-11 | Repository-local oracle visibility is accepted ADR-0013 design; narrower grader identity deferred to Phase J. |
| F-12–F-14 | Fixed: ClickHouse digest, contributor scope/commands, future-state observability wording. |
| F-15–F-16 | Stable governance invariants now executable; STEP-0001 evidence added. Historical prose/status normalization is intentionally non-destructive. |
| F-17–F-18 | Confirmed; hermetic imports/live markers belong to Phase J, coverage baseline to Phase K. |
| F-19 | Optimization-sensitive QA assert fixed; repair/error heuristics remain explicit Phase J debt. |
| F-20–F-21 | Confirmed mixed hardening/maintainability backlog for Phase J; no production credentials are in use. |
| F-22 | Not dead code: compatibility and smoke entry points are tested supported surfaces; deprecation requires usage evidence. |

Primary provenance checked: Pydantic's `github.com/pydantic/httpx2` project and OpenAI's
`openai-python/httpx2.md`, plus installed wheel metadata and `uv tree --invert --package httpx2`.

## Verification

| Command | Exit | Result |
| --- | ---: | --- |
| focused policy/workflow tests | 0 | 24 passed |
| `make bootstrap` | 0 | frozen environment checked; `.env` remained 0600 |
| `make check` | 0 | Ruff, format, 374 tests, plan lint, Compose PASS |
| `make scenario-repro-test` | 0 | matching source/data/baseline fingerprints |
| `make scenario-grade-baseline-test` | 0 | expected isolated `INCOMPLETE` boundary result |
| `make platform-test` | 0 | digest-pinned platform, Airflow/Cosmos, dbt 68/68 and SQL PASS |
| mode/secret/diff audit | 0 | `.env` 0600; no API token in Compose; no whitespace errors |

No LLM call was made. Larger findings are not marked fixed; their target phase remains explicit.
