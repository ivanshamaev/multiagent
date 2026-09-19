# Evidence — STEP-0054: лекция 23, Cost/performance

Captured: 2026-09-19 UTC. Scope: theory-only course text and text-only
publication. Runtime, Data Platform, Docker services и paid LLM не менялись.
Не делались screenshots, browser navigation или визуальная вычитка SVG/HTML.

## Авторство и фактчекинг

- Написана `course/lectures/LECTURE-0023-cost-performance.md`; SHA-256
  `9e0fba372a5942412cb1904327aa52d8daa9f83bf82de1fe881805064bd37579`.
- Separate same-author editorial, technical и recheck passes, source anchors,
  skill hashes и три исправленные minor findings — в
  `course/reviews/LECTURE-0023.json`. Content digest:
  `80a31c453db291adbca6c67578aca2292de1228029e36e57c2a68b6e76ca9b09`.
- Anthropic S26/S02 проверены онлайн 2026-09-19. Claims сверены с текущими
  provider/accounting/budget code/tests и датированными EXP-0001/STEP-0009.
  External token/time claims не перенесены на data-engineering platform.
- Failure cost защищён от double counting; critical-path formula ограничена
  независимыми ветвями и доступными ресурсами; hypothetical `cost/success`
  подписан assumptions. Исторические ₽/latency не названы текущими price/SLO.
  Mermaid source, подпись и текстовый эквивалент сопоставлены с прозой.

## Публикация и проверки

- `uv run python -m course.check` — exit 0 до и после публикации.
- `make course-review COURSE_LECTURE=23` — exit 0: 126 файлов,
  28 диаграмм. Publication digest:
  `f2c70961c06eb4e9b94bf0556566bd30f7da59a1b856b463cb86e1a481849457`;
  rendered SHA лекции:
  `282e32e958f7aa48a3b9875f9773945cce1785fd83bf621336528e02c9ca2549`.
- `make course-build` и `uv run python -m course.build --output
  build/course-step54-repeat` — exit 0: site SHA обоих
  `fb4f2f8672a88698112bcb87dfeab5e0466c367082f80858db70d24b3ac7a9e1`;
  `diff -qr build/course build/course-step54-repeat` — exit 0.
- `make check` — exit 0: Ruff, 532 pytest tests, plan/course governance,
  Docker Compose config PASS. Docker services и Gateway не запускались.
- `git diff --check` — exit 0.

## Пределы доказательства

Review same-author, не независимый. Статическая сборка подтверждает
собираемость Markdown/SVG и repeatability, но не визуальную читаемость,
mobile/print/AX или работу assistive technology. Локальное accounting
оценивает model charge, а не total system cost. Не проверялись свежие
GateLLM prices, caching, monetary tool/infrastructure ledger, parallel role
scheduler, dynamic manager или fully-live six-role READY. External 150k→2k,
15× и up-to-90% относятся только к описанным Anthropic systems.
