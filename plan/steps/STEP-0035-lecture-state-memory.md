# STEP-0035 — Phase L: лекция 04, состояние и память

Status: in progress

Owner: Codex

Updated: 2026-09-16

## Goal, scope и non-goals

Написать и опубликовать theory-only лекцию 04 о различии контекста вызова,
состояния workflow, передаваемых артефактов и долговременного знания. Показать
их lifetime, visibility, consistency, потери при summarization и границы
shared scratchpad/accepted handoff. Пример — только подтверждённый текущий код.

Разрешены лекция и её TODO/module companion, manifest/receipts, индексы курса,
step/evidence/progress. Runtime/platform, опубликованные лекции и общие hashed
requirements/skills/toolchain не менять. Нет labs, paid LLM и Docker mutations.
Не повторять context engineering одного вызова (03), схемы контрактов (02),
детали восстановления/idempotency (17) или provenance (12).

## Acceptance checklist

- [ ] Прочитать S07/S03, owners, glossary, текущие code/tests и dated STEP-0019.
- [ ] Написать глубокую теорию, условия применимости, сравнение четырёх видов
  информации, причинный контрпример и одну содержательную Mermaid-схему.
- [ ] Явно отделить `offline-proven` от `historical-live` и не реализованную
  long-term semantic memory от текущего state/context.
- [ ] Выполнить separate authoring, editorial, claim verification, corrections
  и recheck; сохранить актуальный content receipt и skill versions.
- [ ] Собрать candidate, проверить browser desktop/mobile/light/dark/no-JS,
  keyboard/print/AX/CSP/links и вручную осмотреть screenshots.
- [ ] Создать publication receipt, перевести manifest в reviewed, проверить
  deterministic builds, `make check`, политику курса и зафиксировать evidence.

## Risks и verification

Не объявлять summary точной памятью, общий scratchpad принятым артефактом или
durable checkpoint гарантией exactly-once. Базовый `ContextBundle` не является
semantic retrieval; граница доступа к artifact задаётся кодом и role policy,
а не тем, что модель «помнит». Независимый review и actual assistive technology
отдельно помечаются непроверенными.

Verification: targeted runtime/context/artifact/pipeline tests; `make course-check`;
isolated candidate `build/course-step35-review-0004`; Playwright reader gate;
обычная и повторная сборки + diff; `make check`, `make plan-check`,
`git diff --check`. Preview 8099 оставить доступным.

## Work log

2026-09-16: план создан до авторства; четыре соответствующих skills прочитаны.
