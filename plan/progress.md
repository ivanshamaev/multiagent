# Журнал прогресса

## 2026-09-19 — STEP-0051: лекция 20 опубликована

- Написана теория trace causality, propagation через restart, различий
  traces/events/metrics/provenance и границ sampling/cardinality/retention.
- Separate editorial/technical/recheck, source-level Mermaid semantics и
  статическая сборка выполнены без screenshots/browser/visual review.
  Три minor findings исправлены; dashboard не выдан за evaluation.
- Две production-сборки (120 файлов, 25 диаграмм) совпали побайтно;
  `make check` — 532 passed. Reader содержит 00–20, далее 21, Evaluation.
  Evidence: [STEP-0051](evidence/STEP-0051-lecture-observability.md).

## 2026-09-19 — STEP-0050: лекция 19 опубликована

- Написана теория indirect prompt injection и границ identity,
  authorization, role assignment, approval; локальный HS256 bearer
  отделён от OAuth/процессной аттестации.
- Separate editorial/technical/recheck, source-level Mermaid semantics и
  статическая сборка выполнены без screenshots/browser/visual review.
  Три minor findings исправлены; model-directed manager не объявлен
  реализованным.
- Две production-сборки (118 файлов, 24 диаграммы) совпали побайтно;
  `make check` — 532 passed. Reader содержит 00–19, далее 20,
  Observability. Evidence: [STEP-0050](evidence/STEP-0050-lecture-security-authority.md).

## 2026-09-18 — STEP-0049: лекция 18 опубликована

- Написана теория Airflow data-task orchestration и агентского control plane,
  public REST и Task Execution API, раздельных Observer/Trigger identities и
  approval-bound dev-DAG запуска.
- Separate editorial/technical/recheck, source-level Mermaid semantics и
  статическая сборка выполнены без screenshots/browser/visual review.
  Первичный candidate render получил непостоянный SIGSEGV на старой схеме 05;
  повтор прошёл без изменения исходников.
- Две production-сборки (116 файлов, 23 диаграммы) совпали побайтно;
  `make check` — 532 passed. Reader содержит 00–18, далее 19, Security.
  Evidence: [STEP-0049](evidence/STEP-0049-lecture-airflow-operations.md).

## 2026-09-18 — STEP-0043: лекция 12 опубликована

- Написана теория semantic discovery, provenance фактов и пределов
  агрегированных наблюдений перед PM specification gate; пример сверён
  с текущим Analyst-кодом и датированным STEP-0012.
- Separate editorial/technical/recheck и фактический browser gate завершены;
  семь скриншотов осмотрены. Same-author review, actual AT не заявлен.
- Две идентичные сборки (104 файла, 17 SVG); reader содержит 00–12, далее
  лекция 13. Evidence: `plan/evidence/STEP-0043-lecture-analyst-provenance.md`.

## 2026-09-17 — STEP-0042: лекция 11 опубликована

- Написана теория grain, dbt lineage, уровней parse/compile/build/test и
  различия dbt/Airflow/agent-графов; пример сверён с кодом и STEP-0004.
- Separate editorial/technical/recheck и фактический browser gate завершены;
  семь скриншотов осмотрены. Same-author review, actual AT не заявлен.
- Две идентичные сборки (102 файла, 16 SVG); reader содержит 00–11, далее
  лекция 12. Evidence: `plan/evidence/STEP-0042-lecture-dbt-semantics.md`.

## 2026-09-17 — STEP-0037: лекция 06 опубликована

- Объяснены code-owned transition relation, safety/liveness, terminal
  convergence и bounded rework; graph v2 evidence не выдан за текущий live v3.
- Same-author editorial/technical/recheck и browser/visual gate PASS; семь
  screenshots просмотрены, actual AT не заявлен. Targeted workflow tests:
  30 PASS. Две обычные сборки и полный `make check` — в
  [evidence](evidence/STEP-0037-lecture-strict-workflow.md). Далее 07.

## 2026-09-17 — STEP-0036: лекция 05 опубликована

- Теория executor/edge/typed boundary/graph signature отделена от бизнес-transition
  лекции 06. Источники Microsoft/LangChain применены только в границах статей,
  STEP-0019 помечен как historical offline evidence.
- Same-author editorial/technical/recheck и browser/visual gates PASS; seven screenshots
  осмотрены, actual AT не заявлен. Targeted pipeline tests: 11 PASS.
- Две обычные сборки и полный `make check` — в
  [evidence](evidence/STEP-0036-lecture-maf-executors.md). Далее 06.

## 2026-09-17 — STEP-0035: лекция 04 опубликована

- Theory-only текст различает контекст вызова, workflow state, accepted artifact и
  не реализованный long-term memory layer; контрпример показывает потерю
  неявной оговорки при summarization.
- Separate editorial/technical/recheck и browser/visual passes; семь screenshots,
  исправлена несогласованность canonical заголовка. Контент и публикация имеют
  актуальные receipts; independent review и actual AT не заявлены.
- Targeted context/pipeline tests: 17 PASS. Две обычные сборки: 88 files/9 diagrams,
  идентичный SHA256. Полный `make check` и preview gate — в
  [evidence](evidence/STEP-0035-lecture-state-memory.md). Следующая лекция — 05.

## 2026-09-16 — STEP-0034 завершён: последовательная нумерация курса

- Основной маршрут получил ID 00–25 по порядку обучения; Kubernetes extension — 26.
  Историческое соответствие — [STEP-0034](steps/STEP-0034-course-sequential-numbering.md).
- Четыре опубликованных текста теперь 00/01/02/03. Проверены cross-links,
  prerequisites, исходные планы, четыре content/publication gates и новые URL.
- Старые локальные `topic-NNNN.html` меняют смысл; следующий текст по маршруту —
  04 о состоянии и памяти. [Evidence](evidence/STEP-0034-course-sequential-numbering.md).
- `make check`: 531 PASS; course policy: 80 PASS. Четыре browser gates и 28
  просмотренных screenshots PASS; обычные сборки 86 files/8 diagrams идентичны.

## 2026-09-16 — STEP-0033 завершён: лекция 04 опубликована

- Theory-only текст объясняет harness, отбор и представление контекста одного
  вызова, provider abstraction и границу structured response.
- Separate authoring/editorial/technical/recheck и actual browser/visual gates
  PASS; восемь claims и две исправленные minor findings записаны в receipts.
- `make check`: exit 0, 529 PASS; targeted runtime 40 PASS, course policy 78 PASS.
  Две обычные сборки: 86 files/8 diagrams, побайтово идентичны.
- [Evidence](evidence/STEP-0033-lecture-harness-context.md). Preview 8099 доступен;
  actual AT остаётся непроверенным. Следующая по teaching order — лекция 17.

## 2026-09-16 — STEP-0032 завершён: лекция 03 опубликована

- Theory-only текст разделяет syntax/schema/invariants/context/product correctness,
  объясняет versioning, immutability, evidence и пределы task/actor binding.
