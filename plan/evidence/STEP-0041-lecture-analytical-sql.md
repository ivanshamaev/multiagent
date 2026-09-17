# STEP-0041 evidence — лекция 10, ограниченный аналитический SQL

Date: 2026-09-17

## Outcome и provenance

- Theory-only текст опубликован в `course/lectures/LECTURE-0010-analytical-sql.md`.
  Content/publication receipts: `course/reviews/LECTURE-0010.json` и
  `course/reviews/PUBLICATION-0010.json`. Автор провёл отдельные editorial,
  technical, recheck и browser passes; независимый reviewer не заявлен.
- Идеи специализированного tool и materialized analytical result сверены с
  оригинальными Anthropic S08 и ClickHouse S16. Документация ClickHouse
  `url()` подтверждает внешний источник внутри `SELECT`. Точные локальные
  claims сверены с `policies/tool_policy.py`, профилями Analyst/DE,
  `runtime/analyst.py`, MCP gateway, Compose, SQL grants и STEP-0008.
  Защита от всех SQL обходов, privacy policy и server CPU/memory bounds
  не заявлены как реализованные.
- Первый actual browser gate обнаружил, что TD-схема на mobile начинается
  за видимой областью. После смены на LR новая candidate-сборка проверена
  целиком: desktop/360px mobile, light/dark, no-JS, keyboard/fullscreen
  focus, print, AX, CSP/subpath/links — PASS. Все семь финальных screenshots
  в `output/playwright/step41/lecture-10/` осмотрены; стрелки DENY/error,
  кириллица, начальный узел и печатная схема читаемы.

## Команды и результат

```text
uv run pytest -q tests/policy/test_tool_policy.py tests/adversarial/test_tool_policy_guards.py tests/unit/test_mcp_gateway.py
# exit 0 — 53 passed

make course-check
# exit 0 — governance PASS

uv run python -m course.build --candidate 10 --output build/course-step41-review-0010
# exit 0 — 100 files / 15 diagrams; browser candidate

make course-build
uv run python -m course.build --output build/course-step41-repeat
diff -qr build/course build/course-step41-repeat
# exit 0 — 100 files / 15 diagrams; byte-identical

make check
# exit 0 — Ruff/format, 531 passed, plan/course governance, Compose config

curl http://127.0.0.1:8099/course/
curl http://127.0.0.1:8099/course/topic-0010.html
# HTTP 200 for both; full lecture visible
```

Final full-site SHA256 after documentation-only status update:
`4b06abef81486eb950d2b8741db4dfd44a2f09b36856f23c697e066c168780ec`.
Post-status `make course-build` and independent build in
`build/course-step41-repeat` completed with exit 0 and the same SHA256;
`diff -qr` returned 0.

## Операционный сбой и остаточный риск

Между browser passes Chrome начал выдавать `Target crashed` даже для
ранее работавших страниц. Диагностика показала около 17 МБ свободного
места на `/`. Штатная очистка восстановимого npm-кэша (`npm cache clean
--force`) завершилась с кодом 0; затем доступное место составило 5,2 ГБ,
а новый Chrome browser gate прошёл. Из этого не следует доказанная
единственная причина каждого crash. Кэш можно восстановить загрузкой;
исходники, volumes и `.env` не удалялись.

Реальное взаимодействие со скринридером, аппаратный touch, печать на
бумагу/PDF, cross-browser и fresh live SQL probe не проводились.
Датированное STEP-0008 не доказывает текущие grants при любых environment
overrides или полноту защиты диалекта ClickHouse. Далее — лекция 11.
