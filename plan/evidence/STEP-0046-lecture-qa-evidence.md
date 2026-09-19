# Evidence — STEP-0046: лекция 15, QA

Captured: 2026-09-18 UTC. Scope: theory-only course text and text-only
publication. Runtime, Data Platform, Docker services and paid LLM не менялись.
Не делались screenshots, browser navigation или визуальная вычитка SVG/HTML.

## Авторство и фактчекинг

- Написана `course/lectures/LECTURE-0015-qa-evidence.md`; SHA-256
  `048d0da1a5eb6bcdea708d0dde0180d2ccf2394de1c15c031f558d6d6f15f5b1`.
- Same-author separate editorial, technical и recheck passes, source anchors,
  skill hashes и одна исправленная minor finding записаны в
  `course/reviews/LECTURE-0015.json`. Content digest:
  `8222d720414a2c8acc925efd2c5a4786bef3aba5db892471104cce19040d2e93`.
- Первичные источники dbt Labs S18 и Anthropic S20 перечитаны 2026-09-18.
  Локальные claims сверены с validator/QA code, QA profile, contract,
  five-mutant manifest и датированными STEP-0010, EXP-0003, PRB-0035.
  Mermaid source, подпись и текстовый эквивалент сопоставлены с кодом;
  rendered visual quality не проверялось.

## Публикация и проверки

- `uv run python -m course.check` — exit 0, до и после публикации.
- `uv run python -m course.build --candidate 15 --output
  build/course-step46-text-review-0015` — exit 0: 110 файлов, 20 диаграмм.
  Это механический render, не human visual review. Publication digest
  `bf307617a128e42c31f4ae01fe9aaddcf7150dc650aa279f8163208990458938`;
  rendered SHA лекции
  `fead1c602d96b80a52b4884c66c9173261f09a93da6fd2edae71452db14b9584`.
- `make course-build` и повторная `uv run python -m course.build --output
  build/course-step46-repeat` — exit 0: site SHA обоих
  `7c20ed4606347b8fa3a70091e630704dcf954291e166e68943485547f3b8a98c`;
  `diff -qr build/course build/course-step46-repeat` — exit 0.
- `make check` — exit 0: Ruff, 532 pytest tests, plan/course governance,
  Docker Compose config PASS. Проверка сайта не подразумевает запуска
  Docker, live GateLLM или Data Platform.

## Пределы доказательства

Review same-author, не независимый. Статическая сборка подтверждает
собираемость Markdown/SVG и repeatability, не визуальную читаемость,
mobile/print/AX или взаимодействие с assistive technology. Исторический
QA corpus 5/5 — не оценка будущей частоты false pass; QA и oracle всё ещё
могут разделять ошибочное предположение. Fully-live six-role READY не заявлен.
