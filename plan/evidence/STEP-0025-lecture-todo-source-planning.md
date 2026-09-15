# STEP-0025 — индивидуальные планы лекций и источники

Date: 2026-09-15

Status: PASS (planning slice only; STEP-0025 remains in progress)

## Результат

Созданы 27 todo-планов: 26 core и одна optional лекция о deployment.
`plan/steps/lections/lecture-map.json` фиксирует порядок чтения, prerequisites и 81 уникальную
primary concept area. README задаёт границы смежных тем. В `course/lectures/` пока только README.

Лекции 15/16 раскрывают code-owned workflow и agent-orchestrator; лекция 26 сравнивает их и
hybrid по десяти сценариям. Dynamic manager не объявляется реализованным; границы заданы ADR-0035.
Для каждой лекции выбраны минимум две статьи и идеи для пересказа с attribution.
SOURCES содержит 30 первичных материалов: популярность — качественный редакторский фильтр,
не численный рейтинг отдельных статей. Ссылки открыты; будущие claims требуют фактчекинга.

Каждый план требует вычитку, техническую проверку, исправления и повторную проверку с review
record проверенной версии. Лабораторных работ нет. Ownership проверен для планов; отсутствие
повторов в ещё не написанных текстах не заявляется.

## Проверки

- `python3 - <<'PY' … PY` — inline read-only validation JSON/Markdown, exit 0:
  27 IDs, 26 core + 1 optional, 81 unique concepts, prerequisite order, 259 links,
  минимум 15 author todo на план; lecture texts absent.
- `make plan-check` — exit 0, `plan governance: PASS`.
- `uv run pytest -q tests/policy/test_plan_governance.py` — exit 0, 3 passed in 0.31s.
- `git diff --check` — exit 0.

## Осталось

STEP-0025 не завершён: полный scaffold/checker и planned editorial skills ещё не созданы.
Затем требуется проверять каждый текст и согласованность курса. Runtime, Docker, paid LLM calls
и секреты не затрагивались.