- Separate authoring/editorial/technical/recheck и actual browser/visual gates PASS;
  16 claims, две исправленные minor findings и честный actual-AT gap в receipts.
- Targeted contracts/workflow/adversarial: 36 PASS. Две обычные сборки: 84 files,
  7 diagrams, одинаковый SHA256; final `make check` и course suite — в evidence.
- [Evidence](evidence/STEP-0032-lecture-contracts.md). Preview 8099 сохранён;
  следующий текст — 04, harness и контекст одного вызова.

## 2026-09-15 — STEP-0031 завершён: лекция 01 опубликована

- Theory-only текст: ответственность и capability, ownership, task coupling,
  цена координации и separation of duties; profiles и условный Net Revenue case.
- Отдельные authoring/editorial/technical/recheck passes, primary sources и
  browser/visual gate; две minor findings исправлены, финальный текст перечитан.
  Лекция 00 перепроверена после уточнения статуса forward links.
- `make check`: exit 0, 529 PASS. Обе lecture/content publication receipts актуальны;
  82 files/6 diagrams, две обычные сборки побайтово идентичны.
- [Evidence](evidence/STEP-0031-lecture-organization.md). Preview 8099 доступен;
  actual AT/hardware touch/cross-browser не проверены. Далее — лекция 03.

## 2026-09-15 — STEP-0030 завершён: local publication gate

- Candidate build изолирован; обычный reader выбирает только reviewed с актуальными
  content/publication receipts, actual renderer fingerprint и body+TOC hash.
- Лекция 00 опубликована на стабильном topic URL; roadmap/sidebar/TOC различают
  планы и тексты. Проверены renderer/SVG, keyboard/fullscreen/Escape/focus, print,
  mobile/no-JS, AX names/descriptions, subpath/CSP/links и screenshots.
- `make check`: 529 PASS; post-publication course suite: 78 PASS; две обычные сборки
  побайтово идентичны. [Evidence](evidence/STEP-0030-lecture-publication-gate.md).
- Actual Orca/NVDA/VoiceOver не запускались; AX не выдаётся за AT interaction.
  Preview 8099 работает; следующий STEP-0031 — лекция 01 по утверждённому плану.

## 2026-09-15 — STEP-0029 завершён: пилотная теоретическая лекция 00

- Написан полный Markdown текст: agency, reasoning/action/observation, agent loop,
  частичная видимость, bounded stopping, контрпример и tool-free PM illustration.
  Нет лабораторных работ; соседние темы имеют forward references к primary owners.
- Три обязательных skills применены автором в отдельных authoring/editorial/technical
  проходах и полном recheck. ReAct/Anthropic сверены с primary sources; текущий PM
  отделён от historical-live STEP-0007. Receipt связывает 12 claims с inputs/hashes.
- Фактический render/sanitizer и browser diagram checks сохранены; полный graph
  визуально проверен в print layout. Final lecture reader/screen-reader gate не выполнен:
  статус technically-verified, не reviewed; полный текст пока не опубликован.
- PRB-0058 исправляет hardcoded «не написан» для authored text без публикации draft.
  Final `make check`: exit 0, 519 PASS; `make course-build`, governance и diff check PASS.
- [Evidence](evidence/STEP-0029-pilot-lecture-agentic-baseline.md). Preview 8099 восстановлен,
  HTTP 200; временный diagram-only сервер 8098 остановлен. Следующий этап — publication
  gate пилотной лекции, затем лекция 01 по teaching_order.

## 2026-09-15 — STEP-0028 завершён: Cyberpunk course prototype

- Landing, linked SVG roadmap и каталог 27 тем; AST Markdown reader с программой слева,
  TOC справа, canonical pager и mobile/no-JS disclosure navigation.
- Изучен read-only `ai-agent-memory` builder; перенесены shared-shell/TOC/link-check идеи,
  не CDN/аналитика. Outlines не объявлены лекциями; review gates сохранены.
- `make check`: exit 0, 515 PASS; targeted course suite: 64 PASS. Две сборки идентичны,
  browser/visual checks PASS, PRB-0056/0057 закрыты.
- [Evidence](evidence/STEP-0028-cyberpunk-course-site-prototype.md). Preview оставлен доступным
  на loopback 8099; следующая content работа требует отдельного authoring step.

## 2026-09-15 — STEP-0027 завершён: фиксация дизайна сайта

- Сохранены Cyberpunk / Glitch reference и [specification](../course/design/site-design.md), ADR-0038.
- Главная landing; далее module/lecture pages; SVG roadmap; course menu слева, lecture TOC справа.
- Определены tokens, typography, responsive layout и readability adaptations эффектов.
- `make plan-check course-check` и `git diff --check`: exit 0.
  [Evidence](evidence/STEP-0027-course-site-design-specification.md).
- Это документационная фиксация, не реализация нового UI; существующий preview не менялся.

## 2026-09-15 — STEP-0026 завершён: SVG/static HTML prototype

- Locked Mermaid CLI и локальный Node, AST builder, SVG/CSS validation, allowlisted output,
  строгий CSP и loopback preview; четыре диаграммы и три HTML-страницы.
- Две сборки побайтово совпали; browser checks и визуальная проверка PASS.
- `make check`: exit 0, 504 passed; targeted course tests: 53 passed.
- [Evidence](evidence/STEP-0026-static-course-prototype.md); PRB-0053/0054/0055 исправлены.
- Тексты лекций/publication gate не реализованы; следующий slice — пилотное authoring
  с обязательными per-lecture вычиткой, technical verification и recheck.

Записи добавляются по факту; планируемая работа сюда не попадает.

## 2026-09-15 — STEP-0025 завершён: теоретический каркас

- Созданы 27 outlines, manifest/syllabus/sources/glossary/templates и editorial skills.
- AST/offline course checker включён в Make/check; 28 новых regression tests.
- PyPI и источники восстановились; pinned parser установлен в .venv/uv.lock.
- `make check`: exit 0, 479 passed. [Evidence](evidence/STEP-0025-theory-course-scaffold.md).
- Полные лекции и SVG/HTML renderer не реализованы; публикационный review не заявляется.

## 2026-09-15 — STEP-0025: технические требования к лекциям

- ADR-0036: Mermaid в Markdown, SVG при сборке, общий HTML-компонент для просмотра.
- Созданы `course/technical-requirements.md` и todo-проверки во всех 27 планах.
- Проверены 32 документа/275 ссылок; plan governance PASS, 3 tests PASS.
- [Evidence](evidence/STEP-0025-lecture-technical-requirements.md): build/render ещё не реализованы.

## 2026-09-15 — STEP-0025: проверка индивидуальных todo-планов

- Подготовлены 27 планов и отдельная директория `course/lectures/` с README; тексты не написаны.
- Проверены 81 уникальная concept area, prerequisites и 259 ссылок; governance PASS, 3 tests PASS.
- Сохранено [evidence](evidence/STEP-0025-lecture-todo-source-planning.md); STEP-0025 остаётся in progress.

