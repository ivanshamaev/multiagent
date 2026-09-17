# STEP-0035 evidence — лекция 04, состояние и память

Date: 2026-09-17

## Outcome

- Theory-only Markdown опубликован в `course/lectures/LECTURE-0004-state-memory.md`.
  Canonical manifest, syllabus, module outline и план согласованы по названию.
- Content receipt `course/reviews/LECTURE-0004.json`: separate same-author
  editorial/technical/recheck, восемь verified claims, одна исправленная minor
  finding (заголовок). S07 Anthropic, S03 Cognition, текущий код и датированное
  STEP-0019 использованы в их пределах; независимого review не было.
- Publication receipt `course/reviews/PUBLICATION-0004.json`: final candidate
  `build/course-step35-review-0004-final`, 88 files/9 diagrams. Playwright
  desktop/360px mobile, light/dark, no-JS, keyboard zoom/pan/reset/fullscreen,
  print, AX main/named SVG, CSP/subpath/links PASS. Семь screenshots в
  `output/playwright/step35/lecture-4/` просмотрены; после исправления
  заголовка browser gate повторён. Actual AT, hardware touch, cross-browser,
  paper/PDF не тестировались.

## Commands and results

```text
uv run pytest -q tests/unit/test_context.py tests/workflow/test_role_pipeline.py tests/adversarial/test_role_pipeline_guards.py tests/integration/test_role_pipeline_recovery.py
# exit 0 — 17 passed

make course-check
# exit 0 — governance PASS

uv run python -m course.build --candidate 4 --output build/course-step35-review-0004-final
# exit 0 — 88 files / 9 diagrams

make course-build
# exit 0 — 88 files / 9 diagrams, site SHA256 78f2877a55fb8deb71712d79a6e5fb391251ebb5742e1adc6998e65be015fae7

uv run python -m course.build --output build/course-step35-repeat
diff -qr build/course build/course-step35-repeat
# exit 0 — byte-identical

make check
# exit 0 — Ruff/format, 531 passed, plan/course governance and Compose config

git diff --check && make plan-check course-check
# exit 0

curl http://127.0.0.1:8099/course/topic-0004.html
# HTTP 200 (loopback preview)
```

## Residual risks and next step

Offline code/evidence не доказывают fully-live six-role READY или качество
нового model run; долговременная semantic memory не реализована.
Следующая по маршруту — лекция 05 о MAF executors и edges.
