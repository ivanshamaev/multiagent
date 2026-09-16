# План разработки Agentic Data Platform

## 1. Цель и граница проекта

Сначала строим и проверяем работающую multi-agent систему для инженерии данных. По уточнению
пользователя Phase L создаёт глубокий теоретический курс без лабораторных и практики; наша система,
traces, эксперименты и ошибки иллюстрируют принципы. Реализация примера и общие теоретические
утверждения имеют отдельную provenance; после каждой лекции обязательны вычитка и перепроверка.

Первая значимая цель:

> В воспроизводимой среде один Data Engineer Agent автономно добавляет метрику Net Revenue в dbt/ClickHouse и проходит детерминированный validator и независимый hidden grader.

Следующая цель — добавить QA Agent, который обнаруживает ошибочную реализацию, формирует доказанный defect и запускает ограниченный rework loop.

## 2. Runtime-модель

Система разделена на два контура:

```text
Ubuntu host                         Docker Compose
────────────────────────────       ───────────────────────────
uv + .venv                         ClickHouse
Microsoft Agent Framework          dbt runner
orchestrator/runtime/agents         Airflow + PostgreSQL
Pydantic contracts                 OTel Collector + Tempo + Prometheus + Grafana
pytest/evals/scenario harness       изолированная сеть и volumes
```

Локальный runtime ускоряет разработку и debugging. Data Platform остаётся контейнеризованной и воспроизводимой. Интеграция проходит только через явные API, CLI или MCP interfaces.

## 3. Неподвижные инженерные принципы

- Workflow кодом определяет порядок, gates, retries, approvals и завершение; LLM выбирает только способ выполнения разрешённого шага.
- В MVP агенты обмениваются typed artifacts через workflow и не вызывают друг друга напрямую.
- Agent statement не равен evidence. Проверка хранит команду/запрос, exit code, timestamp и ссылку на output.
- Permissions работают по принципу deny-by-default; hidden graders и policy code недоступны рабочему агенту.
- Сначала golden baseline и scenario reset, затем агент.
- Ошибки платформы, tools, workflow и reasoning классифицируются отдельно.
- В MVP не добавляем Kubernetes, memory, A2A и dynamic teams до появления измеренной необходимости.

## 4. Зависимости этапов

```text
Governance → Golden Data Platform → Scenario Harness
                                      ↓
Contracts → Workflow → Runtime → Tool Policies → DE Agent
                                                ↓
Validator → Hidden Grader → QA → Reviewer → Analyst → PM
                                                ↓
Airflow tools → Reliability → Observability → Isolation → Evals
                                                            ↓
                                                     Course design
```

## 5. Этапы и контрольные точки

### Phase 0 — Governance и repository bootstrap

Задачи:

- P00.1: создать `plan/`, правила журналирования, ADR/problem/experiment templates.
- P00.2: зафиксировать runtime boundary, архитектурные инварианты и Definition of Done.
- P00.3: создать `Claude.md`, `README.md`, `.gitignore`, `.env.example` и `Makefile`.
- P00.4: установить `uv`, создать Python 3.12 `.venv`, `pyproject.toml` и `uv.lock`.
- P00.5: создать канонические каталоги без преждевременной бизнес-логики.

Gate: новый checkout получает локальное окружение одной командой; документация не выдаёт планируемые компоненты за готовые; базовые lint/test команды имеют однозначный результат.

### Phase A — Golden Data Platform

Задачи:

- A01: Docker Compose project, сеть, healthchecks, именованные volumes и dev-only credentials.
- A02: ClickHouse с зафиксированной версией и минимальными правами.
- A03: детерминированный ecommerce seed: customers, orders, items, payments, refunds, sessions, attribution.
- A04: edge cases — partial/multiple refunds, split payments, cancelled orders, late events, NULL channels, currencies, duplicates и timezone boundaries.
- A05: dbt layers `staging → intermediate → marts`; Net Revenue намеренно отсутствует.
- A06: dbt schema/business tests и SQL correctness tests.
- A07: Airflow 3 baseline DAG `ecommerce_hourly` с API-first управлением.
- A07b: подключить фактические dbt transformations/tests к Airflow с изолированными dependencies; marker DAG недостаточен для завершения Phase A.
- A08: единый Make-интерфейс и сохранение test evidence.

Gate:

```bash
make platform-up
make seed
make dbt-build
make platform-test
```

Все команды завершаются с exit code `0` на чистом состоянии.

### Phase B — Scenario Harness

Задачи: описать scenario manifest, воспроизводимый reset данных/репозитория/state, isolated task workspace, run/grade команды и immutable hidden expected results.

Gate: два последовательных `scenario-reset` дают одинаковые checksums данных, git state и baseline test results; `scenario-run` не получает доступ к grader.

### Phase C — Contracts и deterministic workflow

