# Claude.md

## Назначение и источники истины

Репозиторий создаёт проверенную multi-agent систему для Data Engineering, а затем практический курс на основе реальных решений, экспериментов и ошибок. Документы `init/` описывают целевую архитектуру и syllabus, но не доказывают наличие реализации.

Порядок приоритетов: явная задача пользователя → `AGENTS.md` и этот файл → принятые ADR в `plan/decisions/` → активный шаг в `plan/steps/` → исполняемый код/config → исходные материалы `init/`. Архитектурный конфликт не разрешай молча: зафиксируй его и создай/обнови ADR.

## Обязательное ведение `plan/`

До нетривиального изменения создай или обнови активный `plan/steps/STEP-NNNN-short-name.md`. Он обязан содержать:

- status, owner, updated и ровно один current step;
- goal и non-goals;
- affected layers и разрешённые пути;
- acceptance criteria;
- risks, permissions и approvals;
- пошаговый checklist;
- verification commands, ожидаемые и фактические результаты;
- decisions/problems и датированный work log.

Отмечай шаг выполненным только после проверки. После работы обновляй `plan/progress.md`. Новое архитектурное решение фиксируй до реализации в `plan/decisions/ADR-NNNN-short-name.md`. Нетривиальную или повторяемую проблему фиксируй в `plan/problems/PRB-NNNN-short-name.md`; закрывать системную проблему без regression check нельзя. Эксперименты храни в `plan/experiments/` вместе с scenario checksum, configuration fingerprint, числом прогонов и метриками. Не записывай secrets, private data и полный model output.

## Архитектурные инварианты

Сохраняй четыре слоя:

```text
workflow/control plane → agents/reasoning → MCP/tools → Data Platform
```

- Workflow кодом определяет стадии, transitions, retry limits, approvals и Definition of Done. LLM определяет только способ выполнения разрешённой стадии.
- Requirements path: `TaskRequest → Analyst → PM → Data Engineer`. Analyst подтверждает data
  facts, PM владеет business semantics, а readiness остаётся решением reducer.
- В MVP взаимодействие агентов: `agent → typed artifact → workflow → next agent`. Прямой A2A и бесконтрольный group chat запрещены.
- Между стадиями передавай минимальные versioned Pydantic/JSON-schema contracts, а не chat history.
- Ошибка `dbt test` — ошибка платформы или реализации; agent failure возникает, если агент неверно обработал проверенный результат. Не смешивай классы отказов.
- Не добавляй Kubernetes, memory, dynamic teams, A2A или новые skills без подтверждённого problem record и ADR.

## Runtime и зависимости

Agent control plane работает на Ubuntu локально: Python 3.12, `uv`, `.venv`, Microsoft Agent Framework, Pydantic и pytest. Текущая Data Platform в Docker Compose содержит ClickHouse, dbt, Airflow 3 + Astronomer Cosmos и PostgreSQL; observability относится к будущей Phase J. Не устанавливай project dependencies глобально. `uv.lock` обязателен; floating dependencies и Docker tag `latest` запрещены.

Make targets — стабильный пользовательский интерфейс. Детали `docker compose` и service networking остаются внутри Make/config. Добавляй healthchecks, детерминированный seed и идемпотентные операции. Не заявляй, что target работает, пока он не выполнен с exit code `0`.

Checkpointing использует MAF-native state/messages/graph signature через repository adapter:
только `.scenario-state/checkpoints/**`, root 0700, files 0600, UUID IDs, без symlink и без
application pickle types. Checkpoint — trusted local control-plane state, не model/tool input.
Committed superstep не повторяется после resume; side effects внутри оборванной стадии всё равно
обязаны иметь собственную idempotency.

