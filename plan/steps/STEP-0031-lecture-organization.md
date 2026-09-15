# STEP-0031 — Phase L: лекция 01, организация команды

Status: completed

Owner: Codex

Updated: 2026-09-15

## Scope и границы

Написать глубокую теоретическую лекцию 01 по индивидуальному TODO: role decomposition,
task coupling, separation of duties. Показать Analyst/PM/DE/Validator/QA/Reviewer
как распределение ответственности и прав, не пересказывать их алгоритмы и agent loop.
Нет labs/student setup; runtime/платформу/модели не менять.

Разрешённые пути: текст/план 01, её manifest и receipts, course indices,
plan evidence/progress. Публиковать 01 лишь после того же STEP-0030 gate;
при необходимости повторно проверить навигационные claims 00.

## Skills и последовательность

1. `technical-markdown-lectures`: deep theory по scope/owners/prerequisites.
2. `technical-editorial-review`: отдельная полная вычитка после написания.
3. `technical-claim-verification`: primary sources/current code/historical evidence.
4. Исправления и полный recheck; `playwright` для фактического reader/SVG gate.
Авторские passes не называются независимым review.

## Acceptance checklist

- [x] Перечитать Data Mesh и Cognition original + актуальный follow-up; source caveats.
- [x] Проверить соседние owners 10/11/13/14/26, code profiles и ADR-0003/0006.
- [x] Написать определения, причинную модель, критерии разделения, ограничения,
  контрпример, иллюстрацию нашей системы, diagram/table, итог и 3–5 вопросов.
- [x] Отдельно вычитать, проверить claims/diagram semantics, исправить и перечитать.
- [x] Обновить lecture TODO и content receipt с финальным digest/skill versions.
- [x] Реальный candidate render/browser/visual gate и publication receipt, без fake AT PASS.
- [x] Course-check/build/repeat/pytest/make check; evidence, remaining risks и next step.

## Риски и verification

Не выдавать заголовок Don’t Build Multi-Agents за универсальный запрет; сопоставить
с follow-up автора. Data Mesh — аналогия ответственности, не свойство нашей платформы.
Разные prompts не означают независимость ошибок; role name не является capability.
Исторические STEP-0008 measurements не переносить на текущий live статус.
Команды — те же gate/build/browser проверки STEP-0030. Preview 8099 не останавливать.

## Выполненная verification

`make check`: exit 0, 529 tests PASS, Ruff и plan/course/Compose checks PASS.
Post-publication course suite: exit 0, 78 tests PASS in 48.36s.
Candidate + обычная сборка: exit 0, 82 files/6 diagrams; повторная обычная сборка
и побайтовое сравнение PASS. Browser/visual scope и hashes — в отдельных receipts.
[Evidence](../evidence/STEP-0031-lecture-organization.md). Следующая тема — лекция 03.
