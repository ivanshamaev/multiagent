# ADR-0013 — Hidden grader как отдельный capability boundary

Status: accepted

Date: 2026-09-05

## Context

Hidden expected SQL в agent workspace или public validator позволяет недоверенному решению
подстроиться под oracle. Запуск agent-generated Python внутри grader, передача Docker socket или
общая внешняя сеть также позволили бы пересечь trust boundary.

## Decision

Hidden grader собирается отдельным pinned Docker image. Его build context содержит только
human-authored grader entrypoint. Контейнер работает non-root, с read-only root filesystem,
`cap_drop: ALL`, `no-new-privileges`, read-only mount submission и без Docker socket. Отдельная
internal Docker network даёт доступ только к fixture ClickHouse; `API_TOKEN` и Airflow credentials
не передаются.

Grader не исполняет submission code. Public `scenario-run` materializes dbt models отдельно;
`scenario-grade` затем выполняет независимые read-only SQL/schema checks. Oracle hash закреплён в
scenario manifest, но SQL и expected results не копируются в agent workspace. Exit codes являются
частью interface: `0` — pass, `10` — task incomplete/incorrect, `20+` — integrity/configuration
failure, `30` — grader infrastructure failure.

## Alternatives

- Hidden pytest рядом с public tests — отклонено: агент может прочитать ожидаемые значения.
- Запуск grader в agent container — отклонено: смешивает capabilities и допускает tampering.
- Проверять только agent-created tests — отклонено: agent statement не является evidence.

## Consequences and validation

Repository maintainers видят oracle source, но будущий agent получает только disposable snapshot.
Phase E дополнительно ограничит его filesystem tools; production-grade remote grader остаётся
будущим усилением. Policy tests проверяют build context, mounts, network и отсутствие secrets;
baseline обязан получить ожидаемый `INCOMPLETE`, не раскрывая SQL или числовой oracle.
