# STEP-0002 — dbt baseline

Status: active  
Owner: primary agent  
Updated: 2026-09-04  
Current step: подтвердить Core 1.11.14 / adapter 1.10.2 full compatibility

## Goal

Добавить контейнерный dbt runner и проверенный baseline `staging → intermediate → marts` поверх deterministic ClickHouse seed. Net Revenue намеренно не реализуется: это будущая benchmark-задача агента.

## Non-goals

- Не добавлять Airflow, MCP или LLM calls.
- Не реализовывать scenario harness/hidden grader.
- Не вычислять Net Revenue и не создавать готовый ответ для будущего DE Agent.
- Не устанавливать dbt на host.

## Affected layers and allowed paths

Разрешены `docker-compose.yml`, `Makefile`, `.env.example`, `platform/dbt/**`, `tests/policy/**`, `plan/**`, `README.md` и актуализация contributor guides. `init/**`, agent/runtime contracts и GateLLM token не изменяются.

## Acceptance criteria

- [ ] dbt image и Python dependencies зафиксированы; `dbt --version` воспроизводим.
- [ ] `dbt debug`, `dbt parse` и `dbt compile` проходят из контейнера.
- [ ] Созданы sources и staging models для orders, payments, refunds и customers.
- [ ] Созданы intermediate payment/refund aggregates без Net Revenue.
- [ ] Созданы `fct_orders` и `dim_customers` с явно описанной grain.
- [ ] Schema/generic/custom business tests ловят ключевые baseline invariants.
- [ ] `make dbt-build` и общий `make platform-test` завершаются с exit code `0`.
- [ ] Повторный build идемпотентен.

## Risks, permissions, and approvals

- dbt-core и dbt-clickhouse должны быть совместимы с Python 3.12 и ClickHouse 25.8.
- ClickHouse database/schema semantics отличаются от PostgreSQL; profile и source quoting проверяются реальным запуском.
- Relationships tests на больших таблицах могут замедлить baseline; измеряем до оптимизации.
- Container получает только repository dbt project и необходимые connection variables, но не `API_TOKEN`.

## Steps

1. [ ] Выбрать и зафиксировать совместимые версии по primary sources.
2. [ ] Создать Dockerfile/lock requirements для dbt runner.
3. [ ] Добавить Compose service без постоянного background process.
4. [ ] Создать dbt project, profile, sources и layered models.
5. [ ] Добавить generic и custom tests.
6. [ ] Расширить Make targets и policy tests.
7. [ ] Выполнить `debug → parse → compile → build → test` дважды.
8. [ ] Зафиксировать evidence, problems и remaining risks.

## Verification and evidence

| Command | Expected | Actual |
| --- | --- | --- |
| `docker compose build dbt` | exit 0 | pending |
| `make dbt-debug` | exit 0 | pending |
| `make dbt-parse` | exit 0 | pending |
| `make dbt-build` | exit 0 | pending |
| `make platform-test` | exit 0 | pending |

## Decisions and problems

- Runtime boundary: ADR-0001.
- Data Platform stack: ADR-0004.
- Новые проблемы добавляются в `plan/problems/` до workaround.

## Work log

- 2026-09-04: шаг создан после полного green gate STEP-0001; реализация ещё не начата.
- 2026-09-04: зафиксированы Python image digest, `dbt-core==1.10.23`, `dbt-clickhouse==1.10.2` и hash-locked transitive dependencies; image build и `dbt --version` прошли.
- 2026-09-04: первый `dbt debug` подтвердил connection, но завершился с exit code `1` из-за отсутствия git; причина и fix зафиксированы в PRB-0004.
- 2026-09-04: общий wrapper ошибочно применил subcommand-only paths к `dbt --version`; container-native workdir fix зафиксирован в PRB-0005.
- 2026-09-04: `debug`, `parse` и `compile` прошли; устаревшее расположение dbt flags устранено и зафиксировано в PRB-0006 перед build gate.
- 2026-09-04: первый и повторный Core 1.10 build прошли (`PASS=76`), platform tests прошли (`PASS=68` + SQL smoke); deprecated Core warning инициировал upgrade experiment PRB-0007.