## 2026-09-04 — Инициализация проекта

- Проверены `init/init_build_multi_agent_system.md` и `init/init_cource_plan.md`; подробный build-план принят как основной implementation backlog, course plan — как целевое педагогическое представление.
- Проверено окружение: Ubuntu, Python 3.12.3, Docker 28.1.1, Docker Compose 2.35.1, GNU Make 4.3.
- Установлен `uv 0.12.9` в `/home/ivan/.local/bin` официальным standalone installer.
- Принята гибридная runtime-модель: agents/orchestrator локально в `.venv`; Data Platform в Docker Compose.
- Созданы структура `plan/`, подробный roadmap и начальные ADR.
- Проверен GateLLM `/v1/models` без вывода секрета; принят `inclusionai/ling-2.6-flash` как текущий cheapest CHAT default, с обязательным capability gate перед agent calls.
- Первый bootstrap-шаг завершён; актуальный active step указан ниже.

## 2026-09-04 — STEP-0001 завершён

- Созданы `pyproject.toml`, `uv.lock`, Python 3.12 `.venv`, Ruff/pytest config и канонические package-каталоги.
- Созданы Docker Compose/Make interfaces и ClickHouse 25.8.33.6 с loopback ports и healthcheck.
- Детерминированный seed создаёт 7 raw-таблиц и edge cases: cancellations, currencies, split payments, partial/multiple/late refunds, NULL channels и duplicate attribution.
- Пройдены `uv sync --frozen`, `make check` (5 tests), `make seed`, `make platform-test`; повторный seed/build state успешен.
- Зафиксированы и закрыты PRB-0001…PRB-0003.
- Следующий активный шаг: `STEP-0002-dbt-baseline.md`.

## 2026-09-05 — STEP-0002 завершён

- Добавлен одноразовый dbt runner в Docker Compose; Python image закреплён digest, Core/adapter и все transitive dependencies закреплены версиями и hashes.
- Реализованы 7 raw sources, 4 staging views, 2 intermediate views и 2 MergeTree marts без вычисления Net Revenue.
- Добавлены 68 generic/singular tests и независимый ClickHouse smoke с точными counts/aggregates.
- Пройдены `dbt debug → parse → compile → build → test`, повторный build без reset и полный reseed/build; persistent summary — `plan/evidence/STEP-0002-dbt-baseline.md`.
- Исправлены и закрыты PRB-0004…PRB-0008; deprecated Core 1.10 заменён проверенной связкой Core 1.11.14 + adapter 1.10.2, generated dbt user id удалён из repository state.
- Следующий активный шаг: `STEP-0003-airflow-baseline.md`.

## 2026-09-05 — STEP-0003 завершён

- Airflow 3.3.1 и PostgreSQL 16.15 запущены в Docker; images закреплены digest, LocalExecutor ограничен двумя процессами. API Server, Scheduler и Dag Processor имеют healthchecks.
- DAG `ecommerce_hourly` использует public Task SDK и исполняет цепь шести marker tasks. Фактический dbt execution ещё не реализован; следующий STEP-0004 посвящён этой интеграции.
- API smoke проверяет 401 без JWT, authenticated access, component health, exact task dependencies и success всех шести task instances. Два свежих run IDs сохранены в STEP-0003 transcript.
- Независимый review обнаружил дефекты HTTP/polling/error handling в проверяющем скрипте; fixes и regression tests записаны в PRB-0009.
- Пройдены `make -s platform-up`, `make -s airflow-test`, повторный `make -s airflow-init`, `make -s platform-test`; все exit 0. `make check` — Ruff, 20 pytest и Compose PASS.
- STEP-0002 повторно проверен после evidence audit: fresh full transcript, source checksum, timestamps, 76 build results/68 tests и independent SQL assertions сохранены.
- `API_TOKEN` отсутствует в resolved Compose config и actual Data Platform containers. GateLLM completion calls не выполнялись. Существующие Docker volumes и чужие образы не удалялись.
- Актуальный следующий шаг: `STEP-0004-airflow-dbt-execution.md` (planned). Остаток диска после pull — около 2.3 GiB; перед следующим image build проверить повторно.

## 2026-09-05 — STEP-0004 завершён

- По уточнению пользователя custom dbt runner заменён Astronomer Cosmos 1.15.0; решение и migration rationale записаны в ADR-0011 и PRB-0010.
- Cosmos `DbtTaskGroup` строит dbt lineage из восьми моделей и запускает единый `AFTER_ALL` test gate через изолированный dbt virtualenv. Scheduled DAG остаётся paused; acceptance использует manual twin.
- Три API runs завершились 11/11 success и прошли independent SQL. Negative Cosmos test дал `dbt_tests=failed`, `publish=upstream_failed`; baseline не изменился.
- `make platform-test` подтвердил raw assertions, 68 dbt tests и mart assertions. `make check` — 32 tests; API_TOKEN отсутствует в Data Platform.
- Persistent summary и transcript: `plan/evidence/STEP-0004-airflow-cosmos.md`. Следующий активный шаг: `STEP-0005-scenario-harness.md`.

## 2026-09-05 — STEP-0005 завершён

- Добавлены versioned manifest/schema и transactional allowlisted snapshot для `net-revenue`;
  основной checkout, `.env`, `.git`, planning/runtime и grader source в workspace не попадают.
- Два полных reset дали одинаковые source/workspace/ClickHouse fingerprints и baseline dbt result.
- Public `scenario-run` отделён от hidden grader. Grader работает non-root, read-only, без Docker
  socket/API token и только во внутренней сети ClickHouse; baseline ожидаемо имеет `INCOMPLETE`.
- 60 pytest checks покрывают traversal, symlink, unmanaged target, protected edit, stale source,
  contamination recovery и isolation policy. PRB-0012 исправил mode managed workspace.
- `make platform-test` после network change: Airflow/Cosmos 11/11 success, 68 dbt tests и SQL PASS.
- Evidence: `plan/evidence/STEP-0005-scenario-harness.md`. LLM calls и удаление volumes не выполнялись.
- Следующий активный шаг: `STEP-0006-contracts-state-machine.md`.

## 2026-09-06 — STEP-0006 завершён

- Реализованы frozen/closed Pydantic v1 contracts для request, specification, analysis,
  implementation, validation, QA, review и content-addressed evidence.
- Pure reducer проверяет полную transition matrix, role/task/authorship gates и bounded budgets;
  исчерпанный rework детерминированно заканчивается `FAILED` без превышения лимита.
- Canonical hash chain обнаруживает mutation, reorder, replay и truncation относительно ожидаемого
  state. MAF/provider SDK не связан с domain contracts.
- `make check` — 101 tests; scenario fingerprints воспроизведены; isolated baseline grader PASS;
  `make platform-test` — Airflow/Cosmos 11/11, dbt 68/68 и SQL PASS.
