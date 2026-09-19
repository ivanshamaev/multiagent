# STEP-0045 — Phase L: лекция 14, Data Engineer и границы изменения

Status: complete

Owner: Codex

Updated: 2026-09-18

## Цель и границы

Написать theory-only лекцию 14 об implementation authority, изолированном
candidate и semantic repair по evidence. Отделить утверждённую бизнес-спецификацию
от допустимого выбора реализации; не повторять grain/dbt 11, PM readiness 13,
QA 15, reducer 06 или recovery 17. Использовать Net Revenue и текущий код,
не выдавать historical live sample за устойчивое качество или fully-live pipeline.

Уточнение пользователя: проверка лекции **только текстовая**. Не создавать
скриншоты, не запускать browser/visual review и не подменять его фиктивным PASS.
Публикационный gate надо версионировать так, чтобы новые text-only receipts
не уничтожили доказательства старых визуальных проверок.

## Порядок и критерии приёмки

- [x] Проверить первичные S17/S09, код DE, policy profile, сценарий и STEP-0009;
  записать ограничения исторических наблюдений.
- [x] Написать лекцию: причинная модель authority/candidate/repair, схема как
  **текстовый** источник с эквивалентом, Net Revenue контрпример, синтез и вопросы.
- [x] Отдельно вычитать весь текст, выполнить техническую проверку claims и
  повторную вычитку исправлений; сохранить content receipt и source anchors.
- [x] Адаптировать publication gate к text-only schema v2, сохранить schema v1
  историческим; регрессионно проверить stale/missing receipt, Markdown/links,
  build fingerprint и rendered hash без визуального подтверждения.
- [x] Обновить plan/todo/manifest/index/evidence, проверить `make course-check`,
  две идентичные статические сборки, `make check`, `git diff --check`.

## Риски

Статический build доказывает машинную собираемость, не визуальное качество
диаграммы. Исторические publication receipts v1 сохраняют своё прежнее
visual evidence; schema v2 не должна использовать слово `visual` как PASS.
Без business approval PM `BLOCKED` не превращается в разрешение DE.

## Work log

2026-09-18: план создан до текста лекции и migration публикационного gate.

2026-09-18: лекция, separate editorial/technical/recheck и text-only
publication v2 завершены. Сохранены исторические v1 receipts без изменения
pass records; повторные сборки побайтно совпали, `make check` — 532 passed.
Todo-планы и outlines будущих лекций синхронизированы с новым gate.
Подробности — [evidence](../evidence/STEP-0045-lecture-data-engineer.md).
