# STEP-0032 — Phase L: лекция 03, контракты и границы доверия

Status: completed

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

- [x] Прочитать планы/requirements/glossary/owners, source caveats и первичные статьи S08/S20.
- [x] Проверить current contracts/reducer, ADR-0014 и dated STEP-0006.
- [x] Написать модель границы, определения, причинность, versioning/immutability,
  cross-task/actor binding, нарушения, контрпример, Mermaid и пять вопросов.
- [x] technical-editorial-review: отдельная полная вычитка после authoring
  с technical-markdown-lectures; technical-claim-verification: отдельные claims/source anchors.
- [x] Исправить findings, перечитать; сохранить версии skills и актуальный content receipt.
- [x] Candidate render и playwright browser/visual gate; честный AX/actual AT scope.
- [x] Sealing publication receipt, reviewed, build/repeat и final checks/evidence.

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

2026-09-16: лекция написана, отдельно вычитана/проверена/перечитана и опубликована.
Targeted: 36 PASS. Candidate и browser/visual gates PASS; actual AT не запускалась.
Обычная и repeat-сборка: 84 files, 7 diagrams, одинаковый site SHA256
`5f4eb873dcfd596a589958d230c8f66b2f903f5cf9b99084f28fde39667a4eff`;
`diff -qr` PASS. Full `make check`: 529 PASS in 81.04s; post-publication
course suite: 78 PASS in 47.35s. Остаточные риски записаны в evidence.
Следующая тема teaching order — лекция 04.
