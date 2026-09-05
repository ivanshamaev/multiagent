# План разработки Agentic Data Platform

## 1. Цель и граница проекта

Сначала строим и проверяем работающую multi-agent систему для инженерии данных. Только после стабильной версии превращаем реальные коммиты, traces, эксперименты, ошибки и исправления в практический курс. Курс не должен опираться на непроверенную теорию.

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
Pydantic contracts                 OTel Collector + Jaeger
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

### Phase L — Практический курс

Задачи: построить модули из ADR, commits, traces, problem records и experiments; для каждой темы дать theory, наблюдаемую проблему, реализацию, лабораторную работу, hidden checks и критерии сдачи.

Gate: каждая практическая глава ссылается на реально воспроизводимый scenario и доказанное инженерное решение.

## 6. Общая Definition of Done

Изменение считается завершённым, только если:

1. выполнены acceptance criteria активного шага;
2. запущены узкие и интеграционные проверки, сохранены exit codes;
3. обновлены `progress.md`, ADR и problem record при необходимости;
4. нет незаявленных изменений защищённых путей и секретов;
5. документация соответствует фактическому состоянию;
6. остаточные риски и следующий шаг явно записаны.

## 7. Текущая итерация

`STEP-0001…0005` завершены: governance, golden ClickHouse/dbt/Airflow+Cosmos и reproducible
scenario reset/run/hidden-grade lifecycle проверены; transcripts сохранены в `plan/evidence/`.
Активный `STEP-0006` реализует versioned Pydantic artifacts и deterministic state machine без LLM
calls. Только после его gate начинается local agent runtime.
