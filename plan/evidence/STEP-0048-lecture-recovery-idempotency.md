# Evidence — STEP-0048: лекция 17, Recovery

Captured: 2026-09-18 UTC. Scope: theory-only course text and text-only
publication. Runtime, Data Platform, Docker services and paid LLM не менялись.
Не делались screenshots, browser navigation или визуальная вычитка SVG/HTML.

## Авторство и фактчекинг

- Написана `course/lectures/LECTURE-0017-recovery-idempotency.md`; SHA-256
  `8556a7497001d597b8a25a5e28b7ac4669a222b8e2913329209412d39f38673f`.
- Same-author separate editorial, technical и recheck passes, source anchors,
  skill hashes и три исправленные minor findings записаны в
  `course/reviews/LECTURE-0017.json`. Content digest:
  `86bebf7f94b3d99375cfa3128da727d94e96263abd13b1631dfceb49d8890736`.
- Первичные источники AWS Builders’ Library S12 и Anthropic S27 перечитаны
  2026-09-18. Claims сверены с checkpoint/receipt adapters, role executor,
  process-kill integration tests и датированными STEP-0018/0019/0020,
  PRB-0052. Mermaid source, подпись и текстовый эквивалент сопоставлены
  с кодом; rendered visual quality не проверялось.
- Согласованность следующего owner восстановлена: outline/manifest/map
  лекции 18 теперь ссылаются на operation identity из 17, как todo18.

## Публикация и проверки

- `uv run python -m course.check` — exit 0, до и после публикации.
- `uv run python -m course.build --candidate 17 --output
  build/course-step48-text-review-0017` — exit 0: 114 файлов, 22 диаграммы.
  Это механический render, не human visual review. Publication digest
  `42ce774963cda61d7d3fa5bb4bc62f390ac61a9e5b1735128fd485f4b3066ac8`;
  rendered SHA лекции
  `fbd5d701e0bcd38af77e040e7fdc48275b58cddd261085666914a593d031551d`.
- `make course-build` и повторная `uv run python -m course.build --output
  build/course-step48-repeat` — exit 0: site SHA обоих
  `322e1dad43309c592a7ddf6c576ca4cd16f56c40b05d0cdf45ee8340a2d3dbc8`;
  `diff -qr build/course build/course-step48-repeat` — exit 0.
- `make check` — exit 0: Ruff, 532 pytest tests, plan/course governance,
  Docker Compose config PASS. Проверка сайта не подразумевает запуска
  Docker, live GateLLM или Data Platform.

## Пределы доказательства

Review same-author, не независимый. Статическая сборка подтверждает
собираемость Markdown/SVG и repeatability, не визуальную читаемость,
mobile/print/AX или взаимодействие с assistive technology. Исторические
process-kill тесты не доказывают full power-loss durability checkpoint:
адаптер публикует файл после `fsync` содержимого, но не заявляет полный
parent-directory durability protocol. Receipt не дедуплицирует внешнюю
операцию до сохранения результата; fully-live six-role READY не заявлен.