- Evidence: `plan/evidence/STEP-0006-contracts-state-machine.md`. LLM calls не выполнялись.
- Следующий активный шаг: `STEP-0007-local-agent-runtime.md`.

## 2026-09-06 — STEP-0007 завершён

- Добавлен GateLLM provider через pinned MAF Chat Completions adapter: secret-safe settings,
  bounded retries/timeouts, cost/config model selection, schema capability probe и fake transport.
- Controlled PM Agent читает только проверенный content-addressed scenario context, формирует
  строгий draft и передаёт artifact/usage существующему reducer; prompts/raw responses не хранятся.
- Cost comparison выявил 404/504/schema failures дешёвых моделей; Llama 3.1 8B прошла полный smoke
  за ~0.02583 ₽ и зафиксирована как датированный PM default (PRB-0013–0016, EXP-0001).
- `make check` — 129 tests; scenario fingerprints и baseline grader воспроизведены;
  `make platform-test` — Airflow/Cosmos 11/11, dbt 68/68 и SQL PASS.
- Evidence: `plan/evidence/STEP-0007-local-agent-runtime.md`. Следующий активный шаг:
  `STEP-0008-tool-policy-layer.md`.

## 2026-09-11 — STEP-0008 завершён

- Официальные ClickHouse/dbt MCP изолированы в pinned stdio containers; ClickHouse identity имеет
  только SELECT на `raw.*`/`analytics.*`, а dbt работает только с verified scenario project.
- Typed contracts, SQLGlot AST gate, capability profile, atomic workspace adapter, cumulative MCP
  budgets и content-addressed evidence образуют deny-by-default boundary вне prompts.
- MAF видит только локальный facade; invalid arguments и policy denial завершают loop через
  `MiddlewareFailure`. Live smoke прошёл query + dbt compile/test и отклонил DDL до MCP.
- После восстановления удалённых Docker images: Airflow/Cosmos 11/11, dbt 68/68, scenario и grader
  воспроизведены; `make check` — 210 tests. PRB-0017–0020 сохраняют найденные проблемы и fixes.
- Evidence: `plan/evidence/STEP-0008-tool-policy-layer.md`. Следующий planned шаг:
  `STEP-0009-autonomous-data-engineer.md`.

## 2026-09-11 — STEP-0009 в работе: control-plane slice

- Human-authored Net Revenue specification зафиксирована по scenario version и SHA-256 `TASK.md`;
  identity, evidence и workflow transitions исключены из model-owned draft.
- Data Engineer получает verified/delimited context и 13 profile tools. Workspace и official MCP
  вызовы теперь используют единый serialized tool/wall/output ledger.
- Bounded MAF tool loop и code-owned artifact assembly доводят offline execution до `IMPLEMENTED`;
  self-reported completion без фактического dbt diff закрывается как `FAILED`.
- `make check` — 227 tests, Ruff/format и Compose validation PASS. Платные LLM calls не выполнялись.
- Следующий блок STEP-0009: независимый deterministic validator и negative fixtures.

## 2026-09-11 — STEP-0009 в работе: independent validator

- Добавлены closed four-gate validator и независимый Net Revenue SQL contract вне agent workspace.
  Agent-reported success не влияет на решение; только exit codes открывают `VALIDATED` или bounded
  `REWORK`, а infrastructure error приводит к `FAILED`.
- Baseline корректно отклонён новым SQL gate; реальный workspace-integrity gate прошёл и сохранил
  content-addressed evidence. Secret и process-injection environment variables отфильтрованы.
- `make check` — 234 tests, Ruff/format и Compose validation PASS. Следующий блок — связать MAF
  tool loop, artifact assembly и validator в единый offline execution.

## 2026-09-12 — STEP-0009 в работе: offline end-to-end executor

- Один MAF workflow теперь связывает tool-enabled reasoning, реальный isolated workspace facade,
  cumulative ledger, reducer-owned artifacts и independent validator.
- Offline run выполнил два реальных workspace tools, дошёл до `VALIDATED` через fake model/validator
  и восстановил baseline. GateLLM и MCP containers в этом тесте не вызывались.
- PRB-0021 зафиксировал и закрыл конфликт handler `execute` с MAF framework dispatch; regression
  suite — 35 tests. Следующий шаг — минимальный live GateLLM + official MCP run.

## 2026-09-12 — STEP-0009 в работе: live gates и failure taxonomy

- Добавлен opt-in live runner с составным schema/tool capability gate, cost/config fingerprints,
  приватными terminal records и безопасной типизацией zero-tool/framework failures.
- Granite Micro прошла schema gate, но не tools; Llama 3.1 8B прошла оба. Zero-tool run измерил
  3821 tokens и 0.058836 ₽ и был корректно отклонён. Следующие attempts доказали реальные MCP calls,
  policy denials и сохранение terminal evidence без prompts/raw responses.
- HTTP 400 после двух успешных tool rounds независимо воспроизведён минимальным прямым `ping`;
  bounded поиск альтернативы остановлен на HTTP 429. PRB-0022—0026 и EXP-0002 сохраняют выводы.
- Составной selector продолжает cost-order после schema-capable/tool-incapable кандидата. Полный
  `make check && git diff --check` — exit 0, `243 passed`, Compose config valid.
- Следующий блок: phased fresh-conversation execution с cumulative budget/evidence, затем повторный
  live candidate, independent validator и hidden grade.

## 2026-09-12 — STEP-0009 в работе: phased execution

- ADR-0019 разделил Data Engineer на три свежих least-privilege conversation phases при одном
  cumulative gateway ledger. Offline slice: 3 model calls, 3 tool calls, 45 tokens, два changed
  dbt files и deterministic transition до `VALIDATED`.
- Live fan-out из 80 calls закрыт `parallel_tool_calls=false`, exact phase evidence и budget 6
  (PRB-0027). Несовместимый provider schema mode после tool history удалён только для tool phases;
  closed Pydantic validation сохранена (PRB-0028).
- Последняя попытка выполнила ровно один разрешённый `TASK.md` read и остановилась на GateLLM 429.
  Повторные платные calls отложены до снятия rate limit; следующий gate — live candidate и validator.
- `make check && git diff --check` — exit `0`: Ruff/format, `246 passed`, Compose config valid.

## 2026-09-12 — STEP-0009 в работе: bounded rework и repeat-run readiness

- Public validator failure теперь запускает fresh one-write repair с текущим candidate и
  content-addressed diagnostics; повторный validator определяет результат. Один fail исправляется,
  а после двух rework attempts reducer гарантированно завершает workflow как `FAILED`.
- Добавлены минимальные phase-specific draft schemas, безопасная telemetry invalid output и
  однозначное извлечение schema-valid JSON из decoration без сохранения raw response.
- Успешные schema/tool probes кешируются на час только при неизменном полном catalog fingerprint;
  cache имеет mode 0600 и сокращает repeat run на два provider requests. Последний uncached run
  создал cache, но был остановлен внешним HTTP 429; workspace остался baseline-clean.

