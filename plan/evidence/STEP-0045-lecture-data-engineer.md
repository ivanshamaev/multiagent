# Evidence — STEP-0045: лекция 14, Data Engineer

Captured: 2026-09-18 UTC. Scope: theory-only course content and text-only
publication migration. Runtime/Data Platform, Docker и платные LLM не изменялись.
Скриншоты, browser navigation и визуальная вычитка не выполнялись.

## Текст и источники

- Написана `course/lectures/LECTURE-0014-data-engineer.md`; SHA-256
  `5d7c9b45489a5c8672f0068d6ff066b7865edeecea3d35b29c293d68beeefe1e`.
- Отдельные same-author editorial, technical и recheck passes с source anchors,
  findings и skill SHA записаны в `course/reviews/LECTURE-0014.json`.
  Первоисточники — Claire Carroll / dbt Labs, *What is analytics engineering?*
  (S17), и Anthropic, *Effective harnesses for long-running agents* (S09),
  прочитаны 2026-09-18. Перенесены только относящиеся к теме идеи.
- Local claims сверены с `runtime/data_engineer.py`,
  `runtime/data_engineer_workflow.py`, `runtime/specification.py`,
  `runtime/tools/workspace.py`, `runtime/validator.py`, DE profile,
  Net Revenue manifest/specification и датированными STEP-0009/0013.
  20 профильных DE/scenario/course-policy тестов — exit 0.
- Исправлены три minor finding: допустимый SQL против бизнес-смысла,
  envelope validation против фактической hash-сверки загрузчика и явная
  эскалация при конфликте с самой спецификацией. Схема проверена только
  как Mermaid source и текстовый эквивалент; визуальное качество не заявлено.

## Text-only publication gate

- `course.check` и `course.publication` поддерживают исторические schema v1
  и новые text-only schema v2. V2 запрещает browser/visual pass fields,
  требует text/diagram-semantics review, актуальные hashes и успешную
  машинную сборку. Старые v1 records не превращены в фиктивные v2:
  пересчитаны только их content/publication fingerprints после изменения
  общих правил и checker, фактические pass records оставлены без изменений.
- Candidate `uv run python -m course.build --candidate 14 --output
  build/course-step45-text-review-0014` — exit 0: 108 файлов, 19 диаграмм.
  Это автоматический render, **не** human visual review.
- Content digest `fb55087a3ed344507294d62d15756c95041848a33a1177e1041aeb42273fbb97`;
  publication digest `a2a1d3c41fc17213313a76cb12bd33842d0a6f0d6f8f659c58dc7fd9b96ec87e`.
  Reader публикует лекцию 14 (`publication: true`); машинный rendered SHA
  `73ba91013002d9c73222039b57d235bd99dbdbe0c8f69cae152c3cbe9f6b6696`.
- `make course-check`, `make course-build` — exit 0; обычный site SHA
  `9c893aa901c33636cd39ac88975108cfe01c6af7beb20eda0fbb7697202b06c4`.
  Повторная `uv run python -m course.build --output build/course-step45-repeat`
  — exit 0 с тем же SHA; `diff -qr build/course build/course-step45-repeat`
  — exit 0. `make check` — exit 0: Ruff, 532 pytest tests, plan/course
  governance и Docker Compose config PASS. Финальные `git diff --check`,
  plan governance и course-check выполнены после записи evidence.
- После публикации text-only формулировка синхронизирована в todo-планах
  будущих лекций 15–26, outlines 15–25 и шаблоне лекции. Из-за изменения
  страниц outlines обе статические сборки повторены; site SHA выше — финальный.

## Пределы доказательства

Review same-author, не независимый. Машинная сборка доказывает синтаксическую
и структурную собираемость статического сайта; не доказывает читаемость SVG,
mobile/print/dark mode, AX/AT или зрительное соответствие диаграммы.
Исторический DE sample не доказывает fresh model quality или fully-live
Analyst→PM→DE READY; human-authored spec не является выходом live PM.
