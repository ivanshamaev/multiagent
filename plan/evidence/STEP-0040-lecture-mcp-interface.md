# STEP-0040 evidence — лекция 09, MCP как интерфейс

Date: 2026-09-17

## Outcome

- Theory-only текст: `course/lectures/LECTURE-0009-mcp-interface.md`.
  Content/publication receipts: `course/reviews/LECTURE-0009.json` и
  `course/reviews/PUBLICATION-0009.json`. Рецензирование выполнено автором
  отдельными проходами; независимый reviewer не заявлен.
- Оригинальные статьи Anthropic S11/S08, нормативные MCP architecture,
  versioning, transports и tools для 2026-07-28, текущий код gateway/stdio,
  SDK constant и датированный STEP-0008 сверены. Нормативный lifecycle
  2026-07-28 отделён от локального `mcp==1.26.0`, объявляющего 2025-11-25;
  live negotiation и совместимость новых функций не заявлены.
- Первая схема в браузере наложила подписи стрелок. Sequence diagram
  заменила её; затем устранена Mermaid parse error из-за `;` в сообщении.
  Финальная версия перечитана и перерендерена.
- Candidate `build/course-step40-review-0009`: 98 files / 14 diagrams.
  Desktop/360px mobile, light/dark, no-JS, keyboard/fullscreen focus, print,
  AX, CSP/subpath/links — PASS. Семь финальных screenshots в
  `output/playwright/step40/lecture-9/` просмотрены: кириллица, направления
  стрелок, ветви DENY/ALLOW, mobile scroll и print читаемы. Реальное AT,
  hardware touch, бумажная/PDF-печать и cross-browser не проверены.

## Commands and results

```text
uv run pytest -q tests/unit/test_mcp_gateway.py tests/unit/test_mcp_stdio.py tests/policy/test_mcp_boundary.py
# exit 0 — 19 passed

make course-check
# exit 0 — governance PASS

make course-build
# exit 0 — 98 files / 14 diagrams; final site SHA256 below

uv run python -m course.build --output build/course-step40-repeat
diff -qr build/course build/course-step40-repeat
# exit 0 — byte-identical

make check
# exit 0 — Ruff/format, 531 passed, plan/course governance, Compose config

git diff --check
uv run python -m policies.plan_governance
# exit 0 — both

curl http://127.0.0.1:8099/course/
curl http://127.0.0.1:8099/course/topic-0009.html
# HTTP 200 for both
```

Final full-site SHA256: `ccfc6a795cc1e5dda051d1ce6e914114bb039b85d7a141a49c7eaf3731ad2f0a`.

## Residual risk

Browser AX inspection не является проверкой скринридером. Dated STEP-0008
и 19 профильных тестов доказывают только заявленные локальные границы,
не MCP 2026 interoperability и не качество модели. OAuth/security threat
model остаются за лекцией 19, SQL scope — за следующей лекцией 10.