Задачи: реализовать Pydantic-контракты `TaskRequest`, `TaskSpecification`, `AnalysisReport`, `ImplementationResult`, `QAReport`, `ReviewReport`, `Evidence`; затем state machine, допустимые transitions, rework и жёсткие лимиты попыток.

Gate: unit/property tests отклоняют невалидные artifacts, недопустимые transitions, отсутствие evidence и превышение retry budget.

### Phase D — Local Agent Runtime

Задачи: подключить Microsoft Agent Framework code workflow, GateLLM/OpenAI-compatible model-provider abstraction, structured output, context builder, worktree manager, middleware и append-only event log. `API_TOKEN` поступает только из локального ignored `.env`; default model выбирается cost-first и повышается лишь по результатам eval.

Gate: один controlled agent выполняет синтетическую задачу в отдельном workspace, выдаёт валидный artifact и не меняет защищённые пути.

### Phase E — Tool и policy layer

Задачи: read-only ClickHouse MCP, ограниченный dbt interface, capability profiles, file/network allowlists, time/token/tool budgets и evidence для каждого tool call.

Gate: разрешённые read/build операции работают; ClickHouse write, grader access, protected-file edit и неразрешённая сеть стабильно отклоняются policy tests.

### Phase F — Milestone 1: Autonomous Data Engineer

Задачи: зафиксированный human-authored spec Net Revenue, DE instructions, implementation contract, repair loop, deterministic validator и hidden grader. Validator выполняет `dbt parse`, `compile`, `build`, `test`, `pytest`, SQL correctness и repository-policy tests.

Gate: не менее 10 чистых прогонов; отдельно считаются task success, hidden-test pass rate, policy violations, retries, latency, tokens и cost. Запрещено улучшать grader ради прохождения агента.

### Phase G — Milestone 2: Quality loop

Задачи: read-only QA Agent, независимые probes, defect evidence, `QA FAIL → DE REWORK`; затем read-only Reviewer с проверкой acceptance coverage, security и maintainability.

Gate: намеренно ошибочная реализация проходит полный цикл `DE → validator → QA fail → DE fix → QA pass → review`; false QA pass и false approval измеряются на наборе мутантов.

### Phase H — Requirements pipeline

Задачи: Analyst исследует lineage и semantics без записи; PM превращает vague request в `TaskSpecification`, фиксирует assumptions/open questions и выдаёт `BLOCKED_NEEDS_USER`, когда данных недостаточно.

Gate: система либо формирует полный проверяемый spec, либо объяснимо блокируется; выдуманные требования ловятся evals.

### Phase I — Airflow integration

Задачи: собственный Airflow MCP поверх stable `/api/v2`: сначала metadata/logs, затем controlled dev-DAG trigger; прямой доступ к metadata DB запрещён.

Gate: агент диагностирует и валидирует pipeline, не получает production write и не обходит API/policy layer.

### Phase J — Reliability, observability и isolation

Задачи: checkpoints/resume, timeout/retry budgets, crash recovery, OTel traces для workflow/model/tool, dashboards, отдельные runners/credentials, filesystem/network isolation и MCP auth.

Gate: kill/restart продолжает работу с последнего checkpoint; trace связывает task → stage → model/tool call → artifact; adversarial tests не пересекают trust boundaries.

### Phase K — Evaluation и regression benchmark

Задачи: минимум 10 сценариев, repeated-run protocol, metrics, failure taxonomy, prompt/tool-output poisoning и permission-escalation tests. Любое изменение prompt/model/tool сравнивается с baseline статистически, а не субъективно.

Gate: воспроизводимый evaluation report содержит configuration fingerprint, число прогонов, success/safety/quality/cost metrics и разбор regressions.

### Phase L — Глубокий теоретический курс

Задачи: объяснить модели, инварианты, архитектурные альтернативы и ограничения multi-agent систем;
использовать нашу Data Platform как сквозной пример с ADR/traces/PRB/EXP/evidence. Лабораторные,
практические задания и student grading исключены. Для каждой лекции выполнить редакторскую вычитку,
техническую перепроверку и повторную проверку исправлений с persistent review record.

Gate: каждая лекция даёт связную глубокую теорию, проверенные источники и корректно подписанные
примеры; reviewed разрешён только после обоих проходов без существенных unresolved замечаний.

## 6. Общая Definition of Done

Изменение считается завершённым, только если:

1. выполнены acceptance criteria активного шага;
2. запущены узкие и интеграционные проверки, сохранены exit codes;
3. обновлены `progress.md`, ADR и problem record при необходимости;
4. нет незаявленных изменений защищённых путей и секретов;
5. документация соответствует фактическому состоянию;
6. остаточные риски и следующий шаг явно записаны.

## 7. Текущая итерация