Airflow baseline использует LocalExecutor, public `airflow.sdk` и pinned Astronomer Cosmos; будущие tools обращаются к `/api/v2`. dbt выполняется Cosmos в `ExecutionMode.LOCAL` через отдельный hash-locked virtualenv; собственный dbt subprocess runner запрещён без нового ADR. DAG-файлы являются исполняемым кодом: агентские изменения нельзя сразу монтировать в активную папку DAG. Scheduled `ecommerce_hourly` остаётся paused по умолчанию, а API acceptance выполняется на его manual twin.

## Contracts, evidence и validation

Утверждение агента не является evidence. Structured evidence должно содержать source, command/query/test/artifact, exit code, timestamp и output reference. Deterministic validator выполняет:

Domain contracts уже реализованы как frozen Pydantic v1 models с `extra="forbid"`, UTC-only
timestamps и discriminated artifact types. Любой внешний payload проходит `model_validate` или
`model_validate_json`; `model_construct` на trust boundary запрещён. Workflow state изменяется
только `orchestrator` reducer. MAF/provider adapters не определяют transitions и не редактируют
budgets. Event SHA-256 доказывает целостность последовательности, но не заменяет подпись или
durable authenticated storage.

```text
dbt parse → dbt compile → dbt build → dbt test
pytest → SQL correctness → repository policy tests
```

Ненулевой exit code означает failure; reasoning не может его переопределить. Hidden graders независимы от agent-created tests и недоступны рабочему агенту. Не ослабляй assertion, fixture, grader или policy ради зелёного результата.

Scenario lifecycle задаётся versioned manifest в `scenarios/<id>/manifest.json`. Всегда выполняй
`scenario-reset` перед новым run; не используй основной checkout как task workspace. Agent может
менять только manifest `editable_paths`. Baseline record хранится вне workspace, а stale source,
protected edit, unsafe path и grader failure имеют разные deterministic states. Не копируй
`grader/`, `.env`, `.git`, `plan/` или runtime source в agent snapshot.

Hidden oracle изменяется только human-authored change с обновлением SHA-256 manifest и regression
evidence. Он запускается отдельным non-root container с read-only submission и internal сетью до
fixture ClickHouse. Не запускай submission code внутри grader и не передавай ему `API_TOKEN`,
Docker socket или внешнюю сеть.

Тестируй сначала минимальный затронутый модуль, затем интеграционную границу. Тесты размещай в `tests/unit/`, `tests/integration/`, `tests/workflow/`, `tests/policy/` и `tests/adversarial/`. Любой исправленный системный дефект получает regression test.

## LLM gateway и стоимость

Все model calls идут только через OpenAI-совместимый GateLLM endpoint `https://gatellm.ru/v1`. Секрет читается из `API_TOKEN` в ignored `.env`; не переименовывай его, не выводи значение и не передавай в Docker-сервисы Data Platform. Не добавляй прямые provider keys или обход gateway без нового ADR и явного запроса.

Provider abstraction следует проверенному паттерну `research-agent`: lazy OpenAI-compatible client,
configurable `base_url`/model, единый internal response contract, bounded retries и token accounting.
Microsoft Agent Framework adapter реализован как тонкий слой поверх этой абстракции и не владеет
domain transitions.

По умолчанию выбирай самую дешёвую CHAT-модель, которая проходит live capability/eval gate. На
2026-09-06 catalog cheapest `inclusionai/ling-2.6-flash` возвращал 404; Mistral Nemo дважды дал 504
на полном structured request, Ling 3.0 не прошла schema probe, а IBM Granite Micro вернул
невалидный artifact. Текущий проверенный default для PM role —
`meta-llama/llama-3.1-8b-instruct`; выбор и стоимость записаны в EXP-0001. Это датированная
конфигурация, а не вечный hard-code. Перед benchmark обновляй catalog, capability и eval snapshot.
Более дорогую модель назначай роли только после измеренного провала дешёвой.

Unit/integration tests используют fake transport и не расходуют токены. Live smoke calls должны быть отдельными opt-in командами; для каждого сохраняй model id, max output, usage, latency и pricing snapshot. Ставь минимальный `max_tokens`, temperature `0` для deterministic structured tasks и жёсткие per-run budgets.

