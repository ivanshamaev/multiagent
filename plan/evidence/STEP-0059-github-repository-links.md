# Evidence — STEP-0059: прямые ссылки на repository examples

Captured: 2026-09-19 UTC. Scope: static course link mapping и publication
receipts. Исходные тексты лекций, runtime, Data Platform и Docker services не
менялись. Screenshots, browser/visual/AX review не выполнялись.

## Defect, fix and regression

- Published ref `ref-84600c447037` воспроизведён: он указывал на
  `policies/profiles/airflow_observer_v1.json`, но открывал placeholder index.
- PRB-0059 локализует причину в fallback routing `course/build.py`.
- `repository_url()` строит percent-encoded GitHub blob URL для `main`,
  сохраняет fragment и отклоняет empty, absolute, traversal и backslash paths.
- Lecture pages используют direct URLs; `references.html` остаётся
  кликабельным индексом без копирования repository files в public site.
- `tests/policy/test_course_build.py` покрывает direct link, line fragment,
  index, отсутствие старого routing и unsafe paths.

## Publication refresh

- Все 27 manifest statuses были временно переведены в
  `technically-verified` только для пересчёта publication receipts, затем
  возвращены в `reviewed`; status не входит в content digest.
- Content review receipts не менялись. Publication receipts обновлены до
  schema 2 с новым builder hash и явным text-only scope; прежние visual claims
  не переносились.
- Candidate build: 132 files, 31 diagrams,
  `c473f9cdc50fcd2486097be3c824b231ee6b01e70e014c20179fd623d55df686`.
- Production audit: 212 direct GitHub links, 0 legacy reference anchors и
  107 clickable repository entries в index.
- Две production builds: 132 files, 31 diagrams, одинаковый site SHA-256
  `581ca469d5d023f4173a532e63e3e7ba9e656bd9fb07604b25c2ca22041f5a54`.
- Targeted policy suite: 86 passed.

## Verification

- `make check`: PASS; Ruff и format checks, 537 pytest tests, plan/course
  governance и Docker Compose validation прошли.
- `git diff --check`: PASS.
- GitHub Pages workflow публикует только после push в `main`; push/deploy в
  рамках шага не выполнялись.

## Remaining boundary

URL следует mutable branch `main`: local build проверяет наличие target в
собираемом checkout, но не заменяет внешний link monitor. Immutable commit
links потребуют отдельной provenance policy.
