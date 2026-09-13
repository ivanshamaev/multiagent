# STEP-0020 — Phase J: branching, rework and role idempotency

Status: completed

## Goal

Расширить six-role MAF graph управляемыми `BLOCKED`/`FAILED` terminal branches и bounded
`Validator|QA|Reviewer FAIL → DE REWORK` cycles. Закрыть crash window между завершением role
handler и следующим MAF checkpoint через durable idempotency receipt.

## Scope

- заменить линейные edges на code-owned MAF switch/case routes по validated snapshot stage;
- хранить историю gate artifacts и текущую попытку без потери accepted reducer history;
- направлять `REWORK` только в Data Engineer, а `BLOCKED`/`FAILED` — в terminal executor;
- ограничить cycles существующим reducer budget и общим MAF `max_iterations`;
- ввести owner-only, repository-contained, create-only role receipt store;
- вычислять operation key из workflow, executor, входной revision и payload hash;
- при повторном входе возвращать сохранённый validated output, не вызывая handler;
- доказать process kill после receipt, но до MAF checkpoint, rework routing и exhaustion.

Не входят: exactly-once для произвольного side effect внутри handler без idempotency key,
OpenTelemetry и отдельные OS/container identities.

## Acceptance criteria

1. PM/DE/Validator/QA/Reviewer допускают только свои явные success/terminal/rework outcomes.
2. Validator, QA и Reviewer `REWORK` возвращают управление DE; после ремонта pipeline снова проходит
   Validator → QA → Reviewer. Reducer budget завершает исчерпанный цикл как `FAILED`.
3. Terminal executor выдаёт единственный typed output и не запускает downstream roles.
4. Snapshot сохраняет все accepted gate artifacts, запрещает переписывание history и проходит
   event-chain validation на каждом hop.
5. Receipt path и ID fail closed при escape/symlink/loose mode/collision/corrupt data; secrets и
   прикладные pickle-типы не сохраняются.
6. SIGKILL после durable receipt и до MAF checkpoint приводит к cache hit после restart; handler
   текущей роли и уже committed роли не повторяются.
7. Targeted tests и `make check` проходят; Docker остаётся остановлен.

## Implementation sequence

1. Принять ADR-0029 о stage routing и durable role receipts.
2. Версионировать snapshot для artifact history и terminal/rework boundaries.
3. Реализовать receipt store и idempotent executor wrapper.
4. Собрать switch/case graph и terminal sink.
5. Добавить happy, blocked, rework, exhaustion, hostile storage и process recovery tests.
6. Записать evidence, обновить roadmap и remaining risks.

## Verification record

- `make role-pipeline-test` — exit 0, 13 passed: happy path, PM blocked, Validator/QA/Reviewer
  rework, budget exhaustion, receipt storage и два process recovery сценария.
- `make check` — exit 0, 395 tests passed; Ruff, format, plan governance и Compose config PASS.
- SIGKILL №1: resume iteration 3 после committed DE не повторил Analyst/PM/DE.
- SIGKILL №2: процесс убит после сохранения DE receipt, но до iteration 3 checkpoint; resume с
  iteration 2 получил receipt hit. Все persisted role counters, включая DE, равны 1.
- `docker compose ps --format json` — exit 0, пустой вывод; контейнеры не запускались.

Реализован graph `agentic-data-role-pipeline-v2`: native MAF switch/case, terminal output executor,
`REWORK → DE`, artifact attempt ledger и hard limit 32 supersteps. `SecureRoleReceiptStore` использует
contained 0700 directory, mode-0600 JSON, SHA-256 integrity, deterministic operation IDs, atomic
create-only hard-link publication и collision rejection.

Remaining risks: receipt не может гарантировать exactly-once, если процесс погиб внутри
неидемпотентного внешнего side effect до возврата handler. Role tools должны принимать operation ID
или реализовать read-after-timeout reconciliation. Retention/garbage collection receipts и
checkpoints также ещё не определены. Следующий Phase J slice — OpenTelemetry tracing; затем runner
identity, filesystem/network isolation и MCP authentication.
