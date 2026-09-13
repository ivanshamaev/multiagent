# STEP-0019 — Phase J: checkpointable role pipeline

Status: completed

## Goal

Разложить happy-path `Analyst → PM → Data Engineer → Validator → QA → Reviewer` на шесть
отдельных Microsoft Agent Framework executors. Каждый переход должен быть типизированной,
проверяемой границей и создавать MAF checkpoint, пригодный для продолжения в новом процессе.

## Scope

- ввести закрытый typed snapshot всего workflow и строгие проверки входной/выходной стадии;
- передавать snapshot между executors как канонический JSON без регистрации прикладных pickle-типов;
- адаптировать существующие role workflows через инъецируемые stage handlers;
- использовать `SecureCheckpointStorage` и стабильные executor/workflow IDs;
- доказать kill/restart после завершённой роли и отсутствие её повторного выполнения;
- добавить unit, workflow и adversarial regression coverage;
- обновить roadmap, решения и evidence.

Не входят в шаг: ветки `BLOCKED`/rework, повтор внешнего side effect внутри незавершённого
executor, OpenTelemetry, отдельные OS identities и платный GateLLM прогон. Они остаются
следующими срезами Phase J.

## Acceptance criteria

1. В compiled MAF graph ровно шесть role executors и пять последовательных edges.
2. Каждая граница принимает только JSON, валидирует полный Pydantic snapshot, event hash chain,
   ожидаемую входную стадию и обязательные артефакты.
3. Выходы стадий ограничены `ANALYSIS_READY`, `SPEC_READY`, `IMPLEMENTED`, `VALIDATED`,
   `QA_PASSED`, `DONE`; неверная identity/stage/chain отклоняется до следующей роли.
4. Checkpoint payload не требует allowlist прикладных Python-типов.
5. Реальный SIGKILL и новый процесс продолжают pipeline с последнего завершённого role boundary;
   счётчики доказывают, что завершённые роли не вызваны повторно.
6. `make check` и целевые workflow/adversarial тесты проходят; Docker после проверки остановлен.

## Risks and controls

- **Дубликат side effect внутри оборванной роли:** checkpoint фиксируется после executor; handlers
  обязаны быть idempotent, а этот residual risk явно сохраняется.
- **Несовместимый restart:** стабильные IDs плюс graph signature MAF дают fail-closed restore.
- **Подмена snapshot:** strict models, workflow/task consistency и `verify_event_chain` на каждом hop.
- **Секреты в checkpoint:** snapshot содержит доменные артефакты, но не provider credentials,
  prompts или MCP transports; hardened store остаётся owner-only.

## Implementation sequence

1. Зафиксировать ADR-0028 о typed JSON checkpoint boundaries.
2. Реализовать snapshot, stage protocol, шесть executors и graph builder.
3. Добавить детерминированный six-role fixture и process-level recovery smoke.
4. Покрыть topology, boundary rejection и resume regression тестами.
5. Выполнить проверки и записать точные evidence/remaining risks.

## Verification record

- `make role-pipeline-test` — exit 0, 4 passed. Graph дошёл до `DONE`, revision 12; checkpoint
  iterations 0…6 соответствуют entry и шести завершённым ролям.
- Process test остановил worker через `SIGKILL` при входе Validator после durable iteration 3,
  затем новый процесс восстановил pending Validator message. Все шесть role counters равны 1.
- `make check` — exit 0, 386 tests passed; Ruff, format, plan governance и Compose config PASS.
- `docker compose ps --format json` — exit 0, пустой вывод: контейнеры не запускались и остаются
  погашенными. GateLLM и Data Platform не требовались для deterministic recovery проверки.

Реализованы stable graph `agentic-data-role-pipeline-v1`, шесть отдельных executor IDs, immutable
snapshot и canonical JSON codec. Checkpoint files не содержат прикладных Python type markers.
Boundary запрещает смену request/workflow/task, переписывание event prefix и принятых артефактов,
неполную/опережающую artifact sequence и более одной пары reducer transitions за роль.

Remaining risk: checkpoint фиксируется после возврата executor, поэтому внешний side effect внутри
оборванной роли требует собственной idempotency. Happy-path branching/rework, OTel и process/credential
isolation остаются следующими Phase J slices.
