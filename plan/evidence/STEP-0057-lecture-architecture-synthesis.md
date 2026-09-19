# Evidence — STEP-0057: лекция 25, архитектурный синтез

Captured: 2026-09-19 UTC. Scope: theory-only course text and text-only
publication. Runtime, Data Platform, Docker services и paid LLM не менялись.
Не делались screenshots, browser navigation или визуальная вычитка SVG/HTML.

## Авторство и фактчекинг

- Написана `course/lectures/LECTURE-0025-architecture-synthesis.md`;
  SHA-256 `a6c37e50c2f62a523a358fececcdb90f027a6ff8dca12ce2b7b9bad9c8a5a8e9`.
- Separate same-author editorial, technical и recheck passes, source anchors,
  skill hashes и четыре исправленные minor findings сохранены в
  `course/reviews/LECTURE-0025.json`. Content digest:
  `29ae7ff1c41c3a6ca3498ac7053f061736149e92002edfabb93f03f498185d66`.
- Anthropic S09 и Cognition S04 проверены онлайн 2026-09-19. Claims сверены
  с current contracts/reducer/role pipeline/policy/telemetry и датированными
  STEP-0010/0013/0020/0024. External ideas не выданы за local evidence.
- Diagram terminal semantics, graph-v2/v3 boundary, owner lecture number и
  pinned Mermaid syntax исправлены; source, подпись и текстовый эквивалент
  повторно сопоставлены.

## Публикация и проверки

- Первый `make course-review COURSE_LECTURE=25` остановился на semicolon в
  sequence message, который pinned Mermaid parser трактовал как separator.
  После текстовой замены повтор — exit 0: 130 файлов, 30 диаграмм.
- Publication digest:
  `82b1a2fec01a6b749537e4618dffd6ea18d2669879bd939a15e5439bce28aa96`;
  canonical rendered `body + TOC` SHA:
  `2908e0740e08fded85291d480fff7b98bfa3865ddb122e6c287e83a21c90daa1`.
- `make course-build` и `uv run python -m course.build --output
  build/course-step57-repeat` — exit 0: site SHA обоих
  `754cf4385140f4bd596b90bf9200f4c7df9881bbaac30df910b984f24b626942`;
  `diff -qr build/course build/course-step57-repeat` — exit 0.
- Первый `make check` дал 531 PASS и единственный governance FAIL из-за
  уже занятого номера STEP-0056. План лекции перенумерован в STEP-0057 без
  изменения существующего `STEP-0056-github-pages-course-ci.md`; final
  `make check` — exit 0: 532 pytest tests, Ruff, plan/course governance и
  Docker Compose config PASS.

## Пределы доказательства

Review same-author, не независимый. Статическая сборка подтверждает
собираемость Markdown/Mermaid и repeatability, но не визуальную читаемость,
mobile/print/AX или assistive technology. Four-layer model и architectural
closure — аналитический синтез, не новый runtime. Не проверялись fresh paid
models, полностью live six-role READY path, dynamic manager, autonomous
merge/deploy или production certification. Historical live slices не
образуют один end-to-end run и не являются текущим SLO.
