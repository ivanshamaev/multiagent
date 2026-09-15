# STEP-0025 — теоретический course scaffold

Date: 2026-09-15

Status: PASS (scaffold complete; lectures/render/publication not implemented)

## Реализовано

- Course README/syllabus/manifest/source-index/sources/glossary/editorial guidelines.
- 27 outlines: 26 core + extension 24. IDs 00–25 сохранены, 26 — scenario comparison.
  Prerequisite route и 81 unique concept owners синхронизированы с planning map.
- 30 primary article records, минимум две статьи/конкретные идеи на outline; code/dated evidence
  anchors и known gaps. Manager/Kubernetes явно not-implemented, offline не равно live quality.
- Module/lecture/review templates, JSON receipt schema example с false flags и без fake receipts.
- Созданы technical-editorial-review и technical-claim-verification через skill-creator:
  versioned packages в course/skills, совпадающие локальные copies в ~/.codex/skills.
  Сохранена reference copy technical-markdown-lectures; deep theory overrides default 101.
- AST-based offline checker: canonical IDs/paths, prerequisite cycles, owner/topic drift,
  links/anchors/contained paths, Markdown profile и fresh receipts, review passes/findings.
  Digest покрывает prose/assets/plans/sources/skills и central config/toolchain.
- `make course-check` включён в `make check`; 28 regression tests на positive/negative boundaries.

## Commands и результаты

- Первоначальный `uv add --dev 'markdown-it-py==4.0.0'` — exit 2, DNS/PyPI unavailable;
  dependencies тогда не изменились. Повтор разрешён пользователем.
- `curl -I --max-time 15 https://pypi.org/simple/markdown-it-py/` — exit 0, HTTP 200.
- `curl -I --max-time 15 https://markdown-it-py.readthedocs.io/en/latest/using.html` — exit 0, HTTP 200.
  Официальные parser/CLI sources также открыты через browser lookup.
- Повторный `uv add --dev 'markdown-it-py==4.0.0'` — exit 0, 62 packages resolved;
  markdown-it-py 4.0.0 + mdurl 0.1.2 установлены в .venv; pyproject/uv.lock обновлены.
- `python3 .../skill-creator/scripts/quick_validate.py <skill-path>` — exit 0, Skill is valid:
  оба repo package и оба local package.
- `uv run ruff check course tests/policy/test_course_governance.py` — exit 0.
- `make course-check` — exit 0, PASS (not editorial/render verification).
- Первые course regressions — 25 passed in 21.59s; затем добавлены 3 boundary tests.
- `make check` — exit 0: Ruff/format, **479 passed in 54.79s**, plan governance,
  course governance и `docker compose config --quiet`. Новых course tests: 28.
- `uv lock --check --offline` — exit 0, 62 packages resolved.
- `git diff --check` — exit 0.

После синхронизации completion/status/docs повторены `make course-check`, `make plan-check`,
`git diff --check`, `uv lock --check --offline`: все exit 0. Read-only metadata/copy check:
27 outline files, 81 concept owners, отсутствие lecture texts/fake receipts, exact local/repo skill match.
Skill SHA-256: editorial `d16fa811a5b73efe6b323c2883729d6308682b3e43f96a2247c3a5d8cf9d05b2`,
verification `45e9be65480c7478e97f138aaf1925a5caf87b5ebaa202a14aacf66b8c3577f3`.

## Review scope и остаточные риски

Применены technical-markdown-lectures, skill-creator и отдельные editorial/claim-verification
инструкции для проверки каркаса: структуру/terminology/owners и source/evidence boundaries.
Это same-author scaffold review, не independent review и не completed lecture receipt.
Checker проверяет формат/freshness заявленных проходов, не истинность claims или реальное
исполнение человеческой проверки. Внешние ссылки не fetchятся при offline governance.

Renderer/static generator ещё отсутствуют: toolchain хранит null, `make course-build` не создан.
SVG/HTML, visual/a11y/print/CSP/browser и reproducibility gates не выполнены. Ни одна лекция не
написана/reviewed/published. Planned diagram config не является проверенным Mermaid render.
Docker services/images/volumes не запускались/менялись; Compose выполнял только validation.
Paid LLM calls, secrets, runtime/policies/oracle/scenario corpora не затрагивались.

Следующий проверяемый этап — renderer prototype по course/build-status.md, затем авторство
pilot lectures 00/03/08 с вычиткой, technical verification и recheck после каждого текста.
