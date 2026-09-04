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
- В MVP взаимодействие агентов: `agent → typed artifact → workflow → next agent`. Прямой A2A и бесконтрольный group chat запрещены.
- Между стадиями передавай минимальные versioned Pydantic/JSON-schema contracts, а не chat history.
- Ошибка `dbt test` — ошибка платформы или реализации; agent failure возникает, если агент неверно обработал проверенный результат. Не смешивай классы отказов.
- Не добавляй Kubernetes, memory, dynamic teams, A2A или новые skills без подтверждённого problem record и ADR.

## Runtime и зависимости

Agent control plane работает на Ubuntu локально: Python 3.12, `uv`, `.venv`, Microsoft Agent Framework, Pydantic и pytest. Data Platform работает в Docker Compose: ClickHouse, dbt runner, Airflow 3, PostgreSQL и observability. Не устанавливай project dependencies глобально. `uv.lock` обязателен; floating dependencies и Docker tag `latest` запрещены.

Make targets — стабильный пользовательский интерфейс. Детали `docker compose` и service networking остаются внутри Make/config. Добавляй healthchecks, детерминированный seed и идемпотентные операции. Не заявляй, что target работает, пока он не выполнен с exit code `0`.

## Contracts, evidence и validation

Утверждение агента не является evidence. Structured evidence должно содержать source, command/query/test/artifact, exit code, timestamp и output reference. Целевой deterministic validator выполняет:

```text
dbt parse → dbt compile → dbt build → dbt test
pytest → SQL correctness → repository policy tests
```

Ненулевой exit code означает failure; reasoning не может его переопределить. Hidden graders независимы от agent-created tests и недоступны рабочему агенту. Не ослабляй assertion, fixture, grader или policy ради зелёного результата.

Тестируй сначала минимальный затронутый модуль, затем интеграционную границу. Тесты размещай в `tests/unit/`, `tests/integration/`, `tests/workflow/`, `tests/policy/` и `tests/adversarial/`. Любой исправленный системный дефект получает regression test.

## LLM gateway и стоимость

Все model calls идут только через OpenAI-совместимый GateLLM endpoint `https://gatellm.ru/v1`. Секрет читается из `API_TOKEN` в ignored `.env`; не переименовывай его, не выводи значение и не передавай в Docker-сервисы Data Platform. Не добавляй прямые provider keys или обход gateway без нового ADR и явного запроса.

Provider abstraction следует проверенному паттерну `research-agent`: lazy OpenAI-compatible client, configurable `base_url`/model, единый internal response contract, bounded retries и token accounting. Конкретный Microsoft Agent Framework adapter добавляется в Phase D поверх этой абстракции.

По умолчанию выбирай самую дешёвую доступную CHAT-модель, которая проходит capability/eval gate. На 2026-09-04 snapshot `/v1/models` даёт `inclusionai/ling-2.6-flash` как самый дешёвый вариант; это конфигурация, а не вечный hard-coded выбор. Перед benchmark обновляй pricing snapshot. Дорогую модель разрешено назначить конкретной роли только после измеренного провала дешёвой и ADR/experiment с quality-cost сравнением.

Unit/integration tests используют fake transport и не расходуют токены. Live smoke calls должны быть отдельными opt-in командами; для каждого сохраняй model id, max output, usage, latency и pricing snapshot. Ставь минимальный `max_tokens`, temperature `0` для deterministic structured tasks и жёсткие per-run budgets.

## Permissions и безопасность

Доступ к файлам, tools, credentials и сети закрыт по умолчанию и выдаётся role-specific allowlist. Prompt — не security boundary. Любой tool call проверяется middleware до выполнения.

- Data Engineer меняет только явно разрешённые platform paths и соответствующие tests в isolated task workspace.
- QA выполняет независимые проверки и формирует defects, но не исправляет product code.
- Reviewer работает read-only, не редактирует файлы и не approve собственную работу.
- Analyst использует read-only metadata/SQL и не пишет production code/data.
- PM формирует specification/open questions и не реализует решение.
- Workflow управляет gates, retries и approvals; эти решения не делегируются LLM.

Никогда не подключай production credentials и не выполняй production write/deploy. Исключение текущего local development — только `API_TOKEN` для явно разрешённого GateLLM gateway. Расширение file/network scope, secret access и необратимые действия требуют явного human approval. Не удаляй Docker volumes и не выполняй `docker system prune` без явного запроса.

## Работа с изменениями

Сохраняй чужие несвязанные изменения. Не изменяй `init/`, grader, expected result, policy или agent instructions вне scope активного шага. Новая функциональность должна быть минимальной для текущего gate; будущие слои оформляй backlog, а не speculative code.

Перед завершением сообщи и зафиксируй:

1. изменённые файлы и фактический результат;
2. выполненные команды, exit codes и evidence paths;
3. ADR/problem/experiment records;
4. непройденные проверки и остаточные риски;
5. следующий проверяемый шаг.
