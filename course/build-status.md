# Статус сборки

## Реализовано

STEP-0025: manifest, 27 outlines, templates, sources и `make course-check`.
STEP-0026: ограниченный Markdown AST → Mermaid SVG → static HTML prototype.
STEP-0028: Cyberpunk landing, manifest-driven SVG roadmap и reader shell с программой
слева/AST TOC справа. 29 Markdown sources (27 outlines + две служебные страницы) дают
31 HTML-страницу; четыре Mermaid diagrams, отдельный linked roadmap и декоративная hero-схема.
Тексты лекций ещё не написаны и не публикуются. Diagram prototype сохранён как `prototype.html`.

`make course-renderer-install` устанавливает locked renderer и локальный Node;
`make course-build` пишет только allowlisted файлы в ignored `build/course/`.
`make course-preview` обслуживает их на http://127.0.0.1:8099/course/.
Нужны Python `.venv` (`make bootstrap`), npm и системный Noto Sans/fontconfig в Ubuntu.

## Проверки прототипа

SVG allowlist, scoped external CSS, уникальные IDs, CSP без unsafe-inline, pinned fonts
и toolchain/source fingerprints. Viewer: zoom, явно включаемые wheel/pointer/touch pan,
reset, keyboard, fullscreen/fallback, Escape и возврат фокуса. Без JS остаются SVG,
подпись и ссылка на отдельный SVG. Browser checks включают mobile/local scroll,
light/dark, print, кириллицу и геометрию labels. Commands/results — в
[STEP-0026 evidence](../plan/evidence/STEP-0026-static-course-prototype.md).
Новый layout и ссылки проверяются также в STEP-0028; build отклоняет duplicate IDs,
missing local targets/anchors. Страницы тем рендерятся из Markdown, как в изученном примере
`ai-agent-memory`; CDN/аналитика/inline scripts из него не переносились.
[STEP-0028 evidence](../plan/evidence/STEP-0028-cyberpunk-course-site-prototype.md):
515 tests PASS, 64 targeted PASS, две идентичные сборки и реальные UI/browser проверки.

## Ограничения и следующий этап

Это не publisher всех лекций. `prototype-verified` в [toolchain](toolchain.json)
не разрешает автоматически reviewed Mermaid lectures. После каждого текста нужны
редакторская вычитка, technical verification, визуальная проверка и recheck.

Byte reproducibility проверяется локально; CLI использует fingerprint системного Noto Sans,
поэтому переносимость между хостами не доказана. Проверен Chromium, не все browsers;
touch emulated, полного hardware/screen-reader audit и визуальной PDF-вычитки нет.
Renderer исполняет repository-owned sources, не произвольный недоверенный Mermaid.

Следующий authoring slice: пилотные тексты 00/03/08 с per-lecture review receipts;
полноценный publication pipeline — отдельный согласованный шаг. Это contributor workflow,
не лабораторная работа студента.

## STEP-0030: per-lecture publication gate

Предыдущие ограничения prototype superseded только в указанной области:
реализованы candidate build и reviewed-only reader с отдельным publication receipt.
Лекция 00 прошла полный local reader gate; остальные темы не публикуются автоматически.
Renderer теперь verified, а не гарантия проверки всех лекций. AX-разметка проверяется
автоматически, actual AT/hardware/cross-browser interoperability остаётся отдельно
записанным риском. [Evidence](../plan/evidence/STEP-0030-lecture-publication-gate.md).

## STEP-0031: лекция 01

В reader опубликованы полные тексты 00/01; 25 других тем остаются outlines.
Отдельные editorial/technical/recheck, actual render и browser/visual gates выполнены.
AX semantics не выданы за реальную проверку screen-reader взаимодействия.
Следующий текст по teaching order — 03: контракты и границы доверия.

## STEP-0032: лекция 03

Полный текст 03 опубликован после отдельных editorial/technical/recheck и
actual browser/visual passes. Reader содержит 00/01/03; другие 24 темы — outlines.
Schema validity, contextual binding и product correctness намеренно не смешиваются.
Следующая тема по teaching order — 04: harness и контекст одного вызова.

## STEP-0033: лекция 04

Полный текст 04 опубликован после отдельных editorial/technical/recheck и
actual browser/visual passes. Reader содержит 00/01/03/04; другие 23 темы — outlines.
Byte-лимиты ContextBundle не выданы за token accounting или semantic retrieval;
проверка структуры ответа не выдана за business acceptance. Реальное AT не тестировалось.
Следующая тема по teaching order — 17: state и memory.

