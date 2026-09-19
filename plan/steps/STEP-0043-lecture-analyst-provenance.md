# STEP-0043 — Phase L: лекция 12, Analyst и provenance фактов

Status: complete

Owner: Codex

Updated: 2026-09-17

## Цель и границы

После лекции 11 написать и опубликовать theory-only лекцию 12 о semantic
discovery, происхождении data facts и границе между наблюдением, гипотезой
и открытым вопросом перед PM specification gate. Три read phases
иллюстрировать текущим `runtime/analyst_workflow.py`, без повторного
объяснения dbt grain/lineage, memory lifecycle или определения метрики PM.
Нет labs, runtime/Docker изменений или платных LLM вызовов.

## Порядок и критерии приёмки

- [x] Сверить S14/S07 с первичными текстами, `runtime/analyst.py`,
  `analyst_workflow.py`, contract, fixtures и датированным STEP-0012.
- [x] Написать причинную модель источников знания и evidence-backed fact,
  показать ограничение вывода из агрегата/выборки, контрпример, схему,
  3–5 вопросов и переход к PM.
- [x] Провести отдельную полную редакторскую вычитку, technical verification,
  исправления и recheck; сохранить content receipt.
- [x] Собрать candidate и проверить HTML/SVG в Chrome: desktop/mobile,
  light/dark, no-JS, keyboard, print, AX, CSP, subpath и links; сохранить
  publication receipt только после просмотра изображений.
- [x] Обновить manifest, todo, module/index и evidence; выполнить course
  gates, две идентичные сборки, `make check`, preview 8099.

## Риски

Exact-substring evidence подтверждает происхождение формулировки из
наблюдения, но не истинность источника и не логическую силу интерпретации.
Агрегированный профиль заказов не исследует оплаты и возвраты, не является
корпусом anomaly investigation. STEP-0012 — историческое наблюдение, не
текущая оценка надежности Analyst. Browser AX не равен реальному AT.

## Work log

2026-09-17: план создан после чтения todo 12 и текущего Analyst-кода, до
авторства лекции.
2026-09-18: content и browser/visual gates завершены, семь screenshots
осмотрены; две сборки идентичны, `make check` — 531 PASS. Evidence:
`plan/evidence/STEP-0043-lecture-analyst-provenance.md`.