## 2026-09-12 — STEP-0009 в работе: первый live validated candidate

- GPT-5.4 Nano и GPT-5.6 Luna прошли live schema/tool gates; дешёвые DeepSeek/Poolside/Nemotron
  candidates не прошли строгую schema boundary. Явный VISION route поддержан без расширения
  автоматического CHAT-only выбора.
- Phase-specific context и bounded validator head+tail устранили token overflow и потерю root cause.
  Regression suite — 12 tests. PRB-0031 фиксирует defect и repair routing.
- Fresh GPT-5.6 Luna run: 3 calls/tools, 17 370 tokens, 34 209 ms, 1.946100 ₽; все public validator
  gates и isolated hidden grader PASS. Модель provisional до завершения 10-run sample.
- Повреждённая часть только `system.metric_log` точечно удалена после ClickHouse checksum failure;
  volumes/raw/analytics сохранены, baseline снова green (PRB-0032).

## 2026-09-12 — STEP-0009 завершён

- Fixed Luna sample дал 8/10 public и 7/10 end-to-end hidden passes без policy violations или
  protected-path changes; median успешных public runs — 17 330.5 tokens, 34 843 ms и 1.940130 ₽.
- Два разрешённых repair приведены в соответствие с bounded budget: ceiling 42k. Post-fix run
  `3b0b2556cfdf` прошёл public validator и все пять hidden checks после одного repair.
- Финальные gates: `make check` — 252 tests; MCP smoke PASS с ожидаемым DDL denial; scenario
  reproducibility PASS; Airflow/Cosmos 11/11, dbt 68/68 и platform SQL PASS; secret/diff scans PASS.
- Evidence: `plan/evidence/STEP-0009-autonomous-data-engineer.md`. Следующий milestone — Phase G,
  QA Agent и mutation-driven quality loop.

## 2026-09-12 — STEP-0010 начат

- Создан подробный план read-only QA quality loop: trust boundary, evidence ownership, mutation
  corpus, обязательная повторная public validation после DE repair и fail-closed regression gates.
- Reviewer отделён от этого шага, чтобы сначала независимо доказать цикл
  `VALIDATED → QA FAIL → DE REWORK → validator → QA PASS`.

## 2026-09-12 — STEP-0010 завершён

- Независимый `qa_v1` работает в двух свежих read-only phases; code-owned probe, evidence и reducer
  исключают model-owned SQL, transitions и self-approval.
- GPT-5.6 Luna: canonical PASS, все 5/5 прошедших public validator mutations отклонены QA; false
  pass 0/5. QA дополнительно нашёл реальный NULL/`argMax` defect canonical-кандидата.
- Live workflow `quality-net-revenue-20260912161215` доказал одну DE-запись, два полных validator
  run и конечный `QA_PASSED`; 39,466 tokens, rework 1/2.
- Финальные gates: `make check` 280 tests; MCP smoke, reproducibility, baseline grader,
  Airflow/Cosmos 11/11, dbt 68/68, canonical dbt 78/78, public SQL и hidden grader PASS.
- Evidence: `plan/evidence/STEP-0010-qa-quality-loop.md`. Следующий шаг — read-only Reviewer gate.

## 2026-09-12 — STEP-0011 начат

- Создан план завершения Phase G: отдельная Reviewer identity, exact acceptance coverage,
  read-only evidence, false-approval mutations и обязательный возврат через validator и QA.
- ADR-0021 закрепил, что только code-owned `ReviewReport` и reducer могут открыть `DONE`;
  Reviewer не совмещается с DE/QA и не получает write, execution или hidden grader access.

## 2026-09-13 — STEP-0011 завершён

- Reviewer реализован двумя fresh read-only phases с exact acceptance coverage и code-owned
  evidence/identity/budget/transitions; invalid output и shared rework exhaustion закрываются.
- Offline полный цикл доказывает `QA PASS → review fail → DE repair → validator → QA → review PASS`.
- GPT-5.6 Luna одобрил canonical и отклонил 4/4 maintainability mutations: false approval 0/4.
  GPT-5.4 Nano false-rejected canonical и исключён для этой роли по PRB-0037.
- Финальные gates: `make check` 305 tests; MCP, reproducibility, baseline grader, Airflow/Cosmos
  11/11, dbt 68/68, canonical 78/78, public SQL и hidden grader PASS.
- Evidence: `plan/evidence/STEP-0011-reviewer-approval-gate.md`. Phase G завершена; следующий этап —
  Phase H, read-only Analyst и requirements pipeline.

## 2026-09-13 — STEP-0012 запланирован

- Зафиксирован подробный план pre-PM requirements discovery: immutable `TaskRequest`, read-only
  Analyst, evidence-backed facts/lineage/profiling и typed handoff в будущий PM gate.
- Перед реализацией требуется ADR о миграции текущего порядка state machine с
  `SPEC_READY → ANALYZING` на `TaskRequest → Analyst → PM`, без ослабления downstream gates.
- Scope STEP-0012 заканчивается проверенным Analyst artifact/handoff; PM reasoning будет отдельным
  STEP-0013.

## 2026-09-13 — STEP-0012 завершён

- ADR-0022 и reducer перенесли discovery перед PM; новый `RequirementsAnalysisReport` не смешивается
  с техническим DE `AnalysisReport`, а прямой обход Analyst/PM gate запрещён.
- `analyst_v1` выполняет три fresh read-only MCP phase и tool-free synthesis. Facts принимаются
  только как точные excerpts успешного same-task evidence; typed handoff сохраняет unknowns.
- GPT-5.6 Luna прошёл canonical и ambiguous-metric: 25 facts в каждом, 9 open questions во втором,
  суммарно 6 tools/8 model calls без write/policy violation. PRB-0042 исправил `ordered_at` probe.
- Финальные gates: `make check` 322 tests; MCP smoke, reproducibility, baseline grader,
  Airflow/Cosmos 11/11, ClickHouse и dbt 68/68 — PASS.
- Evidence: `plan/evidence/STEP-0012-analyst-requirements-discovery.md`. Следующий шаг — STEP-0013,
  PM specification gate, принимающий только validated requirements handoff.

## 2026-09-13 — STEP-0013 завершён

- ADR-0023 удалил compatibility discovery: PM принимает только matching `PMRequirementsHandoff`,
  `ANALYSIS_READY` state и проверенную hash-chain; workspace context и tools ему не выдаются.
- `TaskSpecification` получил typed `needs_user`. Код запрещает PM превращать unresolved Analyst
  questions в `ready` или менять их; IDs, identity, timestamps, budgets и transition остаются у
  control plane.
- Offline gates доказали READY и BLOCKED paths, malformed output, budget exhaustion, chain replay,
  cross-task/workflow/artifact, identity collision и prompt injection. Полный suite: 328 tests.
