# STEP-0012 — Read-only Analyst requirements discovery

Status: complete
Owner: primary agent
Planned: 2026-09-13
Started: 2026-09-13
Completed: 2026-09-13
Evidence: `plan/evidence/STEP-0012-analyst-requirements-discovery.md`

## Goal

Начать Phase H и реализовать read-only Analyst Agent, который получает immutable business
`TaskRequest`, исследует проверенный data landscape через bounded dbt/ClickHouse tools и выпускает
evidence-backed discovery artifact для следующего PM specification gate. Pipeline должен отличать
подтверждённые факты от предположений, явно сохранять неизвестные вопросы и не позволять Analyst
писать код, менять данные или самостоятельно объявлять specification готовой.

Целевой порядок после миграции:

```text
TaskRequest → ANALYZING → RequirementsAnalysisReport → ANALYSIS_READY
            → PM SPECIFYING → SPEC_READY | BLOCKED (reason=needs_user)
            → Data Engineer → validator → QA → Reviewer
```

## Scope

- ADR для pre-PM порядка, ownership требований и разделения Analyst/PM.
- Версионированный analysis contract с source/model/lineage facts, profiling findings,
  semantic risks, assumptions, open questions и точными evidence references.
- `analyst_v1` instructions и deny-by-default capability profile.
- Несколько fresh bounded MAF phases: metadata discovery, lineage inspection, data profiling и
  synthesis без переноса произвольной tool history между model calls.
- Code-owned request preparation, evidence assembly, identities, budgets и reducer transitions.
- Typed handoff, который будущий PM сможет принять только вместе с исходным `TaskRequest` и
  принятым `RequirementsAnalysisReport` того же workflow/task.
- Offline fixtures/evals и один opt-in live discovery run через GateLLM.

## Non-goals

В этом шаге не реализуются PM reasoning/specification gate, DE-вызов после analysis, Airflow MCP,
production access, writes, DDL, arbitrary shell, hidden grader access, vector memory или dynamic
agent delegation. Analyst не определяет окончательную metric semantics, не выбирает бизнес-правила
при неоднозначности и не превращает assumptions в facts.

## Architectural decisions to record first

1. Заменить текущий исторический порядок `SPEC_READY → ANALYZING` на pre-PM discovery, сохранив
   валидность уже реализованного downstream quality loop через обновлённые factories/tests.
2. Решить, расширять ли `AnalysisReport` до schema v2 или добавить отдельный
   `RequirementsAnalysisReport`; миграция не должна молча менять смысл v1 artifact.
3. Определить deterministic readiness rule: analysis может быть принят при неполных бизнес-ответах,
   но material unknowns обязаны попасть в PM handoff и позднее привести к `BLOCKED` с типизированной
   причиной `needs_user`.
4. Зафиксировать, что LLM предлагает probes и интерпретацию, а policy/code владеют допустимыми
   tools, query grammar, row/byte/time limits, evidence IDs и переходами.

## Acceptance criteria

- [x] ADR документирует новый порядок `TaskRequest → Analyst → PM`, migration path и separation of
  duties: Analyst подтверждает data facts, PM владеет specification, workflow владеет readiness.
- [x] Analysis contract отличает fact/assumption/question/risk; каждый factual finding и lineage
  claim ссылается минимум на одно успешное same-task evidence, а IDs/authorship создаёт код.
- [x] `analyst_v1` разрешает только необходимые workspace reads, dbt metadata/lineage и bounded
  ClickHouse `SELECT`; write, DDL, dbt build/test, shell, grader, secrets, network expansion,
  production databases и wrong-role calls закрыты policy/adversarial tests.
- [x] Analyst запускается только из допустимого pre-spec state с исходным immutable `TaskRequest`;
  cross-task evidence, stale workspace, identity collision и повторное использование чужого
  report отклоняются.
- [x] Каждая phase использует fresh model context и точный tool allowlist; cumulative calls,
  rows/bytes, wall time и tokens не превышают profile/workflow budgets.
- [x] Metadata discovery находит только реально существующие sources/models; lineage не может
  ссылаться на неизвестные nodes, а profiling выводы подтверждаются retained result hashes.
