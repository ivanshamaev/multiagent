# STEP-0009 — Autonomous Data Engineer milestone

Status: active
Owner: primary agent
Updated: 2026-09-12
Current step: разделить live execution на bounded fresh-conversation phases

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

- [x] Human-authored specification фиксирует metric formula, grain, dimensions, edge cases and
  acceptance checks; LLM не может менять её identity или критерии.
- [x] Agent получает только verified scenario context и точный profile tool subset; workspace и MCP
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

## Work log — 2026-09-11

- Принят ADR-0018: frozen human specification, code-owned identity/evidence/transitions, единый
  task ledger и независимый validator. `specification.json` привязан к версии сценария и SHA-256
  `TASK.md`; workspace verification отклоняет tampering.
- Добавлены Data Engineer instructions и request boundary. Spec проходит обычные reducer gates до
  `ANALYZING`; prompt явно разделяет immutable specification и untrusted workspace context, а draft
  не содержит ID, timestamps, evidence или changed-files claims.
- Workspace и official MCP объединены одним serialized gateway. Интеграционный тест подтверждает:
  read + dbt consume общий лимит, следующий ClickHouse call получает pre-execution denial.
- MAF tool loop ограничен 12 roundtrips и 80 calls; profile gateway остаётся жёсткой границей для
  каждого вызова. Control plane собирает `AnalysisReport`/`ImplementationResult` только из
  успешных measured evidence и переводит ложный `completed` без dbt changes в `FAILED`.
- Целевые проверки: `56 passed`, затем `28 passed`, `26 passed`, `25 passed`, все exit `0`.
  Финальный `make check` — exit `0`: Ruff/format, `227 passed`, Compose config valid.

Следующий незакрытый блок: validator с точным command allowlist, отдельным evidence producer,
negative implementation fixtures и переходами `VALIDATING → VALIDATED|REWORK|FAILED`.

## Work log — 2026-09-11, validator increment

- Добавлен независимый public SQL contract вне agent workspace: physical table, семь обязательных
  columns, non-Nullable schema, unique grain, metric identity и signed `net_revenue_cents`. Exact
  expected rows остаются только в unchanged hidden grader.
- Validator выполняет четыре code-owned gates без shell: workspace integrity, full scenario dbt
  build/test, independent SQL и repository policy/adversarial tests. Команду нельзя подменить;
  subprocess получает минимальное окружение без `API_TOKEN`, `LLM_*`, `PYTHONPATH` и `MAKEFLAGS`.
- Output ограничен 2 MB и сохраняется content-addressed. Candidate failure даёт `FAIL → REWORK`,
  повторный fail при исчерпанном лимите — terminal `FAILED`; timeout/process/output failure даёт
  `ERROR → FAILED` без расходования rework attempt.
- `make scenario-contract-test` на baseline ожидаемо отклонён до agent run: outer exit `2`, причина
  — отсутствие physical `analytics.fct_net_revenue`. SQLGlot разобрал все 7 statements.
- Реальный integrity gate — exit `0`, evidence SHA-256 `899c4684…`. Целевые validator/policy tests:
  `46 passed`; полный `make check && git diff --check` — exit `0`, `234 passed`, Compose valid.

Критерий validator остаётся открытым до positive candidate run. Следующий блок — единый MAF
executor, затем один минимальный live run выбранной cost-first моделью.

## Work log — 2026-09-12, offline end-to-end

- MAF workflow связал frozen request, tool-enabled provider, unified gateway, workspace diff,
  code-owned artifact assembly и independent validator. Validator запускается только после
  reducer-accepted `IMPLEMENTED`; failed/blocked draft не может самостоятельно открыть validation.
- Offline fake model через реальные MAF function tools прочитал `TASK.md` и атомарно записал model
  только в disposable workspace. Два tool calls попали в общий ledger/evidence; main checkout и
  official MCP процессы не затрагивались. Fake validator выполнил полный four-gate plan, итоговая
  hash-chain достигла `VALIDATED`, после чего workspace был сброшен к baseline.
- Первая попытка выявила PRB-0021: handler `execute` перекрыл framework dispatch method. Rename в
  `run_attempt` и end-to-end regression test закрыли дефект; targeted suite — `35 passed`.

Следующий gate: полный `make check`, затем opt-in live run с минимальным cost-first model budget.

