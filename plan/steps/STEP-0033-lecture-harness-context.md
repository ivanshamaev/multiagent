# STEP-0033 — Phase L: лекция 04, harness и контекст вызова

Status: complete

Owner: Codex

Updated: 2026-09-16

## Goal, scope и non-goals

Написать и опубликовать theory-only лекцию 04: per-turn context selection,
model-provider abstraction и structured response boundary. Объяснить harness
как кодовый слой сборки запроса, вызова модели и обработки результата, а не
саму модель, workflow policy или хранилище всей памяти.

Разрешены текст/TODO 04, manifest/receipts 04, module companion, course indices,
step/evidence/progress. Runtime/platform, общие hashed requirements/skills/toolchain
и опубликованные тексты не менять. Нет labs, paid LLM или Docker mutations.
Не пересказывать lifecycle state 17, recovery 18, cost 23, MCP 06, contracts 03.

## Skills и acceptance checklist

- [x] Перечитать requirements/glossary/owners и primary S07/S30 с caveats.
- [x] Проверить runtime/context.py, model_provider.py, agent_runtime.py, tests и STEP-0007.
- [x] Написать definitions/causality, selection vs compaction, prompt/retrieval/tool
  observation distinctions, provider abstraction, structured-output errors, counterexample,
  Mermaid, summary и пять questions.
- [x] Выполнить отдельные technical-markdown authoring, editorial и claim verification passes.
- [x] Исправить findings, перечитать весь текст, сохранить content receipt и skill hashes.
- [x] Actual candidate render + Playwright desktop/mobile/no-JS/keyboard/print/AX/CSP/links;
  screenshots inspected, actual AT gap explicit.
- [x] Publication receipt, reviewed manifest, deterministic builds, full checks/evidence.

## Risks и verification

Не приравнивать context window к памяти или доступному payload к доверенному факту.
Compaction — lossy transformation, не доказательство сохранения смысла. Structured
response mode не гарантирует domain acceptance. Protocol abstraction не обещает
одинаковое поведение/качество всех providers. Current ContextBundle выбирает explicit
files и byte ceilings, а не semantic retrieval; actual token count не вычисляется.

Verification: targeted context/model-provider/runtime tests; course-check; isolated
`--candidate 4` в `build/course-review-0004`; Playwright gate;
обычная/repeat builds + diff; `make check`, course policy suite, plan/course checks,
`git diff --check`. Основной preview 8099 оставить работающим.

## Work log

2026-09-16: план создан до authoring; skills/owner outlines/current context/provider
прочитаны. Используем STEP-0030 gate; новое архитектурное решение не требуется.

2026-09-16: лекция и два receipts опубликованы; отдельные editorial/technical/recheck
и actual candidate reader passes выполнены. Две minor findings исправлены; полный
текст перечитан. `make check`: exit 0, 529 PASS; targeted runtime: 40 PASS,
course policy: 78 PASS. Две обычные сборки совпали побайтово (86 files/8 diagrams).
Основной preview 8099 HTTP 200; actual AT не проверялось.
[Evidence](../evidence/STEP-0033-lecture-harness-context.md).
