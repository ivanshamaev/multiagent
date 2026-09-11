# STEP-0009 — Autonomous Data Engineer milestone

Status: active
Owner: primary agent
Updated: 2026-09-11
Current step: принять execution-loop ADR и frozen human-authored Net Revenue specification

## Goal

Реализовать Phase F как первый end-to-end autonomous milestone: один Data Engineer agent получает
неизменяемую спецификацию Net Revenue и verified context, исследует данные через STEP-0008 tools,
редактирует только scenario dbt paths, запускает bounded validation/repair loop и возвращает typed
`ImplementationResult`. Качество оценивают независимый validator и неизменяемый hidden grader.

## Scope and non-goals

В scope входят DE instructions, MAF executor, единый budget ledger для workspace/MCP calls,
детерминированный validator, reducer transitions, repair loop, run evidence и repeated-run metrics.
Не входят QA/Reviewer agents, Analyst/PM discovery, Airflow write tools, production access,
checkpoint database и изменение grader/oracle ради улучшения результата.

## Acceptance criteria

- [ ] Human-authored specification фиксирует metric formula, grain, dimensions, edge cases and
  acceptance checks; LLM не может менять её identity или критерии.
- [ ] Agent получает только verified scenario context и точный profile tool subset; workspace и MCP
  вызовы используют один cumulative tool/wall/output budget.
- [ ] Изменения ограничены dbt models/tests, проходят atomic writes и не касаются main checkout,
  manifest, grader, runtime, policies или `.env`.
- [ ] Deterministic validator независимо выполняет parse, compile, build, 68+ tests, repository
  policy checks и SQL correctness; self-reported agent success не открывает transition.
- [ ] `validation fail → bounded DE rework` работает через существующий reducer; исчерпание лимита
  даёт явный terminal failure без бесконечного LLM/tool retry.
- [ ] Каждый run сохраняет config fingerprint, model/tool usage, latency, attempts, artifacts,
  validator facts и hidden-grade outcome без prompts, raw secrets или grader internals.
- [ ] Не менее 10 fresh runs измеряют task success, hidden pass rate, policy violations, retries,
  latency, tokens и ₽ cost; модель выбирается cost-first по измеренной capability.
- [ ] `make check`, platform/Cosmos, scenario reproducibility and unchanged baseline grader remain
  green; failing/malicious implementations покрыты regression tests.

## Risks and implementation sequence

Основные риски: nondeterministic edits, неполная семантика возвратов/валют, model-driven test
weakening, stale workspace, дорогие repair loops и смешение agent evidence с validator facts.

1. Принять ADR для agent/tool/validator ownership, budget accounting и repair transitions.
2. Зафиксировать spec fixture и DE instructions; добавить adversarial prompt/context tests.
3. Объединить workspace и MCP facade под один task-scoped ledger и evidence stream.
4. Реализовать DE executor и typed artifact assembly поверх reducer без prompt-owned IDs.
5. Реализовать независимый validator и negative fixtures; hidden grader оставить неизменным.
6. Выполнить один offline/fake vertical slice, затем минимальный live run и failure taxonomy.
7. Провести 10 fresh runs, сохранить aggregate evidence и только после gate закрыть milestone.

## Planned verification

Targeted unit/workflow/policy/adversarial tests; `make check`; `make mcp-smoke`;
`make scenario-repro-test`; unchanged baseline grader; successful hidden grade only for agent output;
`make platform-test`; secret/config scan; `git diff --check`.