- Live GPT-5.6 Luna pipeline `requirements-net-revenue-canonical-05ebaff6e8c8` завершился ожидаемым
  `BLOCKED/needs_user`: 22 facts, 9 questions, 3 tools, 5 model calls, 17,671 tokens, 1.932360 ₽.
- Airflow/Cosmos 11/11, dbt 68/68, ClickHouse, MCP, reproducibility и baseline hidden grader gates
  прошли. Evidence: `plan/evidence/STEP-0013-pm-specification-gate.md`. Phase H завершена;
  следующий этап — STEP-0014, read-only Airflow MCP поверх `/api/v2`.

## 2026-09-13 — STEP-0014 завершён

- Реализованы шесть closed read-only Airflow tools поверх фиксированных `GET /api/v2` endpoints:
  DAG, run, task-instance и один bounded task-attempt log; произвольные URL/method/body отсутствуют.
- `airflow-observer-v1` ограничен тремя локальными DAG, cumulative budgets и отдельным FAB Viewer;
  credentials/JWT не попадают в tool arguments, output или evidence, sensitive API fields удалены.
- Live smoke: три allowlisted DAG, восемь Viewer calls/evidence, реальный Cosmos run 11/11 success и
  неизменные before/after metadata. PRB-0038 и PRB-0039 закрыты regression tests.
- Финальные gates: `make check` 350 tests; ClickHouse/dbt MCP, scenario reproducibility, baseline
  grader и `make platform-test` PASS. Evidence: `plan/evidence/STEP-0014-read-only-airflow-mcp.md`.
- Phase I продолжается отдельным controlled dev-DAG trigger; текущий observer останется read-only.

## 2026-09-13 — STEP-0015 завершён

- Отдельный trigger MCP/profile/FAB user разрешает только approved запуск `ecommerce_acceptance`;
  observer не получил write-функций, а credentials и JWT не входят в аргументы или evidence.
- Одноразовый mode-0600 approval связывает task/DAG/idempotency key/approver/expiry. Стабильный
  code-owned run ID, preflight GET и reconciliation исключают дубликат при retry/timeout.
- Live gate доказал `created → existing` для одного run и 11/11 success; paused-состояние manual DAG
  восстановлено. PRB-0040/0041 фиксируют реальные особенности FAB CLI и paused DAG.
- Финальные gates: `make check` 371 tests; observer/MCP, scenario, grader и platform PASS. Evidence:
  `plan/evidence/STEP-0015-controlled-dev-dag-trigger.md`. Phase I завершена; далее Phase J.

## 2026-09-13 — STEP-0017 Kimi audit завершён

- Все F-01…F-22 внешнего аудита сверены с post-STEP-0015 кодом и получили явную диспозицию.
- `.env` теперь 0600 и защищён bootstrap gate; ClickHouse закреплён digest. Исправлены PRB/ADR
  индексы, статусы, коллизия имени, STEP-0001 evidence и фактические runbooks.
- ADR-0026 подтвердил происхождение HTTPX2 из Pydantic/OpenAI stack. `make plan-check` автоматически
  проверяет ключевые инварианты planning ledger; QA assert и Reviewer tuple mismatch исправлены.
- `make check` — 374 tests; scenario, grader и полный platform gate PASS. Крупная герметизация
  tests/identities/runtime helpers явно перенесена в Phase J, coverage — в Phase K.

## 2026-09-13 — STEP-0018 начат

- ADR-0027 выбрал MAF-native checkpoint semantics за hardened repository adapter вместо второго
  custom workflow runtime; untrusted checkpoint ingestion остаётся запрещённым.
- Реализованы contained 0700/0600 storage, UUID/symlink/mode/size/create-only gates и fail-closed
  restore. Двухстадийный graph сохраняет pending message после первого superstep.
- Первый `make checkpoint-smoke` прошёл реальный `SIGKILL → new process → resume`: обе стадии
  вызваны ровно один раз, output восстановлен из iteration-1 checkpoint. Focused suite — 6 PASS.

## 2026-09-13 — STEP-0018 завершён

- Hardened MAF checkpoint adapter отклоняет escape/symlink/loose mode/malformed/incompatible graph,
  хранит UUID records create-only под 0700/0600 и не регистрирует application pickle types.
- Два реальных `SIGKILL → restart → resume` gate подтвердили iteration 1, сохранённый pending
  message и ровно один вызов каждой стадии; committed stage не началась с task zero.
- Финальные gates: `make check` 381 tests; scenario/grader и Airflow/Cosmos/dbt/SQL platform PASS.
  Следующий Phase J slice — декомпозиция реального role pipeline по checkpointable typed handoffs.

## 2026-09-13 — STEP-0019 завершён

- Happy-path `Analyst → PM → DE → Validator → QA → Reviewer` разложен на шесть stable MAF
  executors; entry и каждая завершённая роль создают checkpoint iterations 0…6.
- Typed immutable snapshot пересекает checkpoint boundary только как canonical JSON. На каждом hop
  заново проверяются stage, task/workflow identity, reducer event hash-chain, artifact order и
  неизменность принятой истории; application pickle types не разрешались.
- Реальный `SIGKILL` при входе Validator и resume iteration 3 в новом процессе завершились `DONE`;
  счётчики всех шести ролей равны 1, поэтому Analyst/PM/DE не стартовали повторно.
- Финальные gates: `make role-pipeline-test` — 4 passed; `make check` — 386 tests; Docker Compose
  контейнеры не запускались и остаются остановленными. Evidence:
  `plan/evidence/STEP-0019-checkpointable-role-pipeline.md`.
- Следующий Phase J slice — branching/rework с idempotency незавершённой роли, затем OTel tracing.

## 2026-09-14 — STEP-0020 завершён

- Six-role graph v2 использует native MAF switch/case: PM/DE terminal outcomes завершаются сразу,
  Validator/QA/Reviewer rework возвращается только в DE, `DONE|BLOCKED|FAILED` сходятся в terminal.
- Immutable `gate_history` сохраняет прошлые implementation и gate artifacts; reducer event-chain,
  общий rework budget и hard limit 32 supersteps ограничивают циклы независимо от model output.
- Owner-only `SecureRoleReceiptStore` связывает результат с workflow/executor/revision/input hash.
  Atomic create-only receipt даёт cache hit при повторе и отклоняет escape/symlink/mode/hash/collision.
- SIGKILL после DE receipt, но до MAF checkpoint, затем resume с iteration 2 завершился `DONE`; все
  role counters равны 1. Targeted suite — 13 passed; полный `make check` — 395 passed.
- Evidence: `plan/evidence/STEP-0020-branching-rework-idempotency.md`. Далее — OTel tracing, затем
  runner identity и filesystem/network/MCP isolation.

## 2026-09-14 — STEP-0021 завершён

- Explicit OpenTelemetry provider связывает `workflow → role → model/tool/artifact`; typed carrier
  сохраняет trace/workflow span IDs в checkpoint snapshot и восстанавливает parent после restart.