`STEP-0001…0014` завершены: governance, golden ClickHouse/dbt/Airflow+Cosmos, reproducible scenario
harness, contracts/workflow, controlled GateLLM runtime, deny-by-default tools и autonomous Data
Engineer milestone проверены. Phase G завершена: независимые QA и Reviewer, обязательный bounded
rework через повторные validator/QA gates, QA mutation detection 5/5 и Reviewer false approval 0/4
сохранены в `plan/evidence/`. Phase H завершена: read-only Analyst формирует evidence-backed handoff,
а tool-free PM принимает только этот artifact и детерминированно выбирает полный spec или
`blocked / needs_user`. Phase I завершена: GET-only observer и отдельный controlled trigger работают
поверх `/api/v2`; trigger требует одноразовый approval, использует детерминированный run ID и
отдельную least-privilege identity. STEP-0018 завершил MAF-native hardened checkpoint storage и
process-kill/resume proof. STEP-0019 разложил happy-path `Analyst → PM → DE → Validator → QA →
Reviewer` на шесть MAF executors с typed JSON boundaries и доказал restart после DE без повторного
запуска завершённых ролей. STEP-0020 добавил native branching, bounded rework, terminal convergence
и durable role receipts, исключающие повтор handler после post-result/pre-checkpoint crash.
STEP-0021 добавил один content-free OTel trace через workflow/role/model/tool/artifact, persisted
trace carrier и hardened JSONL exporter. STEP-0022 добавил пять отдельных Bubblewrap runner
identities, zero-network/capability-derived filesystem boundary и request-bound authentication во
всех role-facing MCP connections. STEP-0023 завершил Phase J: OTLP Collector применяет tail
sampling и строит metrics, Tempo/Prometheus ограничивают retention, а Grafana получает provisioned
read-only dashboard. STEP-0024 реализует Phase K versioned offline benchmark (17 cases × 3), strict
baseline, fingerprint и historical live provenance. Offline PASS не заменяет fresh model-quality
sample при смене модели/prompts/tools. Далее — Phase L: теоретический курс из подтверждённых evidence.

Завершённый STEP-0025 реализует каркас Phase L: 26 core topics и extension 24,
source-index, lecture/review templates, editorial Skills и Net Revenue как архитектурный пример. План учитывает исходный
`init/init_cource_plan.md`, но не переносит неподтверждённые A2A/Kubernetes/CLV/merge promises.
На 2026-09-15 созданы course documents, 27 outlines, templates, skills и offline checker;
`make course-check` входит в `make check` (STEP-0025: 479 tests PASS). Тексты ещё не созданы;
STEP-0026 реализует отдельный allowlisted SVG/HTML prototype с реальными browser checks,
не publisher всех лекций. Дальше — пилотное authoring с обязательными per-lecture review gates.
Уточнение пользователя и ADR-0034 отменяют прежние практические треки и оценку часов: цель
каркаса — теория, обязательная вычитка и техническая перепроверка после каждой лекции.
ADR-0035 добавляет равноценное рассмотрение code-owned workflow и agent-orchestrator и отдельное
сравнение/гибрид. Созданы 27 todo-планов в `plan/steps/lections/`; тексты предназначены для
`course/lectures/`. Карта topic ownership и первичные статьи подготовлены, лекции ещё не написаны.
STEP-0027 принял Cyberpunk landing/roadmap/reader дизайн. STEP-0028 реализует его в локальном
static prototype: страницы описаний тем из Markdown outlines, не публикация полных лекций.
Программа сохраняет teaching_order manifest; roadmap/navigation/TOC не дублируют curriculum.
STEP-0029 добавляет полную пилотную лекцию 00 с отдельными editorial/technical/recheck
и diagram-render проверками. Остальные 26 текстов ещё не написаны. Публикационный
gate реализован в STEP-0030: verified pinned renderer, isolated candidate,
отдельные content/publication receipts, полный reader, фактический browser и visual review.
AX semantics проверены, реальное взаимодействие с screen reader — нет; scope указан явно.
STEP-0031 публикует лекцию 01 о role decomposition/task coupling/separation of duties
после отдельных editorial/technical/recheck и reader passes. Лекции 00/01 доступны;
25 прочих текстов ещё не написаны. Следующая тема по teaching_order — лекция 03.
STEP-0032 публикует лекцию 03 о contracts/artifacts/trust boundaries после
content и actual reader gates. Reader содержит 00/01/03; 24 текста остаются outlines.
Следующая тема по teaching_order — лекция 04 о harness/context одного вызова.
STEP-0033 публикует лекцию 04: отбор и представление контекста одного вызова,
provider abstraction и границы structured response. История памяти, recovery и
стоимость остались за владельцами 17/18/23. Reader содержит 00/01/03/04;
23 текста остаются outlines. Следующая тема по teaching_order — лекция 17.
STEP-0034 сохраняет те же темы и порядок, но синхронизирует ID с позицией:
core 00–25 и optional Kubernetes 26. Прежние IDs остаются в таблице миграции;
четыре опубликованных текста после перепроверки теперь имеют ID 00/01/02/03.
Следующая тема — 04, state/memory.
