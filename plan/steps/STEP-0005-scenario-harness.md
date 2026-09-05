# STEP-0005 — Воспроизводимый scenario harness

Status: completed
Owner: primary agent
Updated: 2026-09-05
Current step: gate закрыт; следующий active step — STEP-0006

## Goal

Создать воспроизводимый локальный harness для будущей benchmark-задачи Net Revenue. Два reset должны давать одинаковые данные, git/workspace state и baseline results; рабочий агент не должен видеть hidden expected results.

## Non-goals and affected paths

На этом шаге не подключаем LLM, Microsoft Agent Framework, MCP и не добавляем Net Revenue в golden
dbt project. Human-authored hidden oracle определяет ожидаемое поведение, но не копируется в agent
workspace. Разрешены новые `scenarios/`, `grader/`, `contracts/`, `runtime/`, tests, Make/config и
`plan/**`. Golden seed/dbt expected values не меняются.

## Acceptance criteria

- [x] Versioned scenario manifest фиксирует ID, исходный commit, разрешённые пути, budgets, setup, public gates и hidden grade interface.
- [x] Reset создаёт отдельный disposable workspace и не меняет основной checkout.
- [x] Два reset дают одинаковые checksums файлов и ClickHouse baseline.
- [x] Public task materials не раскрывают hidden SQL/expected results.
- [x] `scenario-run` и `scenario-grade` имеют разные capability boundaries и deterministic exit codes.
- [x] Unit, policy, integration и adversarial tests проверяют traversal, protected paths, stale state и grader isolation.
- [x] Make targets и fresh evidence документируют полный lifecycle без LLM calls.

## Risks and decisions required

Git worktree и Docker volumes могут сохранять state между прогонами; destructive reset допускается только внутри явно созданного scenario workspace и fixture databases. Hidden grader в одном checkout недостаточно изолирован от недоверенного кода. До реализации нужны ADR о workspace lifecycle и grader process/filesystem boundary.

## Implementation steps

1. [x] Инвентаризировать current Make/dbt/ClickHouse boundaries и определить strict JSON manifest.
2. [x] Принять ADR для disposable snapshot lifecycle и hidden grader isolation.
3. [x] Реализовать `scenario-init/reset/status` с target validation и logical checksums.
4. [x] Добавить public validator; hidden grader хранить вне agent-mounted workspace.
5. [x] Проверить два чистых reset, contamination recovery и deny tests.
6. [x] Сохранить evidence, закрыть проблему и открыть contracts/workflow step.

## Planned verification

Минимум: `make check`, schema/unit tests, два последовательных reset с одинаковым fingerprint, public baseline build, independent hidden grade, protected-path adversarial tests и `git diff --check`.

## Decisions, problems, and actual verification

- ADR-0012: allowlisted content snapshot вместо небезопасной копии checkout.
- ADR-0013: hidden grader в отдельном non-root/read-only container и internal network.
- PRB-0012: mode `0700` от `mkdtemp` блокировал grader; managed root теперь `0755` с regression test.
- `make scenario-repro-test SCENARIO=net-revenue` — exit `0`; оба полных reset дали
  `baseline=53bf4b7d…`, `source=798def11…`, `data=3823d7b5…`.
- `make scenario-grade-baseline-test SCENARIO=net-revenue` — exit `0`; raw grader exit `10`
  и state `INCOMPLETE`, как требуется для golden baseline.
- Временная неправильная relation прошла schema/invariant stages и была отвергнута business oracle;
  следующий reset удалил её.
- `make platform-test` — exit `0`; Airflow run
  `api_smoke_20260905T183405699692Z_132ccc11`, 11/11 tasks success; 68 dbt tests PASS.
- `make check` — exit `0`, 60 tests; `git diff --check` — exit `0`.

## Work log

- 2026-09-05: обнаружен новый user commit `0a6fb5f`; он закреплён как source revision manifest.
- 2026-09-05: реализованы manifest/schema, transactional reset, trusted record, logical data hash,
  public run и isolated hidden grade boundaries.
- 2026-09-05: проверены two-reset reproducibility, negative oracle path и полный platform regression.

Persistent evidence: [`../evidence/STEP-0005-scenario-harness.md`](../evidence/STEP-0005-scenario-harness.md).
