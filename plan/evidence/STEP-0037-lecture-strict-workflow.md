# STEP-0037 evidence — лекция 06, жёсткий workflow

Date: 2026-09-17

## Outcome

- Theory-only лекция опубликована в `course/lectures/LECTURE-0006-strict-workflow.md`.
  Content/publication receipts: `LECTURE-0006.json` и `PUBLICATION-0006.json`.
- Восемь claims проверены по оригинальным Anthropic/LangChain статьям, текущим
  transition/state/role графам и тестам; STEP-0020 — датированное offline v2
  evidence, не нынешний live v3. Same-author editorial/technical/recheck
  отдельно выполнены, independent review не заявлен.
- Candidate `build/course-step37-review-0006`: 92 files/11 diagrams.
  Desktop/360px mobile, light/dark, no-JS, keyboard zoom/pan/reset/fullscreen/
  Escape/focus, print, AX, CSP/subpath/links PASS. Семь screenshots в
  `output/playwright/step37/lecture-6/` просмотрены; реальное AT, hardware
  touch, paper/PDF и cross-browser не тестировались.

## Commands and results

```text
uv run pytest -q tests/workflow/test_state_machine.py tests/workflow/test_role_pipeline.py tests/adversarial/test_workflow_guards.py
# exit 0 — 30 passed

make course-check
# exit 0 — governance PASS

make course-build
# exit 0 — 92 files / 11 diagrams; SHA256 1766d617d13d19b1468f5dba83d22647ceffd10af771ba7e3f486886bc5b42e5

uv run python -m course.build --output build/course-step37-repeat
diff -qr build/course build/course-step37-repeat
# exit 0 — byte-identical

make check
# exit 0 — Ruff/format, 531 passed, plan/course governance, Compose config

git diff --check
# exit 0

curl http://127.0.0.1:8099/course/topic-0006.html
# HTTP 200
```

## Residual risk

Bounded rework alone не гарантирует liveness при зависшем внешнем вызове;
изолированные проверки не доказывают fully-live READY и качества LLM.
Следующая — лекция 07 об agent-orchestrator.
