# STEP-0001 — Repository bootstrap

Status: done  
Owner: primary agent  
Updated: 2026-09-04  
Current step: completed; следующий шаг — `STEP-0002-dbt-baseline.md`

## Goal

Создать воспроизводимую основу: `uv`-окружение для локального control plane и минимальную Docker Compose Data Platform с ClickHouse, deterministic seed и автоматической smoke-проверкой.

## Non-goals

- Не подключать LLM или Microsoft Agent Framework до готовности contracts/runtime шага.
- Не добавлять dbt и Airflow в этот же change set.
- Не реализовывать Net Revenue.
- Не добавлять Kubernetes, A2A, memory или production credentials.

## Affected layers and allowed paths

Разрешены root configuration, `plan/**`, `platform/clickhouse/**`, базовые package-каталоги и `tests/**`. Разрешено зафиксировать GateLLM configuration contract без реализации model call. Существующие `init/**` не изменяются.

## Acceptance criteria

- [x] `uv` доступен из `PATH` и сообщает зафиксированную версию.
- [x] `uv sync --frozen` создаёт `.venv` на Python 3.12.
- [x] `docker compose config` успешно валидирует конфигурацию.
- [x] `make platform-up` поднимает healthy ClickHouse.
- [x] `make seed` создаёт семь raw-таблиц с детерминированными edge cases.
- [x] `make platform-test` проверяет таблицы, объёмы и обязательные edge cases.
- [x] Документация и журнал отражают фактические результаты и ограничения.
- [x] GateLLM gateway, secret name и cost-first default зафиксированы без раскрытия токена.

## Risks, permissions, and approvals

- Docker image download требует сети и дискового пространства.
- Порты 8123/9000 могут конфликтовать; используются настраиваемые host ports.
- `platform-reset` с удалением volume не выполняется без явной необходимости; seed должен быть идемпотентным.
- Dev credentials не подходят для production и не должны использоваться вне локального Compose.

## Steps

1. [x] Проверить исходные документы и версии инструментов.
2. [x] Установить `uv` и зафиксировать проблему XDG install path.
3. [x] Создать governance documents и ADR.
4. [x] Создать `pyproject.toml`, `.python-version`, `.gitignore`, `.env.example`, `README.md` и package skeleton.
5. [x] Создать Compose/Make интерфейс и ClickHouse configuration.
6. [x] Реализовать deterministic seed и SQL smoke tests.
7. [x] Выполнить локальные и контейнерные проверки.
8. [x] Обновить work log, risks и status.

## Verification and evidence

| Command | Expected | Actual |
| --- | --- | --- |
| `uv --version` | `uv 0.12.9` | PASS |
| `uv sync --frozen` | exit 0 | PASS |
| `uv run pytest` | exit 0 | PASS: 5 tests |
| `docker compose config --quiet` | exit 0 | PASS |
| `make platform-up seed platform-test` | exit 0 | PASS: ClickHouse healthy, baseline PASS |

## Decisions and problems

- Decisions: ADR-0001…ADR-0007 in `plan/decisions/`.
- Problems: `plan/problems/PRB-0001-uv-install-path.md` and
  `plan/problems/PRB-0002-clickhouse-join-alias.md`,
  `plan/problems/PRB-0003-clickhouse-numeric-supertype.md`.

## Work log

- 2026-09-04: repository inventory and tool-version audit completed.
- 2026-09-04: official `uv 0.12.9` installer downloaded and inspected; second install used explicit `UV_INSTALL_DIR` after XDG path issue.
- 2026-09-04: roadmap and documentation protocol created before implementation.
- 2026-09-04: первый ClickHouse seed выявил обязательный alias для `numbers()` в JOIN; проблема зафиксирована и запрос исправлен.
- 2026-09-04: второй seed выявил signed/unsigned coercion в refund id; integer domain явно зафиксирован как `UInt64`.
- 2026-09-04: тот же numeric coercion найден в duplicate attribution id; PRB-0003 расширена до системного seed-паттерна и остаётся active до полного smoke test.
- 2026-09-04: каталог GateLLM моделей получен через `API_TOKEN`; live completion не выполнялся, текущий cheapest CHAT default и capability gate зафиксированы в ADR-0008.
- 2026-09-04: повторный полный gate прошёл; `.env` подтверждён как ignored без вывода `API_TOKEN`; STEP-0001 закрыт.

## Remaining risks

- ClickHouse dev-user пока имеет широкие права внутри локального сервиса; role-specific users появятся в policy/tool phase.
- SQL smoke output содержит технические нули от `throwIf`; позже evidence wrapper сохранит более структурированный report.
- dbt и Airflow ещё не входят в golden baseline.