## STEP-0034: последовательная нумерация

Нынешние core IDs 00–25 совпадают с порядком чтения; optional Kubernetes — 26.
Исторические записи выше используют номера, действовавшие в момент соответствующих
шагов. Опубликованные тексты теперь 00/01/02/03, следующая тема — 04 (state/memory).
Content/publication receipts переназначены после повторной вычитки и browser gate;
старые локальные `topic-NNNN.html` не считаются стабильными публичными ссылками.

## STEP-0035: лекция 04 — состояние и память

Полный theory-only текст опубликован после separate editorial/technical/recheck и
actual browser/visual passes. Показаны разные сроки жизни контекста, workflow state,
accepted artifact и возможного long-term knowledge; последний слой не реализован.
Reader содержит 00–04; 22 темы остаются outlines. Следующая — 05, MAF executors.
Actual AT/hardware touch/cross-browser audit не выполнен.

## STEP-0036: лекция 05 — MAF executors

Theory-only текст опубликован после отдельной вычитки, source/code verification
и actual browser/visual gate. Typed JSON boundary, executor/edge и проектное
понятие graph signature отделены от бизнес-перехода. Reader содержит 00–05;
21 тема остаётся outline. Следующая — 06, жёсткий workflow.

## STEP-0037: лекция 06 — жёсткий workflow

Theory-only текст опубликован после separate editorial/technical/recheck
и actual browser/visual gate. Safety/liveness и terminal convergence
отделены от executor delivery; rework не выдаётся за бесконечный retry.
Reader содержит 00–06, 20 тем остаются outlines. Следующая — 07,
model-directed agent-orchestrator.

## STEP-0038: лекция 07 — agent-orchestrator

Theory-only текст прошёл separate editorial/source/code/recheck и actual
browser/visual gate. Manager, task/progress ledgers и replanning описаны как
архитектурная альтернатива, не реализованный runtime. Reader содержит 00–07,
19 тем остаются outlines. Следующая — 08, изоляция среды исполнения.

## STEP-0039: лекция 08 — изоляция исполнения

Theory-only текст прошёл separate editorial/technical/recheck и actual
browser/visual gate. Визуальная неточность sandbox-схемы исправлена и
перепроверена. Reader содержит 00–08, 18 тем остаются outlines. Следующая —
09, MCP как интерфейс.

## STEP-0040: лекция 09 — MCP как интерфейс

Theory-only текст прошёл separate editorial/technical/recheck и actual
browser/visual gate. Нормативная версия MCP 2026-07-28 отделена от локального
SDK, объявляющего 2025-11-25; negotiation не назван авторизацией. После
визуальной ошибки flowchart схема заменена на sequence diagram и проверена
повторно. Reader содержит 00–09, 17 тем остаются outlines. Следующая — 10,
ограниченные аналитические SQL capabilities.

## STEP-0041: лекция 10 — ограниченный аналитический SQL

Theory-only текст прошёл separate editorial/technical/recheck и actual
browser/visual gate. Показаны границы metadata/profile/aggregate, AST policy,
права пользователя БД и несовпадение `LIMIT` с ценой исполнения. Первую
TD-схему заменили на LR после проверки mobile; финальные семь скриншотов
просмотрены. Reader содержит 00–10, 16 тем остаются outlines. Следующая —
11, dbt, lineage и семантика аналитической модели.

## STEP-0042: лекция 11 — dbt и семантика аналитической модели

Theory-only текст объясняет grain, dbt lineage, разные свидетельства
parse/compile/build/test и различие dbt-, Airflow- и agent-графов.
Content review и browser/visual gate завершены; семь скриншотов осмотрены.
Reader содержит 00–11, 15 тем остаются outlines. Следующая — 12,
Analyst и provenance фактов. Фактическое взаимодействие с screen reader
не проверено.

## STEP-0043: лекция 12 — Analyst и provenance фактов

Theory-only текст объясняет semantic discovery, привязку data fact к
наблюдению, границы агрегата и разделение facts/assumptions/questions.
Текущие три read phases и tool-free synthesis сверены с кодом, исторический
STEP-0012 не выдан за свежий live результат. Content и browser/visual
gates завершены, семь скриншотов осмотрены. Reader содержит 00–12,
14 тем остаются outlines. Следующая — 13, PM specification.

## STEP-0044: лекция 13 — PM и формальная спецификация

