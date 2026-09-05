# STEP-0005 — Воспроизводимый scenario harness

Status: active
Owner: primary agent
Updated: 2026-09-05
Current step: определить manifest/reset contract и immutable grader boundary

## Goal

Создать воспроизводимый локальный harness для будущей benchmark-задачи Net Revenue. Два reset должны давать одинаковые данные, git/workspace state и baseline results; рабочий агент не должен видеть hidden expected results.

## Non-goals and affected paths

На этом шаге не подключаем LLM, Microsoft Agent Framework, MCP и не реализуем Net Revenue. Разрешены новые `scenarios/`, `grader/`, `contracts/`, `runtime/`, tests, Make/config и `plan/**`. Не меняем golden seed/dbt expected values без отдельного defect и ADR.

## Acceptance criteria

- [ ] Versioned scenario manifest фиксирует ID, исходный commit, разрешённые пути, budgets, setup, public gates и hidden grade interface.
- [ ] Reset создаёт отдельный disposable workspace и не меняет основной checkout.
- [ ] Два reset дают одинаковые checksums файлов и ClickHouse baseline.
- [ ] Public task materials не раскрывают hidden SQL/expected results.
- [ ] `scenario-run` и `scenario-grade` имеют разные capability boundaries и deterministic exit codes.
- [ ] Unit, policy, integration и adversarial tests проверяют traversal, protected paths, stale state и grader isolation.
- [ ] Make targets и fresh evidence документируют полный lifecycle без LLM calls.

## Risks and decisions required

Git worktree и Docker volumes могут сохранять state между прогонами; destructive reset допускается только внутри явно созданного scenario workspace и fixture databases. Hidden grader в одном checkout недостаточно изолирован от недоверенного кода. До реализации нужны ADR о workspace lifecycle и grader process/filesystem boundary.

## Implementation steps

1. Инвентаризировать current Make/dbt/ClickHouse boundaries и определить manifest JSON Schema/Pydantic model.
2. Принять ADR для disposable git workspace, scenario database naming и hidden grader isolation.
3. Реализовать `scenario-init/reset/status` с явными target validation и checksums.
4. Добавить public validator interface; hidden grader хранить вне agent-mounted workspace.
5. Проверить два чистых reset, intentional contamination recovery и deny tests.
6. Сохранить transcript, закрыть проблемы и только затем начать contracts/workflow phase.

## Planned verification

Минимум: `make check`, schema/unit tests, два последовательных reset с одинаковым fingerprint, public baseline build, independent hidden grade, protected-path adversarial tests и `git diff --check`.
