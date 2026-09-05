# STEP-0002 — dbt baseline

Status: done
Owner: primary agent  
Updated: 2026-09-05
Current step: завершён; fresh full-gate transcript сохранён

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

- [x] Python base image закреплён digest, а dbt/Python dependencies — точными версиями и hashes; `dbt --version` воспроизводим.
- [x] `dbt debug`, `dbt parse` и `dbt compile` проходят из контейнера.
- [x] Созданы sources и staging models для orders, payments, refunds и customers.
- [x] Созданы intermediate payment/refund aggregates без Net Revenue.
- [x] Созданы `fct_orders` и `dim_customers` с явно описанной grain.
- [x] Schema/generic/custom business tests ловят ключевые baseline invariants.
- [x] `make dbt-build` и общий `make platform-test` завершаются с exit code `0`.
- [x] Повторный build идемпотентен.
- [x] Fresh full-gate transcript содержит source revision, timestamps, exit codes и persistent output reference.

## Risks, permissions, and approvals

- dbt-core и dbt-clickhouse должны быть совместимы с Python 3.12 и ClickHouse 25.8.
- ClickHouse database/schema semantics отличаются от PostgreSQL; profile и source quoting проверяются реальным запуском.
- Relationships tests на больших таблицах могут замедлить baseline; измеряем до оптимизации.
- Container получает только repository dbt project и необходимые connection variables, но не `API_TOKEN`.
- Debian package `git` не закреплён snapshot/version, поэтому весь dbt image пока не является bit-reproducible.

## Steps

1. [x] Выбрать и зафиксировать совместимые версии по primary sources.
2. [x] Создать Dockerfile/lock requirements для dbt runner.
3. [x] Добавить Compose service без постоянного background process.
4. [x] Создать dbt project, profile, sources и layered models.
5. [x] Добавить generic и custom tests.
6. [x] Расширить Make targets и policy tests.
7. [x] Выполнить `debug → parse → compile → build → test`, затем повторить `build → test` без reset и после полного reseed.
8. [x] Сохранить fresh ADR-0005-compliant transcript и remaining risks.

## Verification and evidence

| Command | Expected | Historical aggregate |
| --- | --- | --- |
| `docker compose build dbt` | exit 0 | reported exit 0; local image `sha256:299b4b00…` |
| `make dbt-version` | exit 0 | reported Core 1.11.14, clickhouse 1.10.2 |
| `make dbt-debug` | exit 0 | reported exit 0; all checks passed |
| `make dbt-parse && make dbt-compile` | exit 0 | reported exit 0; 8 models, 68 tests, 7 sources |
| `make dbt-build` | exit 0 | reported exit 0; PASS=76, WARN=0, ERROR=0 |
| `make platform-test` | exit 0 | reported exit 0; PASS=68 + two SQL smoke suites |
| повторный build и полный reseed/build | exit 0 | reported exit 0 for both paths |
| `make check` | exit 0 | reported exit 0; Ruff, 8 pytest, Compose config |
| dbt container token isolation check | exit 0 | reported `API_TOKEN` absent |

Свежая проверка 2026-09-05 03:50:10–03:52:33 UTC повторила version/debug/parse/compile, build/test без reset и после reseed; все команды завершились с exit code `0`. Она заменяет historical aggregate как основание закрытия. [Summary](../evidence/STEP-0002-dbt-baseline.md) и [полный transcript](../evidence/STEP-0002-fresh-transcript.md) содержат scoped source fingerprint, timestamps и сохранённый output. Общий gate с Airflow и token isolation — в STEP-0003 evidence.

## Decisions and problems

- Runtime boundary: ADR-0001.
- Data Platform stack: ADR-0004.
- Исправленные проблемы: PRB-0004 (git), PRB-0005 (CLI scope), PRB-0006 (flags deprecation), PRB-0007 (Core support window), PRB-0008 (local user id artifact).
- Remaining risks: dev ClickHouse user пока имеет широкие локальные права; unpinned Debian `git` не даёт bit-reproducible image; adapter release не заявляет full Core 1.11 feature support; Core 1.12 вне текущего scope.

## Work log

- 2026-09-04: шаг создан после полного green gate STEP-0001; реализация ещё не начата.
- 2026-09-04: зафиксированы Python image digest, `dbt-core==1.10.23`, `dbt-clickhouse==1.10.2` и hash-locked transitive dependencies; image build и `dbt --version` прошли.
- 2026-09-04: первый `dbt debug` подтвердил connection, но завершился с exit code `1` из-за отсутствия git; причина и fix зафиксированы в PRB-0004.
- 2026-09-04: общий wrapper ошибочно применил subcommand-only paths к `dbt --version`; container-native workdir fix зафиксирован в PRB-0005.
- 2026-09-04: `debug`, `parse` и `compile` прошли; устаревшее расположение dbt flags устранено и зафиксировано в PRB-0006 перед build gate.
- 2026-09-04: первый и повторный Core 1.10 build прошли (`PASS=76`), platform tests прошли (`PASS=68` + SQL smoke); deprecated Core warning инициировал upgrade experiment PRB-0007.
- 2026-09-04: Core обновлён до 1.11.14; historical local artifacts сообщают об успешных full gate, повторном build без reset и `seed → build → platform-test`.
- 2026-09-05: post-gate audit удалил tracked dbt `.user.yml` и добавил ignore/policy regression (PRB-0008).
- 2026-09-05: evidence audit выявил отсутствие source revision, точных timestamps и persistent output transcript; шаг возвращён в validating до fresh capture.
- 2026-09-05: свежий gate сохранён в persistent transcript; Core 1.11.14/adapter 1.10.2, build PASS=76 и tests PASS=68 повторились до/после reseed. Шаг снова закрыт на основании этих данных.