Theory-only текст отделяет business intent, наблюдаемые факты, нормативное
определение метрики и acceptance criteria. PM `READY` с полным контрактом
не смешан с историческим live `BLOCKED/needs_user`; human-authored сценарий
не выдан за ответ агента. Content и actual browser/visual gates завершены,
семь скриншотов осмотрены. Reader содержит 00–13, 12 тем остаются outlines.
Следующая — 14, DE и границы разрешённых изменений. Реальное AT не проверено.

## STEP-0045: лекция 14 — Data Engineer

Theory-only текст отделяет authority над реализацией от business contract,
показывает границу disposable dbt candidate, fan-out контрпример и repair
по public evidence. С этой лекции per-lecture gate v2 — text-only:
редакторская и техническая вычитка, сверка Mermaid source с прозой,
машинная сборка и hashes. Скриншоты, browser/visual review и AX не
выполнялись; визуальное качество не заявляется. Исторические receipts v1
сохраняют фактически выполненные проверки. Reader содержит 00–14,
11 тем остаются outlines. Следующая — 15, QA.

## STEP-0046: лекция 15 — QA

Theory-only текст объясняет разницу validator PASS и независимого QA-probe,
mutation/false pass, read-only identity и evidence-backed defect. Historical
sample 5/5 ограничен датой и corpus; общий blind spot oracle показан через
PRB-0035. Separate editorial/technical/recheck и text-only diagram semantics
зафиксированы в schema-v2 receipts. Candidate и две production-сборки прошли;
последние совпали побайтно (`7c20ed4606347b8fa3a70091e630704dcf954291e166e68943485547f3b8a98c`).
Скриншотов, browser/visual/AX review не было. Reader содержит 00–15,
10 тем остаются outlines. Следующая — 16, Reviewer.

## STEP-0047: лекция 16 — Reviewer

Theory-only текст отделяет quality/maintainability judgment от semantic QA,
объясняет code-owned review authority и запрет self-approval. Four-mutant
historical sample и canonical false rejection ограничены датой/configuration;
`APPROVE → DONE` не выдан за production merge/deploy. Separate editorial,
technical/recheck и Mermaid source review зафиксированы в schema-v2 receipts.
Candidate и две production-сборки прошли; последние совпали побайтно
(`6665f83a55ce82375916481a7c01c6969796ac72848b1aa309ceb980120cba92`).
Скриншотов, browser/visual/AX review не было. Reader содержит 00–16,
9 тем остаются outlines. Следующая — 17, Recovery.

## STEP-0048: лекция 17 — Recovery и idempotency

Theory-only текст разделяет MAF checkpoint, локальный role receipt и
idempotency внешнего эффекта, включая окна сбоя до/после receipt и
checkpoint. Исторические `SIGKILL` tests ограничены process/offline scope;
power-loss durability и exactly-once внешних сервисов не заявлены.
Schema-v2 editorial/technical/recheck и Mermaid source review сохранены.
Candidate и две production-сборки прошли; последние совпали побайтно
(`322e1dad43309c592a7ddf6c576ca4cd16f56c40b05d0cdf45ee8340a2d3dbc8`).
Скриншотов, browser/visual/AX review не было. Reader содержит 00–17,
8 тем остаются outlines. Следующая — 18, Airflow API.

## STEP-0049: лекция 18 — Airflow API

Theory-only текст разделяет Airflow DAG и agent workflow, public REST
`/api/v2` и Task Execution API, Observer и approved dev-DAG Trigger.
Historical STEP-0014/0015 ограничены локальным Airflow 3.3.1. Schema-v2
editorial/technical/recheck и Mermaid source review сохранены. Первый
candidate render получил непостоянный SIGSEGV на диаграмме темы 05;
повтор прошёл. Две production-сборки совпали побайтно
(`b24be0231fbc78b8609374229b858ec4f4507664e651912391f042e61fa21c01`).
Скриншотов, browser/visual/AX review не было. Reader содержит 00–18,
7 тем остаются outlines. Следующая — 19, Security.

## STEP-0050: лекция 19 — Security и полномочия

Theory-only текст разделяет untrusted content, authentication, role
assignment, authorization и approval authority. Локальный request-bound
bearer не назван OAuth, human/process attestation или one-time nonce;
manager-agent остаётся теоретическим сценарием. Schema-v2
editorial/technical/recheck и Mermaid source review сохранены. Candidate
и две production-сборки прошли; последние совпали побайтно
(`a2fa6496fe2bab2d15876d88f1af1bc95eaad7e2005fb364bfe7ef10217adff9`).
Скриншотов, browser/visual/AX review не было. Reader содержит 00–19,
6 тем остаются outlines. Следующая — 20, Observability.

