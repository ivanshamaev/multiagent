# STEP-0034 — Phase L: последовательная нумерация курса

Status: complete

Owner: Codex

Updated: 2026-09-16

## Goal и решение

ID каждой core-лекции должен совпадать с её позицией в teaching order: 00–25.
Единственная optional Kubernetes extension получает 26 и остаётся за пределами
core route. Slug и unique topic ownership неизменны; новый порядок — прежний
утверждённый маршрут, а не новая программа.

| Было | Стало | Тема |
| --- | --- | --- |
| 00 | 00 | agency |
| 01 | 01 | organization |
| 03 | 02 | contracts |
| 04 | 03 | harness/context |
| 17 | 04 | state/memory |
| 02 | 05 | MAF executors |
| 15 | 06 | strict workflow |
| 16 | 07 | agent-orchestrator |
| 05 | 08 | isolation |
| 06 | 09 | MCP interface |
| 07 | 10 | analytical SQL |
| 08 | 11 | dbt semantics |
| 11 | 12 | Analyst provenance |
| 10 | 13 | PM specification |
| 12 | 14 | DE |
| 13 | 15 | QA |
| 14 | 16 | Reviewer |
| 18 | 17 | recovery |
| 09 | 18 | Airflow operations |
| 19 | 19 | security |
| 20 | 20 | observability |
| 21 | 21 | evaluation |
| 22 | 22 | failure modes |
| 23 | 23 | cost/performance |
| 26 | 24 | comparison/hybrid |
| 25 | 25 | synthesis |
| 24 | 26 | optional Kubernetes |

## Scope, constraints и acceptance

- [x] Перенумеровать canonical manifest/map, prerequisites/related, Markdown paths,
  module directories, TODO plans, syllabus и active cross-links; оставить historical
  STEP/evidence filenames/содержимое неизменными.
- [x] Обновить course-check hardcoded optional ID; добавить regression test на
  contiguous teaching order и optional placement.
- [x] Переименовать/перепривязать четыре content/publication receipts без выдачи
  механической замены за независимую fact review.
- [x] Выполнить actual candidate/normal SVG/HTML builds, browser checks новых
  topic URLs, visual review изменённых номеров/ссылок, deterministic build diff.
- [x] `make check`, course policy tests, `make plan-check course-check`, link/receipt
  governance и `git diff --check` — PASS; evidence записано.

## Риски

Старые локальные URL `topic-0002/0003/0004...` меняют смысл: сайт до этого был
локальным preview, публичная обратная совместимость не заявлена. Не менять
системные STEP/ADR/PRB identifiers и исходный `init/` как исторические записи.
No Docker, paid LLM или student labs. После миграции нужно отдельно проверять
актуальность receipt digest: нельзя просто менять статус на reviewed.

## Completion

2026-09-16: миграция выполнена; полный regression suite 531 PASS, course policy
80 PASS. Четыре candidate reader gates и 28 просмотренных screenshots PASS;
обычные сборки 86 files/8 diagrams побайтово идентичны. Сохранён старый
generated `build/course` как `build/course-pre-step34`; основной preview 8099
отдаёт новые full-reader URL. [Evidence](../evidence/STEP-0034-course-sequential-numbering.md).