## Permissions и безопасность

Доступ к файлам, tools, credentials и сети закрыт по умолчанию и выдаётся role-specific allowlist. Prompt — не security boundary. Любой tool call проверяется middleware до выполнения.

- Data Engineer меняет только явно разрешённые platform paths и соответствующие tests в isolated task workspace.
- QA выполняет независимые проверки и формирует defects, но не исправляет product code.
- Reviewer работает read-only, не редактирует файлы и не approve собственную работу.
- Analyst использует read-only metadata/SQL и не пишет production code/data.
- Airflow Observer читает только allowlisted DAG/run/task/log metadata через repository-owned MCP и
  stable `/api/v2`; Viewer credentials и JWT не попадают в prompt, arguments, output или evidence.
- PM формирует specification/open questions и не реализует решение.
- Workflow управляет gates, retries и approvals; эти решения не делегируются LLM.

QA запускается только после `VALIDATED` под отдельным `qa_v1` profile. Текущий Net Revenue
protocol использует свежую фазу чтения кандидата и свежую фазу immutable code-owned SQL probe;
каждая вызывает ровно один tool. QA не генерирует исполняемый probe SQL и не видит hidden grader.
После QA FAIL только Data Engineer получает публичный accepted defect, а прежний validator PASS
аннулируется: обязательны полный validator rerun и новый QA-сеанс. Reviewer начинает только из
`QA_PASSED`, независимо читает model/test и один владеет переходом в `DONE`; его замечания ведут
через полный повтор DE → validator → QA → Reviewer. Opt-in команды — `make qa-live`,
`make reviewer-live` и `make quality-loop-live`; они расходуют GateLLM budget и не входят в
обычный `make check`.

Analyst запускается до PM через `analyst_v1`: три fresh phase получают только code-owned dbt
inventory, `fct_orders` lineage и aggregate ClickHouse profile, затем tool-free synthesis. В
`RequirementsAnalysisReport` разрешены только точные excerpts соответствующего retained evidence;
assumptions и open questions не являются facts. `make analyst-live` — opt-in платный gate. До
PM допускается только reducer-accepted typed `PMRequirementsHandoff`; raw `ContextBundle` PM не
получает. При незакрытых Analyst questions код запрещает `ready` и требует exact
`blocked / needs_user`. `make requirements-live` проверяет весь opt-in pipeline.

Airflow Observer использует только `airflow-observer-v1`: шесть fixed GET operations, три локальных
DAG ID, bounded pagination/log/output/call/time и отдельный FAB Viewer. Запрещены arbitrary URL,
trigger, pause, clear, retry, XCom, config, variables, connections и metadata DB. `make
airflow-mcp-smoke` — неплатный live gate; write-capability нельзя добавлять в этот profile/server.

Airflow trigger изолирован в отдельном profile/process/identity и разрешает только создание run
`ecommerce_acceptance`. Он требует code-owned одноразовый approval, связывающий task/DAG/key,
выводит run ID из idempotency key и не принимает `conf`, URL, method или credentials. Observer
остаётся read-only; pause/unpause доступны только административной live-test fixture.

Никогда не подключай production credentials и не выполняй production write/deploy. Исключение текущего local development — только `API_TOKEN` для явно разрешённого GateLLM gateway. Расширение file/network scope, secret access и необратимые действия требуют явного human approval. Не удаляй Docker volumes и не выполняй `docker system prune` без явного запроса.

## Работа с изменениями

Сохраняй чужие несвязанные изменения. Не изменяй `init/`, grader, expected result, policy или agent instructions вне scope активного шага. Новая функциональность должна быть минимальной для текущего gate; будущие слои оформляй backlog, а не speculative code.

Перед завершением сообщи и зафиксируй:

1. изменённые файлы и фактический результат;
2. выполненные команды, exit codes и evidence paths;
3. ADR/problem/experiment records;
4. непройденные проверки и остаточные риски;
5. следующий проверяемый шаг.