## STEP-0051: лекция 20 — Observability

Theory-only текст разделяет trace, event log, metrics, artifact provenance
и private reasoning; объясняет restart carrier, post-sampling span metrics,
cardinality и retention. Dated STEP-0021/0023 ограничены offline и
historical single-host scope. Schema-v2 editorial/technical/recheck и
Mermaid source review сохранены. Candidate и две production-сборки прошли;
последние совпали побайтно
(`5ffc1c1479c5492b5e1de854c377bcc6b7c333977f0dd4b6527619e7c148b038`).
Скриншотов, browser/visual/AX review не было. Reader содержит 00–20,
5 тем остаются outlines. Следующая — 21, Evaluation.

## STEP-0052: лекция 21 — Evaluation

Theory-only текст определяет task/trial/outcome/grader, различает offline
regression invariants, датированные live samples и fresh comparisons.
`51/51` не выдан за независимые semantic tasks, а historical `7/10` — за
текущую надёжность модели. Schema-v2 editorial/technical/recheck и Mermaid
source review сохранены. Скриншотов, browser/visual/AX review не было.
Reader содержит 00–21, 4 темы остаются outlines. Следующая — 22,
Failure modes.

## STEP-0053: лекция 22 — Failure modes

Theory-only текст разделяет symptom, ошибочное состояние, activation
condition и root cause; классифицирует infrastructure/tool/workflow/
reasoning/policy причины и показывает common-mode correlation. PRB-0035,
0051 и 0052 разобраны как разные causal chains, а retry с backoff/jitter не
выдан за semantic или policy repair. Schema-v2 editorial/technical/recheck
и Mermaid source review сохранены. Скриншотов, browser/visual/AX review не
было. Reader содержит 00–22, 3 темы остаются outlines. Следующая — 23,
Cost/performance.

## STEP-0054: лекция 23 — Cost/performance

Theory-only текст отделяет provider token price от total cost и cost per
accepted outcome; объясняет critical path, parallel work, hierarchy budgets
и reservation/reconciliation. Cost-first capability gate не выдан за
полный optimizer, а EXP-0001/STEP-0009 — за текущие цены или SLO.
Schema-v2 editorial/technical/recheck и Mermaid source review сохранены.
Скриншотов, browser/visual/AX review не было. Reader содержит 00–23,
2 темы остаются outlines. Следующая — 24, Workflow vs agent-orchestrator.

## STEP-0055: лекция 24 — Workflow vs agent-orchestrator

Theory-only текст сравнивает четыре архитектурных кандидата по известности
декомпозиции, coupling, side-effect risk, audit/replay, cost/latency и
evaluation. Bounded hybrid ограничивает model-directed область read-only
исследованием; writes и gates остаются code-owned. Separate editorial,
technical/recheck и Mermaid source review сохранены в schema-v2 receipts.
Candidate static build прошёл; скриншотов и browser/visual/AX review не было.
Reader содержит 00–24; далее 25, architecture synthesis.

## STEP-0057: лекция 25 — Architecture synthesis

Theory-only текст собирает intent/evidence, control/contracts,
execution/capabilities и assurance/operations в одну evidence-bounded
архитектуру. Net Revenue walkthrough отделяет локальный `DONE` от
merge/deploy; code-enforced, offline-proven, historical-live и not-proven
claims разведены. Separate editorial, technical/recheck и Mermaid source
review сохранены. Candidate static build прошёл; скриншотов и
browser/visual/AX review не было. Reader содержит все core-лекции 00–25;
outline остаётся только у optional темы 26.

## STEP-0058: опциональная лекция 26 — Kubernetes и tenancy

Theory-only extension определяет tenant через trust model и сравнивает
namespace-per-tenant, virtual control plane и dedicated cluster. Identity/RBAC,
admission/seccomp, network, storage, quotas/cgroups и kernel boundary разведены
как разные enforcement layers. Локальный Bubblewrap/Compose baseline отмечен
`offline-proven`, Kubernetes — `not-implemented`. Separate editorial,
technical/recheck и Mermaid source review сохранены. Candidate и две
production-сборки прошли; последние совпали побайтно
(`87bf3367dcec915145a0f05c29d068b17f2f46d277b1f7ee8ae06a5e65019b36`).
Скриншотов, browser/visual/AX review не было. Reader содержит лекции 00–26.