- Closed façade экспортирует IDs, stages, operation/receipt state, token usage, latency, statuses и
  hashes, но не prompts, completions, arguments/results, exception messages/stacks или credentials.
- Owner-only JSONL exporter отклоняет unknown spans/attributes, escape, symlink, loose modes и
  bounded-file overflow. PRB-0043 исключил повторный artifact span при receipt replay.
- `make telemetry-test` — 48 passed; `make check` — 406 passed; Docker Compose пуст. Evidence:
  `plan/evidence/STEP-0021-opentelemetry-trace-chain.md`. Далее — runner identity и isolation.

## 2026-09-14 — STEP-0022 завершён

- Пять strict profiles задают отдельные role runner/actor/UID и связываются с существующими
  capability profiles. Bubblewrap создаёт user/PID/IPC/UTS/network namespaces без fallback.
- Реальный hostile subprocess доказал zero network, отсутствие `.env`, checkout, Docker socket и
  чужих mounts; PM не видит workspace, read-only roles не пишут, DE меняет только два dbt subtree.
- Role-facing MAF connections теперь подписывают каждый canonical request короткоживущим bearer;
  gateway проверяет runner/profile/role/actor/task/audience/request hash до tool policy/adapter.
- Закрыты PRB-0044…0046: Base64URL malleability, writable ephemeral directory shell и неверный
  host-scoped `RLIMIT_NPROC`. `make runner-isolation-test` — 16 passed; `make check` — 422 passed.
- Evidence: `plan/evidence/STEP-0022-runner-and-mcp-isolation.md`. Далее — operational telemetry
  backend/metrics, затем Phase K.

## 2026-09-14 — STEP-0023 завершён

- Explicit local OTLP/HTTP exporter отправляет content-free spans в pinned Collector без global
  provider/env instrumentation. Tail policy всегда хранит errors и выбирает 25% healthy traces.
- Spanmetrics экспортирует только low-cardinality role/model/tool/stage/receipt dimensions. Tempo
  хранит local blocks 72h, Prometheus — 7d/1GB; Grafana provisioned двумя datasource и read-only
  operational dashboard.
- Два live smoke с сохранёнными volumes нашли error traces, fresh `keep-errors` counters и
  Prometheus metrics, подтвердили два healthy scrape target и Grafana provisioning без LLM/token.
  PRB-0047…0049 фиксируют Tempo schema, Docker port и persisted-series defects.
- Evidence: `plan/evidence/STEP-0023-operational-observability-backend.md`. Phase J завершена;
  следующий этап — Phase K evaluation benchmark.

## 2026-09-15 — STEP-0024 завершён

- ADR-0033 разделяет offline invariants и dated live model-quality provenance. Добавлены 17
  versioned cases × 3 повтора, strict baseline, configuration fingerprint, failure taxonomy и
  owner-only sanitised reports. Historical baseline индексирует 24 прошлых live attempts;
  свежие LLM/Data Platform вызовы не выполнялись.
- PRB-0050 исправил pytest naming collision; PRB-0051 сериализует shared-fixture Make targets;
  PRB-0052 исправил checkpoint publication-before-chmod через private staging и atomic create-only
  publication. Reader permission checks и model/quality assertions не ослаблены.
- Два final post-fix samples: 51/51 PASS каждый, одинаковый актуальный fingerprint; 13 targeted
  benchmark tests и 7 checkpoint/recovery tests PASS. `make check`: exit 0, 451 tests PASS,
  Ruff/format, governance и Compose PASS. Контейнеры остановлены, volumes сохранены.
- Evidence: `plan/evidence/STEP-0024-phase-k-evaluation-benchmark.md`; experiment EXP-0005.
  Далее Phase L — практический курс из подтверждённых engineering decisions/evidence. При смене
  модели/prompts/tools перед выводами о качестве нужен отдельный budgeted fresh live sample.

## 2026-09-15 — STEP-0025: спланирован каркас Phase L

- Полностью прочитан `init/init_cource_plan.md`; сохранены номера 0–25 и единый ecommerce project.
  План: 24 core modules, extensions 16/24, 89 estimated student hours (25 theory / 64 practice),
  source-index, manifest, glossary, templates, rubric/capstone и offline metadata checker.
- Сопоставлены implementation/evidence anchors; отражены фактический Analyst-before-PM pipeline,
  local Bubblewrap вместо agent containers, read-only QA/tool-free PM и отдельный Airflow trigger.
- A2A/dynamic teams, Kubernetes, skills/memory, CLV и automated merge/release не объявлены
  реализованными. Offline orchestration, platform и paid opt-in labs разделены; historical live
  rates не выдаются за fresh model quality или live six-role READY.
- Использован `technical-markdown-lectures` для будущего lesson template и педагогического цикла;
  полные лекции и scaffold в этом запросе не создавались. STEP-0025 остаётся активным.
- Следующее действие — реализовать каркас по checklist STEP-0025, начиная с ADR-0034, затем
  проверить metadata/links/statuses. Planning evidence хранится отдельно от verification будущих labs.

## 2026-09-15 — STEP-0025: theory-only revision по уточнению пользователя

- Прежний practical plan superseded: убраны labs, student setup/assignments, grading, paid tracks
  и capstone-задание; 89-hour theory/practice estimate снят. ID 25 — архитектурный синтез.
- Цель — глубокая теория с нашей системой как примером. ADR-0034 сохраняет evidence-based принцип,
  но заменяет учебные practice/grading требования ADR-0007; исходный `init/` не изменён.
- Skills: доступный `technical-markdown-lectures`; planned `technical-editorial-review` и
  `technical-claim-verification` требуют отдельной подготовки через `skill-creator` перед авторством;
  `openai-docs` условно используется для утверждений именно об OpenAI. Новые skills не установлены.
- После каждой лекции обязательны полная вычитка, technical verification, исправления и recheck.
  Review records привязаны к content hash; stale/missing records не допускают reviewed.
- Обновлены step/roadmap/status. Лекции/scaffold не создавались, другой reviewer не привлекался;
  утверждение о независимой вычитке не делается. STEP-0025 остаётся активным.
- 2026-09-15, дополнение: созданы 27 per-lecture todo-планов в `plan/steps/lections/`, index,
  topic ownership/prerequisite map и 30 первичных статей. Тема 16 стала core manager-agent flow;
  добавлена 26 — comparison/hybrid с десятью scenarios. Тексты будут в `course/lectures/`.
  Skill `technical-markdown-lectures` помог согласовать структуру и переходы. Лекции не написаны,
  semantic duplication review будущих текстов и применение отсутствующих skills не заявляются.

## 2026-09-17 — STEP-0038: лекция 07

Опубликована theory-only лекция об agent-orchestrator после отдельной вычитки,
source/code verification и визуального publication gate. Manager-flow прямо
обозначен как не реализованный в платформе. Две сборки совпали побайтно,
`make check` — 531 passed. Reader содержит 00–07; далее 08.

## 2026-09-17 — STEP-0039: лекция 08