## Work log — 2026-09-12, live capability and failure taxonomy

- Live runner получает актуальный GateLLM catalog, проверяет strict schema и forced tool calling,
  запускает official ClickHouse/dbt MCP и сохраняет приватную redacted terminal run record.
- Cost-first проверка разделила способности: Granite Micro принимает schema mode, но возвращает 404
  для tools; Llama 3.1 8B прошла оба micro-gate. Prose-only результат Llama корректно отклонён с
  measured usage `3821` tokens и стоимостью `0.058836` ₽ вместо ложного success.
- Function errors получили bounded recovery (не более трёх подряд); provider/framework failure после
  старта теперь всегда сохраняет tool metadata, а неизвестные usage/cost явно остаются `null`.
- Реальные policy denials подтвердили allowlist `raw`/`analytics`. Следующий run выполнил успешные
  `dbt.parse` и `dbt.compile`, после чего provider вернул HTTP 400.
- Минимальный прямой `ping` воспроизвёл тот же предел независимо от MCP: два tool rounds успешны,
  третий получает HTTP 400. Поиск следующей модели остановлен на HTTP 429 без обхода rate limit.
- PRB-0022—0026 и EXP-0002 фиксируют результаты. Следующий implementation block — отдельные свежие
  investigation/implementation conversations с единым code-owned budget/evidence, затем validator.
- После инкремента `make check && git diff --check` завершились с exit `0`: Ruff/format, `243
  passed` и Compose config valid.

## Work log — 2026-09-12, phased conversation increment

- Принят ADR-0019. Investigation, mart SQL и contract-test выполняются в трёх свежих диалогах с
  одним общим gateway ledger. Каждая фаза получает ровно необходимый tool subset и обязана добавить
  ровно один evidence record; usage/latency/hashes завершённых model calls агрегируются кодом.
- Data Engineer context расширен существующими intermediate/mart/source SQL и models YAML, поэтому
  implementation phases не требуют дополнительного history round. Offline vertical slice достиг
  `VALIDATED`: 3 model calls, 3 tool calls, 2 изолированных changed files, 45 measured tokens.
- Live run выявил parallel batch из 80 повторных calls (PRB-0027); `parallel_tool_calls=false` и
  live limit 6 закрыли fan-out. Следующая попытка выполнила ровно один разрешённый read, но сочетание
  tool history + provider schema mode дало 400 (PRB-0028); schema mode удалён только из tool phases,
  closed local Pydantic validation сохранена.
- После этого exact-one-read повтор дошёл до final boundary и остановился на HTTP 429. Новые платные
  попытки остановлены до восстановления rate limit. Следующий gate — завершить phased live candidate,
  затем independent validator/hidden grade и bounded rework.
- Полный `make check && git diff --check` после phased increment — exit `0`: Ruff/format, `246
  passed`, Compose config valid.

## Work log — 2026-09-12, bounded rework and provider telemetry

- Реализован полный `FAIL → REWORK → IMPLEMENTING → IMPLEMENTED → VALIDATING` loop. Repair получает
  только content-addressed output публичного failing gate и текущие candidate SQL/test как явно
  untrusted context, выполняет ровно один write и повторно проходит весь validator.
- Offline regressions доказывают оба исхода: один repair достигает `VALIDATED`; три validation fail
  расходуют ровно два разрешённых attempts и детерминированно завершаются `FAILED` без шестого model
  call. Tool/model/wall usage каждого repair списываются reducer-ом отдельно.
- Фазовые contracts разделены на минимальные investigation и implementation drafts. Invalid output
  теперь сохраняет error codes, measured usage/cost/latency/hashes без raw response. Единственный
  schema-valid JSON внутри model decoration принимается, ambiguous response отклоняется (PRB-0029).
- Catalog-bound mode-0600 capability cache с TTL 1 час устранил два повторных probe calls на run;
  любое изменение catalog/model/pricing или stale/malformed cache закрыто инвалидирует его
  (PRB-0030). Первый run cache создал, но finalization всё ещё получил внешний HTTP 429.

## Planned verification

Targeted unit/workflow/policy/adversarial tests; `make check`; `make mcp-smoke`;
`make scenario-repro-test`; unchanged baseline grader; successful hidden grade only for agent output;
`make platform-test`; secret/config scan; `git diff --check`.
