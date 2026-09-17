# STEP-0038 evidence — лекция 07, agent-orchestrator

Date: 2026-09-17

## Outcome

- Theory-only текст опубликован в `course/lectures/LECTURE-0007-agent-orchestrator.md`.
  Content/publication receipts: `LECTURE-0007.json`, `PUBLICATION-0007.json`.
- Claims сверены с оригиналами Microsoft Research, Anthropic, официальной A2A
  specification, текущим role graph и ADR-0035. Manager-flow помечен как
  **не реализованный** в нашей платформе. Same-author editorial/technical/
  recheck выполнены отдельно; независимая рецензия не заявлена.
- Candidate `build/course-step38-review-0007`: 94 files/12 diagrams.
  Browser на desktop/360px mobile, light/dark, no-JS, keyboard zoom/pan/reset,
  fullscreen/Escape/focus, print, AX, CSP/subpath/links — PASS. Семь screenshots
  в `output/playwright/step38/lecture-7/` просмотрены. Фактическое AT,
  hardware touch, paper/PDF и cross-browser не проверялись.

## Commands and results

```text
uv run pytest -q tests/workflow/test_role_pipeline.py tests/policy/test_course_governance.py
# exit 0 — 46 passed

make course-check
# exit 0 — governance PASS

make course-build
# exit 0 — 94 files / 12 diagrams; SHA256 749cb750ab5f18c71d5746760459b44fcad887206f9ca328020cd579abc470a2

uv run python -m course.build --output build/course-step38-repeat
diff -qr build/course build/course-step38-repeat
# exit 0 — byte-identical

make check
# exit 0 — Ruff/format, 531 passed, plan/course governance, Compose config

git diff --check
# exit 0

curl http://127.0.0.1:8099/course/topic-0007.html
# HTTP 200
```

## Residual risk

Schema investigation manager — мысленный сценарий, не runtime capability.
Источники из research-setting не доказывают качество нашего DE pipeline.
Следующая лекция 08 — изоляция среды исполнения.
