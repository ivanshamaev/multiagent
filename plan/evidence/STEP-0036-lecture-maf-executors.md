# STEP-0036 evidence — лекция 05, MAF executors

Date: 2026-09-17

## Outcome

- `course/lectures/LECTURE-0005-maf-executors.md` опубликована с
  `LECTURE-0005.json` и `PUBLICATION-0005.json` receipts.
- Seven claims проверены по исходным Microsoft/LangChain статьям, текущему
  `runtime/role_pipeline.py`/`runtime/checkpoints.py`, тестам и датированному
  STEP-0019. Same-author editorial/technical/recheck отдельно выполнены;
  independent review не заявлен. Graph signature не выдан за реализованный hash.
- Candidate `build/course-step36-review-0005`: 90 files/10 diagrams.
  Browser desktop/360px mobile, light/dark, no-JS, keyboard zoom/pan/reset/
  fullscreen/Escape/focus, print, AX, CSP/subpath/links PASS; семь screenshots
  `output/playwright/step36/lecture-5/` просмотрены. Actual AT, hardware touch,
  paper/PDF и cross-browser не тестировались.

## Commands and results

```text
uv run pytest -q tests/workflow/test_role_pipeline.py tests/adversarial/test_role_pipeline_guards.py tests/integration/test_role_pipeline_recovery.py
# exit 0 — 11 passed

make course-check
# exit 0 — governance PASS

make course-build
# exit 0 — 90 files / 10 diagrams; SHA256 35d212d38188b5293a2f3b935909ccf41b4e5dfc00d107f50526f7841031b073

uv run python -m course.build --output build/course-step36-repeat
diff -qr build/course build/course-step36-repeat
# exit 0 — byte-identical

make check
# exit 0 — Ruff/format, 531 passed, plan/course governance, Compose config

git diff --check
# exit 0

curl http://127.0.0.1:8099/course/topic-0005.html
# HTTP 200
```

## Residual risk

STEP-0019 не тестирует нынешние branching/receipts/tracing в live сценарии.
Graph versioning требует отдельной проверки миграций при изменении топологии;
этот шаг не добавляет такую миграцию. Следующая — лекция 06.
