# Evidence — STEP-0055: лекция 24, Workflow vs agent-orchestrator

Captured: 2026-09-19 UTC. Scope: theory-only course text and text-only
publication. Runtime, Data Platform, Docker services и paid LLM не менялись.
Не делались screenshots, browser navigation или визуальная вычитка SVG/HTML.

## Авторство и фактчекинг

- Написана `course/lectures/LECTURE-0024-orchestration-comparison.md`;
  SHA-256 `d5af418fdb7e7b00ed33a0326427cf910718784f21aff574a39c8aee63a60dfb`.
- Separate same-author editorial, technical и recheck passes, source anchors,
  skill hashes и три исправленные minor findings сохранены в
  `course/reviews/LECTURE-0024.json`. Content digest:
  `7aaebef6548fb0de216d9928cbdce3cf577c11c0f741561f5f86ae143fb94bc2`.
- Anthropic S01/S02 и Cognition S03/S04 проверены онлайн 2026-09-19. Claims
  сверены с ADR-0035, текущими reducer/role pipeline и датированным STEP-0020.
  Vendor observations не перенесены на качество или performance платформы.
- Уточнены различия терминологии `orchestrator-workers`, необходимость
  persisted events для audit и смысл single writer. Mermaid source, подпись
  и текстовый эквивалент сопоставлены с прозой.

## Публикация и проверки

- `make course-review COURSE_LECTURE=24` — exit 0: 128 файлов,
  29 диаграмм. Publication digest:
  `949d133488ed2a2056ffa9102ff0488187a46b6d48849a8a7612ffcd9cc9cf40`;
  canonical rendered `body + TOC` SHA лекции:
  `eb0a3f0aac3359a1f5881e6daa453d6e1509df6befd40561b2150e3133284353`.
- Первый production build корректно отклонил receipt, куда по ошибке был
  записан SHA полного `topic-0024.html`, а не canonical hash из
  `diagram-index.json`. Receipt исправлен без изменения текста или gate.
- `make course-build` и `uv run python -m course.build --output
  build/course-step55-repeat` — exit 0: site SHA обоих
  `e022476b9758ef7a0266b38219413159a6e8fd31a3735e89f3981fd6e2f073c6`;
  `diff -qr build/course build/course-step55-repeat` — exit 0.
- `make check` — exit 0: Ruff, 532 pytest tests, plan/course governance,
  Docker Compose config PASS. Docker services и Gateway не запускались.

## Пределы доказательства

Review same-author, не независимый. Статическая сборка подтверждает
собираемость Markdown/Mermaid и repeatability, но не визуальную читаемость,
mobile/print/AX или работу assistive technology. Scenario matrix —
архитектурная гипотеза, а не comparative benchmark. Не реализованы и не
проверялись dynamic planner, worker queue, hybrid scheduler, autonomous
merge или fully-live six-role READY. External conclusions ограничены
описанными Anthropic/Cognition systems и не доказывают универсального
преимущества workflow либо manager.