Опубликована теория локальной изоляции после отдельной вычитки и проверки
исходных статей, кода и offline evidence. Визуальная ошибка в схеме была
выявлена браузерным gate, исправлена и перепроверена. Две сборки совпали,
`make check` — 531 passed. Reader содержит 00–08; далее 09.

## 2026-09-17 — STEP-0040: лекция 09

Опубликована theory-only лекция о MCP host/client/server, lifecycle и
semantic tool surface. Текущая нормативная спецификация 2026-07-28 не
приравнена к установленному SDK 2025-11-25. После вычитки и source/code
verification визуальная ошибка в диаграмме исправлена и повторно проверена
в браузере. Content/publication receipts актуальны; две сборки совпали,
`make check` — 531 passed. Reader содержит 00–09; далее 10.

## 2026-09-17 — STEP-0041: лекция 10

Опубликована theory-only лекция об аналитическом read scope и составном
SQL resource envelope. Текст прошёл отдельные editorial/technical/recheck,
а финальная LR-схема — actual browser/visual gate после исправления
мобильного layout. Content/publication receipts актуальны, две сборки
совпали побайтно; 53 профильных теста и `make check` (531 tests) PASS.
Во время проверки временно не хватало места на разделе; после очистки
восстановимого npm-кэша browser gate повторно прошёл. Reader содержит
00–10; далее 11, dbt semantics.

## 2026-09-18 — STEP-0044: лекция 13

Опубликована theory-only лекция о формальной спецификации показателя,
readiness и допустимом NEEDS_USER. Отдельные editorial/technical/recheck,
28 профильных тестов и actual Chrome visual gate завершены. Исторический
live BLOCKED не выдан за READY; семь скриншотов осмотрены, две сборки
совпали побайтно. Reader содержит 00–13, 12 тем остаются outlines.
Следующая — 14, DE. Промежуточные публикации 11–12 учтены в
[STEP-0042](steps/STEP-0042-lecture-dbt-semantics.md) и
[STEP-0043](steps/STEP-0043-lecture-analyst-provenance.md).

## 2026-09-18 — STEP-0045: лекция 14

Опубликована theory-only лекция о границах реализации DE, disposable dbt
candidate и semantic repair на примере Net Revenue. Separate editorial,
technical и recheck passes завершены; Mermaid сверена только по исходному
тексту, подписи и текстовому эквиваленту. Новый gate v2 не требует
скриншотов/визуальной вычитки и запрещает fake visual PASS; исторические
v1 receipts сохранены. Две статические сборки совпали побайтно,
`make check` — 532 passed. Reader содержит 00–14; далее 15, QA.

## 2026-09-18 — STEP-0046: лекция 15

Опубликована theory-only лекция о независимом QA-probe, мутациях,
свидетельствах дефекта и пределах PASS после validator. Исторические
5/5 и общая ошибка candidate/oracle не выданы за гарантию качества.
Separate editorial/technical/recheck и Mermaid source review выполнены
только по тексту, без скриншотов или browser/visual проверки. Две
production-сборки совпали побайтно; `make check` — 532 passed. Reader
содержит 00–15; далее 16, Reviewer. Подробности:
[evidence](evidence/STEP-0046-lecture-qa-evidence.md).

## 2026-09-18 — STEP-0047: лекция 16

Опубликована theory-only лекция о read-only Reviewer, качестве изменения,
праве одобрить локальный workflow и рисках false approval/rejection.
Отдельные editorial/technical/recheck и Mermaid source review выполнены
только по тексту, без скриншотов или browser/visual проверки. Две
production-сборки совпали побайтно; `make check` — 532 passed. Reader
содержит 00–16; далее 17, Recovery. Подробности:
[evidence](evidence/STEP-0047-lecture-reviewer-authority.md).

## 2026-09-18 — STEP-0048: лекция 17

Опубликована theory-only лекция о checkpoint, role receipt, operation
identity и пределах exactly-once. Процессные `SIGKILL` доказательства
не выданы за гарантию внешних эффектов или power-loss durability.
Separate editorial/technical/recheck и Mermaid source review выполнены
только по тексту, без скриншотов или browser/visual проверки. Исправлена
ссылка на owner operation identity в outline 18. Две production-сборки
совпали побайтно; `make check` — 532 passed. Reader содержит 00–17;
далее 18, Airflow API. Подробности:
[evidence](evidence/STEP-0048-lecture-recovery-idempotency.md).

## 2026-09-19 — STEP-0052: лекция 21

Опубликована theory-only лекция об evaluation как измерительной системе:
task/trial/outcome/grader, единицы успеха, baseline и неопределённость.
Offline `17 × 3`, исторический live sample и fresh A/B comparison явно
разделены; `51/51` не выдан за 51 независимую задачу, а `7/10` — за
постоянное свойство модели. Separate editorial/technical/recheck и Mermaid
source review выполнены только по тексту. Две production-сборки совпали;
`make check` — 532 passed. Reader содержит 00–21; далее 22, Failure modes.
Подробности: [evidence](evidence/STEP-0052-lecture-evaluation.md).

## 2026-09-19 — STEP-0053: лекция 22

Опубликована theory-only лекция о symptom/root-cause distinction,
propagation и retry amplification. Infrastructure/tool/workflow/reasoning/
policy taxonomy показана как пересекающаяся инженерная модель; PRB-0035,
0051 и 0052 разобраны через common-mode blind spot, shared fixture и race
window. Backoff с jitter не выдан за исправление permanent defect. Separate
editorial/technical/recheck и Mermaid source review выполнены только по
тексту. Reader содержит 00–22; далее 23, Cost/performance. Подробности:
[evidence](evidence/STEP-0053-lecture-failure-taxonomy.md).

## 2026-09-19 — STEP-0054: лекция 23

Опубликована theory-only лекция о total cost, cost per accepted outcome,
critical path и иерархии budgets. Provider token price отделён от tools,
infrastructure, coordination, human work и failed attempts; parallel work —
от latency. Cost-first capability gate ограничен своим реальным scope, а
EXP-0001/STEP-0009 сохранены как датированные measurements. Separate
editorial/technical/recheck и Mermaid source review выполнены только по
тексту. Reader содержит 00–23; далее 24, orchestration comparison.
Подробности: [evidence](evidence/STEP-0054-lecture-cost-performance.md).

## 2026-09-19 — STEP-0055: лекция 24

Опубликована theory-only лекция о выборе между code-owned workflow,
agent-orchestrator, bounded hybrid и более простой реализацией. Topology,
control ownership, authority и transport разведены; десять DE-сценариев
сопоставлены по единой rubric. External observations ограничены исходными
settings, а manager/hybrid — статусом `not-implemented`. Separate
editorial/technical/recheck и Mermaid source review выполнены только по
тексту. Reader содержит 00–24; далее 25, architecture synthesis.
Подробности: [evidence](evidence/STEP-0055-lecture-orchestration-comparison.md).
