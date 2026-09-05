# ADR-0010 — Изолированное выполнение dbt в Airflow

Status: accepted

Date: 2026-09-05

Supersedes: ADR-0009 only for its deferred dbt execution boundary; topology/auth/API rules remain.

## Context

STEP-0003 доказал Airflow scheduling/API с marker tasks. Для завершения Golden Data Platform DAG должен исполнять реальные transformations/tests. Airflow image и dbt lock закрепляют разные версии общих зависимостей, поэтому установка в один environment нарушает воспроизводимость.

## Decision

Расширяем pinned официальный Airflow image отдельным `/opt/airflow/dbt-venv` без system-site-packages; зависимости ставятся на build из существующего `platform/dbt/requirements.lock` с обязательными hashes. Airflow Python graph не изменяется. Build context allowlists только Dockerfile и lock. Фактический runtime вызывается через фиксированный argv subprocess, без shell, Docker socket, model calls или пользовательского `dag_run.conf` как команды.

dbt project/profile монтируются read-only. Output изолируется по run/stage/attempt в named volume; stdout, command metadata и dbt invocation IDs сохраняются как evidence, компактный результат — в XCom. Перед каждым слоем проверяется результат dbt, timeout или nonzero returncode приводят к task failure. `load_raw` проверяет source tests; destructive seed остаётся явной host Make-командой.

`publish` завершает публикацию in-place marts только после успешных tests. Отдельный manual-only failure probe разделяет ту же factory и порядок tasks, но выполняет заранее написанный failing dbt fixture на стадии tests. Public API проверяет, что publish не исполнился. По умолчанию DAGs paused; acceptance unpause/restore ограничен двумя локальными DAG IDs.

## Alternatives

Отдельный HTTP runner service даёт дополнительную process boundary, но требует API/auth/queue/result protocol до появления agent tools. Для текущего single-host trusted baseline изолированного subprocess достаточно. Dependency isolation не считается sandbox для недоверенного agent code; усиление разрешений остаётся Phase E/J.

## Consequences and validation

Airflow image становится project-specific, но переиспользует уже скачанные base layers. Проверяем версии и `pip check` в обоих environments, read-only project, минимум два успешных API runs с SQL correctness, failure-before-publish и отсутствие gateway token в build/runtime. Named output volume требует будущей retention policy. [Официальное расширение Airflow image](https://airflow.apache.org/docs/docker-stack/build.html) описывает build-time dependency installation и отдельные environments для конфликтующих packages.
