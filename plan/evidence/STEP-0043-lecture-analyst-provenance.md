# Evidence — STEP-0043: лекция 12, Analyst и provenance фактов

Captured: 2026-09-17–18 UTC. Scope: course content/publication; runtime,
Docker data platform и платные LLM не изменялись/не запускались.

## Content и источники

- Написана `course/lectures/LECTURE-0012-analyst-provenance.md`;
  SHA-256 `80c3e9596eacb4a8be33f3f8330beea4e81037d463ba8dbac987bf3e8ebd9adc`.
- Separate same-author editorial, technical и recheck passes записаны в
  `course/reviews/LECTURE-0012.json` с SHA инструкций трёх skills.
  Два внешних первоисточника — Zhamak Dehghani, *Data Mesh Principles
  and Logical Architecture* (S14), и Anthropic, *Effective context
  engineering for AI agents* (S07) — прочитаны 2026-09-17.
- Точные implementation claims сверены с `runtime/analyst.py`,
  `runtime/analyst_workflow.py`, `contracts/artifacts.py`, `contracts/tools.py`,
  `tests/fixtures/analyst_cases.json` и датированным
  `plan/evidence/STEP-0012-analyst-requirements-discovery.md`.
- Исправлены три minor finding: inventory отделён от схемы полей;
  evidence описан как ссылка на сохранённый output, а не сам output;
  Mermaid и текстовый эквивалент приведены к последовательности кода
  «три reads → tool-free synthesis → приём report → PM handoff/отказ».
  Затронутые разделы перепроверены.

## Browser и публикация

- Candidate: `uv run python -m course.build --candidate 12 --output
  build/course-step43-review-0012` — exit 0, 104 файла, 17 диаграмм.
- Chrome candidate `/course/topic-0012.html`: desktop, 360px mobile,
  light/dark, no-JS, keyboard zoom/pan/reset/fullscreen с возвратом
  фокуса, print, AX main + SVG name/description, CSP, subpath и links — PASS.
  Семь изображений `output/playwright/step43/lecture-12/*.png` осмотрены:
  первый узел виден на mobile, печать показывает все узлы, стрелки,
  ветку отказа и кириллицу. Их hashes — в `PUBLICATION-0012.json`.
- Content digest `f64b7cfebb3a316df0d7c4b4ab69798f1d7e2d3e859ac60753b9a688a22cd7e1`;
  publication digest `66c893737cc2715f0a3a87a83234d9a0c63754776033e92c5a7de55e90043f01`.
  Обычный reader публикует лекцию 12 (`publication: true`), rendered
  SHA `f782c1f4c5aacb53aa6b09f7a966a6ef284c490baf7bdf65de79ec4a3092316e`.
- `make course-check`, `make course-build` и повторная
  `uv run python -m course.build --output build/course-step43-repeat` — exit 0.
  Оба site SHA одинаковы:
  `fd77c2cb3460753181d705c26629dae3d1a2084c1d932224634badf45d40969f`;
  `diff -qr` — exit 0. Preview
  `http://127.0.0.1:8099/course/topic-0012.html` — HTTP 200.
- `make check` — exit 0: Ruff, 531 pytest tests, plan/course governance
  и Compose config PASS. Финальные `git diff --check` и plan governance
  выполнены после этой записи.

## Пределы доказательства

Рецензия выполнена автором, не независимым reviewer. Проверка AX/no-JS
не заменяет реальный Orca/NVDA/VoiceOver; аппаратный touch и печать на
бумаге не проверены. STEP-0012 содержит только два датированных live
случая и не является оценкой статистической надёжности. Текущий профиль
заказов не исследует оплаты/возвраты и не устанавливает бизнес-формулу;
все три успешных read phases не делают требования автоматически ready.
