# STEP-0049 — Phase L: лекция 18, Airflow API и контролируемые операции

Status: complete

Owner: Codex

Updated: 2026-09-18

## Цель и границы

Написать theory-only лекцию 18: различить Airflow как планировщик data tasks
и агентский control plane; объяснить public REST `/api/v2` и отдельный
Task Execution API для выполнения задач; показать раздельные read-only Observer и approved
dev-DAG trigger с operation identity. Не повторять MCP-протокол (09),
idempotency как общую теорию (17) и threat model/authentication (19).
Runtime/Data Platform и paid models не менять.

Затрагиваемые пути: `course/lectures/`, module18/manifest/reviews/index,
`plan/steps/lections/`, `plan/evidence/`, course/plan status records.

## Порядок и критерии приёмки

- [x] Сверить Airflow S28 и AWS S12 с актуальной официальной документацией,
  observer/trigger code/policies и STEP-0014/0015 evidence; отделить
  historical live от текущих code boundaries.
- [x] Написать лекцию с причинной моделью двух оркестраторов, таблицей
  границ, approval/operation identity, Mermaid-диаграммой и 3–5 вопросами.
- [x] Выполнить отдельные editorial, technical, diagram semantics и recheck
  passes; сохранить schema-v2 content receipt с source anchors и hashes.
- [x] Проверить Markdown/links, candidate/static publication build; сохранить
  text-only publication receipt без screenshots/browser/visual/AX review.
- [x] Обновить todo/manifest/index/evidence; две production-сборки побайтно
  совпадают, `make check`, governance и `git diff --check` проходят.

## Риски и полномочия

API-first Airflow не означает, что REST может менять произвольный DAG/run.
Observer и Trigger имеют разные identity, profile и полномочия. Наличие
идемпотентного run ID не доказывает exactly-once при любой сетевой ошибке;
нужна сверка принятого результата. Разрешены локальные документы и
неплатные проверки; approvals не требуются.

## Work log

2026-09-18: план создан до авторства лекции.
2026-09-18: лекция опубликована, same-author content/publication receipts
сохранены. Candidate render повторён после непостоянного Mermaid CLI SIGSEGV
на старой диаграмме 05; два production output совпали. `make check`: 532
passed. [Evidence](../evidence/STEP-0049-lecture-airflow-operations.md).
