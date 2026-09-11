# STEP-0008 — MCP tools and deny-by-default policy layer

Status: completed
Owner: primary agent
Updated: 2026-09-11
Current step: завершён; evidence — `plan/evidence/STEP-0008-tool-policy-layer.md`

## Goal

Реализовать Phase E как отдельный controlled vertical slice: Data Engineer role получает только
bounded workspace files, read-only ClickHouse discovery/query и разрешённые dbt operations через
typed tool contracts. Каждый вызов сначала проходит pure deny-by-default policy, затем bounded
execution и формирует content-addressed evidence. Tool output остаётся недоверенным.

## Non-goals and affected paths

На шаге нет автономной реализации Net Revenue, Airflow tools, hidden grader access, production
credentials, arbitrary shell, internet access, multi-agent handoff или LLM-driven retry loop.
Разрешены `mcp/`, `policies/`, `runtime/`, профиль `agents/data_engineer/`, scenario-safe adapters,
tests, pinned dependencies/container definitions, Make/docs и `plan/**`. Golden dbt semantics,
grader oracle и protected main checkout не меняются.

## Acceptance criteria

- [x] По official source/docs принято ADR: версии и process boundary официальных ClickHouse/dbt
  MCP, stdio/HTTP transport, dependency isolation и связь с MAF tools.
- [x] Versioned capability profile перечисляет role, exact tool names, argument constraints,
  editable/readable paths, database/query limits и budgets; неизвестное поле/tool/role запрещено.
- [x] ClickHouse использует отдельные read-only credentials; write/DDL, multi-statement query,
  system-sensitive access и unbounded results отклоняются до исполнения.
- [x] dbt adapter работает только с verified scenario project и explicit operations
  `parse|compile|build|test|show|list|get_lineage_dev|get_node_details_dev`; arbitrary executable,
  selector/argument injection и env override невозможны.
- [x] Workspace adapter читает/пишет только manifest paths, запрещает symlink/traversal/protected
  files и выполняет atomic writes с pre/post hash.
- [x] Policy применяется вне prompt и до каждого MCP/function call; tool/wall-time/output budgets
  проверяются кодом, а denial не маскируется retry.
- [x] Каждый принятый вызов создаёт typed evidence: tool, normalized args hash, timestamps,
  exit/status, bounded output reference/hash и usage; secret/raw environment не сериализуются.
- [x] Offline tests покрывают allow cases и adversarial denial: ClickHouse write, grader/`.env`
  access, protected edit, shell metacharacters, unknown tool, output poisoning и exhausted budget.
- [x] E2E smoke выполняет read-only warehouse query и dbt compile/test в disposable workspace;
  `make check`, scenario reproducibility/grader и platform regressions остаются зелёными.

## Risks and decisions required

Official MCP packages and tool names may differ from the proposal in `init/`; current docs/source
must be checked before pinning. A read-only SQL account alone may not constrain result size or
expensive queries. dbt commands can write `target/` and reach ClickHouse, so container mounts,
working directory, selectors and environment need independent guards. MCP text can contain prompt
injection; evidence records facts, never instructions. Running official servers directly in the
agent venv may create dependency conflicts, so isolated `uv` environments or containers are the
default candidate until compatibility is proven.

## Implementation steps

1. Research official ClickHouse MCP, dbt MCP and MAF MCP interfaces; record versions and ADR.
2. Define strict tool request/result/evidence contracts and versioned capability profile schema.
3. Implement pure policy evaluation with normalized paths, SQL/argument classification and budgets.
4. Add isolated ClickHouse read-only and dbt scenario adapters; no arbitrary subprocess interface.
5. Add workspace read/write boundary with atomic changes and scenario verification.
6. Connect MAF middleware/tools only after adapter and adversarial tests pass.
7. Run E2E allowed/denied probes, full regressions, and persist exact evidence/residual risks.

## Planned verification

Targeted unit/policy/adversarial tests; resolved MCP/container configuration secret scan; read-only
ClickHouse identity/permission probes; dbt parse/compile/test in reset workspace; attempted DDL,
multi-statement SQL, traversal, protected edit, arbitrary command/env and output-poisoning tests;
`make check`; `make scenario-repro-test`; `make scenario-grade-baseline-test`;
`make platform-test`; `git diff --check`.

## Work log

- 2026-09-06: STEP-0007 closed before tool implementation. Scope separated from autonomous DE
  behavior so permissions and evidence can be validated independently of model quality.
- 2026-09-06: official source review зафиксировал mcp-clickhouse 0.6.0, dbt-mcp 2.2.1 и MAF
  MCPStdioTool/allowed_tools. ADR-0016 принимает isolated stdio processes, explicit dbt enable-list,
  dedicated ClickHouse read-only grants и repository policy как primary authorization gate.
- 2026-09-06: ADR-0017 фиксирует pinned SQLGlot ClickHouse AST preflight: single read query,
  qualified allowlisted databases и literal bounded LIMIT; parser остаётся defense in depth перед
  server-side read-only grants/timeout.
- 2026-09-11: после удаления пользовательских Docker containers/images повторно собраны pinned
  ClickHouse/dbt MCP images. Live advertised schemas выявили PRB-0018; contracts исправлены для
  list resource-type array, single lineage depth, separate dbt-show limit и mutual-exclusive
  selectors.
- 2026-09-11: реализованы content-addressed `ToolEvidenceStore`, serial cumulative-budget
  `MCPToolGateway` и локальный MAF facade. Модель видит только профильный subset локальных tools;
  каждый вызов повторно проходит pure policy, а denial превращается в `MiddlewareFailure` и не
  возвращается модели как обычная retryable tool error. Целевой gate: 61 passed.
- 2026-09-11: live вызов `dbt_parse` через connected MAF facade завершился success и сохранил
  bounded evidence. `make check` прошёл: Ruff, format, 208 tests и Compose config. Восстановление
  ClickHouse/Airflow containers отложено: PRB-0019 фиксирует повторяемый отказ host/VPN DNS до
  Docker registry; MCP images восстановлены, новый пустой named volume ClickHouse создан Compose.
- 2026-09-11: после восстановления DNS `make mcp-smoke` прошёл query/compile/test и локальный DDL
  denial; реальные grants дали SELECT=1/INSERT=0 для `mcp_reader`. Scenario fingerprint и hidden
  baseline grader воспроизведены; Airflow/Cosmos 11/11, dbt 68/68, full `make check` 210/210.
  PRB-0019 закрыт, PRB-0020 исправил обнаруженный false-green recipe. STEP-0008 завершён.
