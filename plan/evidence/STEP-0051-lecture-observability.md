# Evidence — STEP-0051: лекция 20, Observability

Captured: 2026-09-19 UTC. Scope: theory-only course text and text-only
publication. Runtime, Data Platform, Docker services and paid LLM не менялись.
Не делались screenshots, browser navigation или визуальная вычитка SVG/HTML.

## Авторство и фактчекинг

- Написана `course/lectures/LECTURE-0020-observability.md`; SHA-256
  `9a9c9d33eb9307ef53f51cdabcb2b49fe42628436fa2c0c4916f3523742b9559`.
- Separate same-author editorial, technical и recheck passes, source anchors,
  skill hashes и три исправленные minor findings — в
  `course/reviews/LECTURE-0020.json`. Content digest:
  `43e5d0f0a45011df50065a5c8fef0aedc7c323f67129537aa65e991a3582ed76`.
- Dapper S29, Anthropic Managed Agents S27 и официальные OpenTelemetry
  trace/sampling docs проверены 2026-09-19. Claims сверены с текущими
  telemetry facade, Collector/Tempo/Prometheus/Grafana configs, tests и
  датированными STEP-0021/0023. Historical live и offline evidence отделены.
- Parent/child ограничен instrumented operational causality; keep-errors не
  назван гарантией полноты. Зафиксировано, что span metrics получают поток
  после tail sampling, hashes не являются encryption, trace не показывает
  private reasoning или semantic correctness. Mermaid source, подпись и
  текстовый эквивалент сопоставлены с кодом/config.

## Публикация и проверки

- `uv run python -m course.check` — exit 0 до и после публикации.
- `uv run python -m course.build --candidate 20 --output
  build/course-step51-text-review-0020` — exit 0: 120 файлов, 25 диаграмм.
  Publication digest:
  `4978d189d89004f827c2bd215a6c96b70aa09f7a9635e3beb3835b003ddb007a`;
  rendered SHA лекции:
  `e721bc80a7393b7e1527abc213f260114d475549f505d3eb6f6cade76399ac1e`.
- `make course-build` и `uv run python -m course.build --output
  build/course-step51-repeat` — exit 0: site SHA обоих
  `5ffc1c1479c5492b5e1de854c377bcc6b7c333977f0dd4b6527619e7c148b038`;
  `diff -qr build/course build/course-step51-repeat` — exit 0.
- `make check` — exit 0: Ruff, 532 pytest tests, plan/course governance,
  Docker Compose config PASS. Docker services, live observability backend
  и Gateway не запускались.

## Пределы доказательства

Review same-author, не независимый. Статическая сборка подтверждает
собираемость Markdown/SVG и repeatability, но не визуальную читаемость,
mobile/print/AX или работу assistive technology. STEP-0021 — offline/fake
transport evidence; STEP-0023 — historical single-host live smoke от
2026-09-14, не свежая проверка доступности. Sampling намеренно теряет traces,
а post-sampling metrics не представляют автоматически полную популяцию.
Не доказаны HA, TLS, alerts, external storage или fully-live six-role READY.
