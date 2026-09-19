# Evidence — STEP-0047: лекция 16, Reviewer

Captured: 2026-09-18 UTC. Scope: theory-only course text and text-only
publication. Runtime, Data Platform, Docker services and paid LLM не менялись.
Не делались screenshots, browser navigation или визуальная вычитка SVG/HTML.

## Авторство и фактчекинг

- Написана `course/lectures/LECTURE-0016-review-authority.md`; SHA-256
  `34dbe1486794ec504dbc85e3a63b819191c3c4603aca30b8199062b0d7b7b9d3`.
- Same-author separate editorial, technical и recheck passes, source anchors,
  skill hashes и две исправленные minor findings записаны в
  `course/reviews/LECTURE-0016.json`. Content digest:
  `20984f195803edc0998d3ac8ee0ab34f4b329d52018d0ffd3b2358b61954ba08`.
- Первичные источники Google Testing Blog S19 и Cognition S04 перечитаны
  2026-09-18. Claims сверены с Reviewer executor, acceptance contract,
  role profile, four-mutant manifest и датированными STEP-0011, EXP-0004,
  PRB-0037. Mermaid source, подпись и текстовый эквивалент сопоставлены
  с кодом. Rendered visual quality не проверялось.

## Публикация и проверки

- `uv run python -m course.check` — exit 0, до и после публикации.
- `uv run python -m course.build --candidate 16 --output
  build/course-step47-text-review-0016` — exit 0: 112 файлов, 21 диаграмма.
  Это механический render, не human visual review. Publication digest
  `7b17b40c71561bacf220049517e17b31632030f49a6cf98f750092215431fcf3`;
  rendered SHA лекции
  `cc1113d242f34ee167b236acdd9df55727bf31b0c040633f03f86eedd3b1e5cc`.
- `make course-build` и повторная `uv run python -m course.build --output
  build/course-step47-repeat` — exit 0: site SHA обоих
  `6665f83a55ce82375916481a7c01c6969796ac72848b1aa309ceb980120cba92`;
  `diff -qr build/course build/course-step47-repeat` — exit 0.
- `make check` — exit 0: Ruff, 532 pytest tests, plan/course governance,
  Docker Compose config PASS. Проверка сайта не подразумевает запуска
  Docker, live GateLLM или Data Platform.

## Пределы доказательства

Review same-author, не независимый. Статическая сборка подтверждает
собираемость Markdown/SVG и repeatability, не визуальную читаемость,
mobile/print/AX или взаимодействие с assistive technology. Исторический
Reviewer corpus 4/4 — не оценка будущей частоты false approval. `DONE`
локального workflow не означает production merge или deploy; fully-live
six-role READY не заявлен.
