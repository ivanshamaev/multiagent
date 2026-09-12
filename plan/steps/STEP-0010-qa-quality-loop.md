# STEP-0010 — Read-only QA quality loop

Status: complete
Owner: primary agent
Started: 2026-09-12
Completed: 2026-09-12

## Goal

Реализовать первую часть Phase G: независимый read-only QA Agent проверяет уже прошедший public
validator candidate, выполняет разрешённые probes, формирует evidence-backed `QAReport` и только
через reducer открывает `QA_PASSED` либо ограниченный `QA FAIL → DE REWORK`. После исправления
кандидат обязан заново пройти полный validator и QA; self-report любого агента не является gate.

## Scope and non-goals

В scope входят QA instructions/profile, immutable QA input, отдельно измеримые bounded QA charges,
code-owned evidence assembly, интеграция с существующим DE repair path, mutation fixtures и
метрики false pass.
QA не получает write tools, shell, grader, secrets или production access. Reviewer/approval,
Airflow write tools, multi-scenario benchmark, durable checkpoints и course material остаются за
следующими шагами.

## Acceptance criteria

- [x] ADR фиксирует separation of duties: DE не выполняет QA, QA не пишет workspace, validator
  повторяется после каждого исправления, hidden grader не входит в feedback loop.
- [x] Профиль QA содержит только минимальные workspace/read-only ClickHouse/dbt capabilities;
  policy и adversarial tests закрыто отклоняют write, DDL, grader и protected paths.
- [x] QA получает frozen specification, candidate artifacts и public evidence с проверенными hashes;
  model draft не управляет artifact IDs, authorship, evidence или workflow transitions.
- [x] Независимые QA probes создают bounded evidence; `PASS` возможен только при всех успешных
  checks, а `FAIL` содержит воспроизводимый defect, acceptance criterion и evidence references.
- [x] Reducer выполняет `VALIDATED → QA → QA_PASSED` и
  `VALIDATED → QA → REWORK → DE → validator → QA` в пределах общего rework budget.
- [x] Набор намеренно ошибочных implementations измеряет false acceptance по всей цепочке:
  validator и QA обязаны обнаружить минимум ошибки refund date, attribution, split payments,
  duplicates и weakened test; отдельно учитывается, какой gate первым остановил mutation.
- [x] Regression tests доказывают independence, fail-closed invalid output, budget exhaustion,
  отсутствие записи и невозможность пропустить повторный validator.
- [x] `make check`, MCP/policy, scenario reproducibility, Airflow/Cosmos, dbt и baseline hidden
  grader остаются green; exact commands, exit codes, метрики и residual risks записаны в evidence.

## Implementation sequence

1. Принять ADR о QA trust boundary, ownership артефактов и порядке повторной валидации.
2. Добавить QA role instructions и deny-by-default read-only capability profile.
3. Реализовать минимальный QA draft contract, verified context builder и code-owned assembler
   `QAReport`; отдельно классифицировать model, tool, infrastructure и candidate failures.
4. Реализовать deterministic probe runner с точным allowlist и bounded retained output.
5. Расширить workflow: запуск QA только после `VALIDATED`, QA failure как reducer-owned rework,
   DE repair по QA evidence, затем обязательные validator и QA reruns.
6. Создать mutation corpus и offline vertical slices для pass, detected defect, repaired defect,
   invalid QA output, policy denial и exhausted budget.
7. Выполнить один минимальный live QA/repair run только после offline gates; затем полный platform
   regression и persistent evidence.

## Risks and verification

Главные риски: QA повторяет validator вместо независимой проверки, LLM выдумывает evidence,
hidden oracle просачивается в feedback, QA/DE делят credentials, repair обходит validator,
mutation corpus подгоняется под prompt. Узкие проверки запускаются после каждого слоя; системный
дефект получает problem record и regression. Никакие grader/validator assertions не ослабляются.

Planned commands: targeted `pytest`; `make check`; `make mcp-smoke`; mutation evaluation;
`make scenario-repro-test`; baseline hidden-grade check; `make platform-test`; secret scan;
`git diff --check`.

## Completion record

Implemented `qa_v1`, two fresh least-privilege QA phases, immutable code-owned semantic probe,
typed report assembly, reducer-owned branching, five independent mutations and an opt-in live
quality runner. GPT-5.6 Luna rejected all 5/5 validated mutations and passed canonical. The saved
live repair run used one DE write and reached `QA_PASSED` only after a second full validator.

Final gates: targeted QA suite `27 passed`; `make check` `280 passed`; MCP smoke, scenario
reproducibility, baseline grader, Airflow/Cosmos 11/11, dbt 68/68, canonical dbt 78/78, public SQL
and isolated hidden grader all exited 0. Details and run IDs are in
`plan/evidence/STEP-0010-qa-quality-loop.md` and `plan/experiments/EXP-0003-qa-mutations.md`.

Residual risk: evaluation covers one scenario and one model snapshot; LLM structured-output
variance remains fail-closed but can consume budget. Reviewer/approval is deliberately deferred.
