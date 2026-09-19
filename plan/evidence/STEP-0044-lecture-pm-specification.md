# Evidence — STEP-0044: лекция 13, PM и формальная спецификация

Captured: 2026-09-18 UTC. Scope: course content/publication; runtime,
Docker data platform и платные LLM не изменялись/не запускались.

## Content и источники

- Написана `course/lectures/LECTURE-0013-pm-specification.md`; SHA-256
  `454156d402259d5e5d23254a0415110427aeef620fcf8f08888a325f6560a869`.
- Separate same-author editorial, technical и recheck passes записаны в
  `course/reviews/LECTURE-0013.json` с SHA инструкций трёх editorial skills.
  Первичные статьи dbt Labs, *Build and centralize metrics with the dbt
  Semantic Layer* (S15), и Zhamak Dehghani, *Data Mesh Principles and Logical
  Architecture* (S14), прочитаны 2026-09-18; идеи адаптированы с attribution.
- Implementation claims сверены с `runtime/agent_runtime.py`,
  `runtime/specification.py`, `contracts/artifacts.py`,
  `orchestrator/transitions.py`, human-authored
  `scenarios/net-revenue/specification.json` и датированным
  `plan/evidence/STEP-0013-pm-specification-gate.md`.
  Профильные PM/spec/workflow тесты: 28 passed, exit 0.
- Исправлены четыре minor editorial/technical finding: число категорий,
  вход executor против model-visible prompt, семантическая materiality против
  структурной проверки и точность примера с возвратами. Затронутые места
  перепроверены.

## Browser и публикация

- Candidate: `uv run python -m course.build --candidate 13 --output
  build/course-step44-review-0013` — exit 0, 106 файлов, 18 диаграмм.
- Chrome candidate `/course/topic-0013.html`: desktop, 360px mobile,
  light/dark, no-JS, keyboard zoom/pan/reset/fullscreen с возвратом фокуса,
  print, AX main + SVG name/description, CSP, subpath и links — PASS.
  Семь изображений `output/playwright/step44/lecture-13/*.png` осмотрены:
  все READY/BLOCKED/отказ ветки, стрелки и кириллица видны в print;
  на mobile схема прокручивается локально. Hashes — в `PUBLICATION-0013.json`.
- Content digest `9c0c49f7f986b8ab10f820ec60e2eb89c1b104b69bd1d0c3bfc6e078a71d88ae`;
  publication digest `4cf22218e0730b4e2936d6ec53d2fb5fcec097604201cc7265e2dfc56cf81cdb`.
  Обычный reader публикует лекцию 13 (`publication: true`), rendered SHA
  `01808248e9de3e80b5f2cf9ed35ccbb469ecb2b0786b5b9be51460b1b68ce5cb`.
- `make course-check`, `make course-build` и повторная
  `uv run python -m course.build --output build/course-step44-repeat` — exit 0.
  Оба site SHA: `c842688981a4b7f9a34a27f01844301e657d8e1afa57213fd36e55701a35c2c6`;
  `diff -qr build/course build/course-step44-repeat` — exit 0.
  Preview `http://127.0.0.1:8099/course/topic-0013.html` — HTTP 200.
- Первый `make check`: Ruff PASS, 530/531 pytest PASS; единственный fail —
  требование evidence для уже закрытого STEP-0044. Этот файл добавлен;
  полный повторный `make check` — exit 0: Ruff, 531 pytest tests,
  plan/course governance и Docker Compose config PASS. Финальные
  `git diff --check`, `uv run python -m policies.plan_governance` и
  `make course-check` — exit 0 после этой записи.

## Пределы доказательства

Рецензия выполнена автором, не независимым reviewer. Chrome AX/no-JS не
заменяет реальный Orca/NVDA/VoiceOver; аппаратный touch, бумажная печать
и межбраузерный аудит не выполнены. Формальная полнота PM spec не доказывает
истинность бизнес-метрики. Human-authored READY baseline не является
результатом live PM, а STEP-0013 зафиксировал только historical BLOCKED.
