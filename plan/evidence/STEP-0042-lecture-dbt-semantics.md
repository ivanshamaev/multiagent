# Evidence — STEP-0042: лекция 11, dbt и семантика аналитической модели

Captured: 2026-09-17 UTC. Scope: course content/publication, без изменения
runtime, Docker data platform и платных LLM вызовов.

## Content и источники

- Написана `course/lectures/LECTURE-0011-dbt-semantics.md`; SHA-256
  `c0056c6e903934432ef3dcfac71c2d29199b188e2bbb3d5616052c8e2e50c535`.
- Отдельные same-author editorial, technical и recheck passes записаны в
  `course/reviews/LECTURE-0011.json`. Использованы skills
  `technical-markdown-lectures`, `technical-editorial-review`,
  `technical-claim-verification`; SHA инструкций сохранены в receipt.
- Первоисточники: статьи dbt Labs S17/S18, официальные dbt reference для
  `parse`, `compile`, `build`, `test`, `ref()` и официальная Cosmos testing
  behavior документация. Claims сверены с `platform/dbt/models/`,
  `platform/dbt/tests/`, `platform/airflow/dags/cosmos_pipeline.py` и
  историческим `plan/evidence/STEP-0004-airflow-cosmos.md`.
- Исправлены два minor finding: grain промежуточной модели уточнён до
  успешных попыток оплаты; определение SQL-модели ограничено этим проектом.
  Секции повторно вычитаны. Реализация, исторический запуск и
  гипотетический контрпример различены явно.

## Browser и публикация

- Candidate: `uv run python -m course.build --candidate 11 --output
  build/course-step42-review-0011` — exit 0, 102 файла, 16 диаграмм.
- Chrome candidate `/course/topic-0011.html`: desktop, 360px mobile,
  light/dark, no-JS, keyboard zoom/pan/reset/fullscreen с возвратом фокуса,
  print, AX main + SVG name/description, CSP, subpath и links — PASS.
  Семь файлов `output/playwright/step42/lecture-11/*.png` осмотрены;
  мобильная схема начинает с `raw.payments`, печать содержит все узлы,
  стрелки и кириллицу. Их SHA-256 — в `PUBLICATION-0011.json`.
- Content digest `7346c9b5d4f4be3b13f003ddfc6fff7743bcd8e6af639b69b10e46e43e3f96c2`;
  publication digest `501e635f06db362271268722baaf0ccd95134754393bea5df363b31e3726abab`.
  Обычная сборка публикует лекцию 11 (`publication: true`), rendered SHA
  `2f1b762532bc189b7036f26529b266f18a3e0c33250ad1eafd9220e504871d7d`.
- `make course-check` — exit 0. `make course-build` и повторная
  `uv run python -m course.build --output build/course-step42-repeat` — exit 0,
  site SHA `17f42e3eda47a39cc2684bdd6dc2efea280abcf0d10f11b0c84499fc65cc47ee`;
  `diff -qr` — exit 0. Preview `http://127.0.0.1:8099/course/topic-0011.html`
  — HTTP 200.
- `make check` — exit 0: Ruff, 531 pytest tests, plan/course governance
  и Compose config PASS. `git diff --check` — см. завершающую проверку.

## Пределы доказательства

Рецензия выполнена автором, а не независимым reviewer. AX tree и no-JS
проверены, но реальный Orca/NVDA/VoiceOver, аппаратный touch и печать на
бумаге не проверены. STEP-0004 — историческое наблюдение 2026-09-05,
не свежий live прогон ClickHouse/Airflow и не гарантия качества всех
будущих данных. Полнота бизнес-определения метрики требует отдельного
контракта и проверки, которую зелёные dbt tests сами по себе не заменяют.
