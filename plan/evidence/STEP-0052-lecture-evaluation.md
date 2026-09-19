# Evidence — STEP-0052: лекция 21, Evaluation

Captured: 2026-09-19 UTC. Scope: theory-only course text and text-only
publication. Runtime, Data Platform, Docker services и paid LLM не менялись.
Не делались screenshots, browser navigation или визуальная вычитка SVG/HTML.

## Авторство и фактчекинг

- Написана `course/lectures/LECTURE-0021-evaluation.md`; SHA-256
  `2e7f91382b72f684981bcd68656cbbf65a926860f1f8cede0fddbb0a1871ed01`.
- Separate same-author editorial, technical и recheck passes, source anchors,
  skill hashes и три исправленные minor findings — в
  `course/reviews/LECTURE-0021.json`. Content digest:
  `e9450ad67def5e993241730370a60b1a5b38512cc435c08639b439987def8817`.
- Anthropic S20/S21 проверены онлайн 2026-09-19. Claims сверены с текущими
  Phase K suite/baseline/runtime/tests и датированными STEP-0024/STEP-0009.
  Offline regression, historical live sample и fresh comparison разделены.
- `51/51` и `102/102` не названы независимыми semantic tasks или live model
  quality; `7/10` ограничены одним DE scenario/configuration. Гетерогенные
  24 попытки ролей не агрегированы в общий success rate. Mermaid source,
  подпись и текстовый эквивалент сопоставлены с прозой.

## Публикация и проверки

- `uv run python -m course.check` — exit 0 до и после публикации.
- `uv run python -m course.build --candidate 21 --output
  build/course-step52-text-review-0021` — exit 0: 122 файла, 26 диаграмм.
  Publication digest:
  `8be91920c277f1e3a44967cf8b2db0f8c9968491888437cad2fc4dd288df4d7f`;
  rendered SHA лекции:
  `2bfa9aa8b06852803f9bbe383fcea0acfb892dc65d8db9289af24cc866f6f0a8`.
- `make course-build` и `uv run python -m course.build --output
  build/course-step52-repeat` — exit 0: site SHA обоих
  `f76d1a09168027f4c06e43eb1c8e788a4957d4d2df768118c7896a3514508371`;
  `diff -qr build/course build/course-step52-repeat` — exit 0.
- `make check` — exit 0: Ruff, 532 pytest tests, plan/course governance,
  Docker Compose config PASS. Docker services и Gateway не запускались.
- `git diff --check` — exit 0.

## Пределы доказательства

Review same-author, не независимый. Статическая сборка подтверждает
собираемость Markdown/SVG и repeatability, но не визуальную читаемость,
mobile/print/AX или работу assistive technology. Исторические live samples
не являются свежей оценкой provider/model. Малый N, grader errors,
contamination и общие infrastructure variables сохраняют неопределённость.
Phase K — trusted repository regression harness, не arbitrary-code/network
sandbox и не доказательство fully-live six-role READY.
