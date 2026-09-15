# STEP-0032 — Phase L: лекция 03, контракты и границы доверия

Status: in progress

Owner: Codex

Updated: 2026-09-15

## Goal, scope и non-goals

Написать и опубликовать глубокую theory-only лекцию 03 по индивидуальному TODO:
artifact schema, contract invariants, cross-task binding. Различить допустимый формат,
внутреннюю согласованность, соответствие текущей задаче и истинность результата.
Пример — текущие contracts/common.py, artifacts.py, evidence.py и reducer gates;
STEP-0006 — historical evidence, ADR-0014 — решение, не свежий live proof.

Разрешённые пути: текст/TODO 03, её manifest entry/content/publication receipts,
module-03 companion, course indices и plan/progress/evidence. Runtime/platform,
общие hashed requirements/toolchain/skills и уже опубликованные тексты не менять.
Нет labs, student setup, paid LLM, Docker startup/reset или новых agent capabilities.
Не пересказывать PM semantics 10, DE implementation 12, workflow graph 15,
authentication 19, storage/recovery 17/18 и evaluation methodology 21.

## Skills и checklist

- [ ] Прочитать планы/requirements/glossary/owners, source caveats и первичные статьи S08/S20.
- [ ] Проверить current contracts/reducer, ADR-0014 и dated STEP-0006.
- [ ] Написать модель границы, определения, причинность, versioning/immutability,
  cross-task/actor binding, нарушения, контрпример, Mermaid и пять вопросов.
- [ ] technical-editorial-review: отдельная полная вычитка после authoring
  с technical-markdown-lectures; technical-claim-verification: отдельные claims/source anchors.
- [ ] Исправить findings, перечитать; сохранить версии skills и актуальный content receipt.
- [ ] Candidate render и playwright browser/visual gate; честный AX/actual AT scope.
- [ ] Sealing publication receipt, reviewed, build/repeat и final checks/evidence.

## Acceptance, риски и verification

Schema validity не гарантирует domain correctness; self-reported producer_id не authenticates
роль; SHA256/relative path не доказывают существование файла или происхождение evidence.
Pydantic frozen — не абсолютная tamper-proof/deep immutability; schema v1 не версия SDK.
Diagram обозначает логические проверки, не точную runtime call sequence.

Команды: targeted contract/workflow pytest; `make course-check`; isolated
`uv run python -m course.build --candidate 3 --output build/course-review-0003`;
Playwright /course/ desktop/mobile/no-JS/keyboard/print/AX/CSP/links и screenshots;
`make course-build`, повторная labelled build + diff; `make check`, `git diff --check`.
Publication только после реальных passes. Preview 8099 оставить доступным.

## Work log

2026-09-15: изучены scope/owners, current contracts и ADR-0014; внешние primary
articles и Pydantic models проверяются перед авторством. Новое ADR не требуется:
используется принятый STEP-0030 publication gate без изменения архитектуры.
