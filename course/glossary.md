# Glossary: определения и primary owners

Canonical краткие определения; подробные условия раскрываются один раз в owner lecture.

| Термин | Определение | Owner |
| --- | --- | --- |
| Agent loop | Ограниченная последовательность запросов модели, действий и observations до stopping condition. | [00](modules/module-00-agentic-baseline/README.md) |
| Role | Область ответственности; сама по себе не является process или security identity. | [01](modules/module-01-organization/README.md) |
| Executor | Runtime-единица обработки typed input/output; не владелец business policy по умолчанию. | [05](modules/module-05-maf-executors/README.md) |
| Contract | Проверяемые schema и invariants обмена; корректный формат не гарантирует истинность данных. | [02](modules/module-02-contracts/README.md) |
| Context | Информация, доступная модели в конкретном ходе; не вся durable state. | [03](modules/module-03-harness-context/README.md) |
| Isolation | Принудительное ограничение process/filesystem/network; не инструкция в prompt. | [08](modules/module-08-isolation/README.md) |
| MCP | Протокол взаимодействия host/client/server для предоставления capabilities; не бизнес-policy. | [09](modules/module-09-mcp-interface/README.md) |
| Grain | Смысл одной строки модели и условия её уникальности. | [11](modules/module-11-dbt-semantics/README.md) |
| Specification | Business semantics и acceptance constraints; unresolved facts требуют явной неопределённости. | [13](modules/module-13-pm-specification/README.md) |
| Provenance | Связь утверждения с источником/наблюдением и областью его применимости. | [12](modules/module-12-analyst-provenance/README.md) |
| Candidate | Ограниченный вариант изменения до независимой проверки и принятия. | [14](modules/module-14-data-engineer/README.md) |
| QA | Проверка evidence/defects отдельно от реализации; FAIL не исправляет продукт автоматически. | [15](modules/module-15-qa-evidence/README.md) |
| Reviewer | Read-only роль оценки результата и качества; не автор изменения. | [16](modules/module-16-review-authority/README.md) |
| Code-owned workflow | Код определяет допустимые переходы, stopping и gates; LLM reasoning может оставаться недетерминированным. | [06](modules/module-06-strict-workflow/README.md) |
| Agent-orchestrator | Модель определяет delegation/decomposition/replanning внутри внешних permission/budget boundaries. | [07](modules/module-07-agent-orchestrator/README.md) |
| State | Данные состояния выполнения; durable хранение и model context имеют разные жизненные циклы. | [04](modules/module-04-state-memory/README.md) |
| Checkpoint | Сохранённая граница возобновления; не гарантия exactly-once внешних side effects. | [17](modules/module-17-recovery-idempotency/README.md) |
| Idempotency | Повтор операции с той же identity не создаёт дополнительный разрешённый эффект. | [17](modules/module-17-recovery-idempotency/README.md) |
| Authorization | Принудительная проверка допустимости операции, отличная от аутентификации identity. | [19](modules/module-19-security-authority/README.md) |
| Trace | Связанная последовательность spans с causality/context, не доказательство semantic correctness. | [20](modules/module-20-observability/README.md) |
| Evaluation | Измерение поведения на определённых cases/trials/configuration; quality отличается от invariant PASS. | [21](modules/module-21-evaluation/README.md) |
| Hybrid orchestration | Model-directed investigation внутри code-owned outer policy/quality/write gates. | [24](modules/module-24-orchestration-comparison/README.md) |

Все 81 primary concept areas перечислены в manifest/ownership map; определения уточняются
при авторстве, не создаются как неподтверждённый подробный текст заранее.
