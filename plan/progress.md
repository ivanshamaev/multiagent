# Журнал прогресса

Записи добавляются по факту; планируемая работа сюда не попадает.

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
  суммарно 6 tools/8 model calls без write/policy violation. PROBLEM-0011 исправил `ordered_at` probe.
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
