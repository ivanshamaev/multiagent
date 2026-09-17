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
