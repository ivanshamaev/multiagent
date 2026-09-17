# STEP-0039 evidence — лекция 08, изоляция среды исполнения

Date: 2026-09-17

## Outcome

- Theory-only текст опубликован в `course/lectures/LECTURE-0008-isolation.md`.
  Content/publication receipts: `LECTURE-0008.json`, `PUBLICATION-0008.json`.
- Claims сверены с оригинальными Anthropic S10/S27, Linux man-pages, текущим
  launcher/profiles/tests и датированным STEP-0022. Отдельные same-author
  editorial/technical/recheck выполнены; независимая рецензия не заявлена.
- Первый actual browser gate выявил misleading layout: host validation
  зрительно оказалась внутри sandbox subgraph. Схема исправлена, candidate
  заново собран и проверен; дефект записан в content receipt.
- Final candidate `build/course-step39-review-0008`: 96 files/13 diagrams.
  Desktop/360px mobile, light/dark, no-JS, keyboard zoom/pan/reset/fullscreen/
  Escape/focus, print, AX, CSP/subpath/links — PASS. Семь финальных screenshots
  в `output/playwright/step39/lecture-8/` просмотрены. Actual AT,
  hardware touch, paper/PDF и cross-browser не проверялись.

## Commands and results

```text
uv run pytest -q tests/unit/test_runner_isolation.py tests/integration/test_runner_namespace_isolation.py tests/adversarial/test_runner_isolation_guards.py
# exit 0 — 7 passed

make course-check
# exit 0 — governance PASS

make course-build
# exit 0 — 96 files / 13 diagrams; SHA256 c7d0667cc16a09f48947f0416496b891f5cdd79fc3c7121fb736f44264731c1a

uv run python -m course.build --output build/course-step39-repeat
diff -qr build/course build/course-step39-repeat
# exit 0 — byte-identical

make check
# exit 0 — Ruff/format, 531 passed, plan/course governance, Compose config

curl http://127.0.0.1:8099/course/topic-0008.html
# HTTP 200
```

## Residual risk

Namespace использует общее host kernel. Локальный тест одного внешнего
соединения не доказывает невозможность всех каналов egress. Security policy
и Kubernetes tenancy остаются за отдельными лекциями 19 и 26. Следующая
по teaching order — 09, MCP как интерфейс.