- [x] Profiling SQL code-owned; shared AST/policy boundary для будущего generated SQL допускает
  только read-only query к `raw`/`analytics` с обязательным literal `LIMIT`, без comments,
  system tables, DDL/DML или unbounded output.
- [x] Synthesis не может выдать `ANALYSIS_READY`, если evidence отсутствует или output невалиден;
  transport/schema/tool failures сохраняют safe telemetry и не становятся data findings.
- [x] PM handoff содержит исходный request, accepted analysis artifact, unresolved material
  questions и configuration fingerprint, но не raw prompts, secret values или hidden evidence.
- [x] Offline evaluation покрывает clear request, ambiguous metric, missing source, semantic
  conflict, NULL/high-cardinality dimension, late-arriving data и prompt injection in metadata.
- [x] Live run сохраняет model/config/usage/cost/latency/tool metrics; модель выбирается только после
  schema+tool capability gate и canonical/mutation comparison, обычные tests не расходуют tokens.
- [x] `make check`, MCP smoke, scenario reproducibility, Airflow/Cosmos, dbt baseline и существующий
  Net Revenue hidden grader остаются green; результаты и residual risks записаны в evidence.

## Implementation sequence

1. Принять ADR и описать artifact/state migration, включая совместимость с STEP-0007/0009–0011.
2. Добавить/мигрировать contracts и reducer transitions; сначала unit/property tests для invalid
   evidence, wrong task/role, missing questions и недопустимого обхода PM.
3. Создать Analyst instructions/profile с минимальными путями, databases и tool budgets.
4. Реализовать trusted boundary: request builder, phase drafts, fact-to-evidence validation,
   code-owned report assembler и safe failure taxonomy.
5. Реализовать fresh metadata → lineage → profiling → synthesis workflow. Начать с code-owned
   probe templates; разрешать generated SELECT только там, где существующий parser доказывает
   read-only/limit/database constraints.
6. Добавить deterministic PM-handoff validator, не вызывая PM model в этом шаге.
7. Создать independently authored fixtures/mutations и offline vertical slices для READY,
   evidence-backed unknowns, denied write/DDL, injection и exhausted budget.
8. После offline gates выполнить bounded live capability comparison дешёвых reasoning models,
   один canonical run и минимум один ambiguity/mutation sample.
9. Выполнить полный regression, сохранить evidence/problem/experiment records и подготовить
   STEP-0013 для PM specification gate.

## Risks and mitigations

- **Порядок workflow:** миграция может сломать готовый DE/QA/Reviewer loop. Сначала меняются reducer
  tests/factories, затем adapters; прежние downstream gates должны пройти без упрощения.
- **Профилирование как утечка:** samples могут содержать чувствительные значения. Предпочитать
  aggregate counts/null rates/min-max; запрещать raw PII columns и ограничить retained rows/bytes.
- **LLM-authored evidence:** текст модели не считается фактом. Report принимает только проверенные
  refs на успешные tool outcomes с content hashes.
- **Business hallucination:** Analyst обязан формулировать material ambiguity как open question;
  только PM в следующем шаге решает READY/BLOCKED, не подменяя ответ пользователя.
- **Query fan-out/cost:** точные phase allowlists, sequential calls и жёсткий общий budget; catalog
  price не считается доказательством capability.
- **Prompt injection:** metadata/tool output всегда untrusted delimiter content; policy не зависит
  от instructions модели.

## Planned verification commands

```bash
uv run pytest -q tests/unit/test_analyst.py tests/workflow/test_analyst_workflow.py
uv run pytest -q tests/policy/test_analyst_profile.py tests/adversarial
make analyst-live ANALYST_CASE=canonical
make check
make mcp-smoke
make scenario-repro-test
make scenario-grade-baseline-test
make platform-test
make scenario-run scenario-contract-test scenario-grade SCENARIO=net-revenue
git diff --check
```

Live-команда является opt-in и запускается только после offline gates. Docker volumes не удаляются;
`platform-down` используется без `-v`.
