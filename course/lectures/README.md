# Теоретические лекции по Multi-Agent Engineering

Отдельная директория для текстов лекций `LECTURE-NNNN-<topic>.md`.
Написана [лекция 00](LECTURE-0000-agentic-baseline.md): agency, обратная связь
и ограниченный agent loop. [Лекция 01](LECTURE-0001-organization.md) объясняет разделение
ответственности, связность задач и цену координации. [Лекция 02](LECTURE-0002-contracts.md)
разделяет schema, invariants, contextual binding и предметную корректность.
[Лекция 03](LECTURE-0003-harness-context.md) рассматривает harness, контекст одного
вызова и provider boundary. [Лекция 04](LECTURE-0004-state-memory.md) разделяет
контекст, состояние, артефакты и долговременное знание.
[Лекция 05](LECTURE-0005-maf-executors.md) объясняет executors, edge delivery и
typed graph boundary. [Лекция 06](LECTURE-0006-strict-workflow.md) разбирает
code-owned переходы, terminal outcomes и bounded rework. [Лекция 07](LECTURE-0007-agent-orchestrator.md)
разбирает model-directed planning и ограниченное делегирование как альтернативу,
которая в нашем runtime не реализована. [Лекция 08](LECTURE-0008-isolation.md)
объясняет границы процесса, файловой системы и сети. [Лекция 09](LECTURE-0009-mcp-interface.md)
разделяет MCP-интерфейс, семантику tools и code-owned разрешение вызова.
[Лекция 10](LECTURE-0010-analytical-sql.md) объясняет область аналитического чтения,
SQL-ограничения и составной read capability. [Лекция 11](LECTURE-0011-dbt-semantics.md)
разбирает grain, lineage и доказательную силу dbt-проверок.
[Лекция 12](LECTURE-0012-analyst-provenance.md) объясняет происхождение
наблюдений Analyst и границу фактов, предположений и вопросов.
[Лекция 13](LECTURE-0013-pm-specification.md) разбирает определение метрики,
readiness и допустимый исход NEEDS_USER.
[Лекция 14](LECTURE-0014-data-engineer.md) объясняет пределы автономии DE,
границу candidate и semantic repair. [Лекция 15](LECTURE-0015-qa-evidence.md)
разбирает независимый QA-probe, mutation detection и evidence-backed defect.
[Лекция 16](LECTURE-0016-review-authority.md) объясняет review authority,
false approval и maintainability judgment. [Лекция 17](LECTURE-0017-recovery-idempotency.md)
разделяет checkpoint, role receipt и идемпотентность внешнего эффекта.
[Лекция 18](LECTURE-0018-airflow-operations.md) разводит Airflow data DAG и
агентский workflow, read-only Observer и approved dev-DAG Trigger.
[Лекция 19](LECTURE-0019-security-authority.md) объясняет indirect prompt
injection, authentication, authorization и границы повышения полномочий.
[Лекция 20](LECTURE-0020-observability.md) разделяет trace, event log,
metrics и provenance, объясняет propagation, sampling и cardinality.
[Лекция 21](LECTURE-0021-evaluation.md) определяет task, trial, outcome и
grader, разделяет regression invariants, live samples и fresh comparisons.
[Лекция 22](LECTURE-0022-failure-taxonomy.md) разводит observable symptoms
и причины, common-mode correlation и retry amplification.
[Лекция 23](LECTURE-0023-cost-performance.md) связывает total cost, budgets,
critical path, parallel work и quality-constrained optimization.
[Лекция 24](LECTURE-0024-orchestration-comparison.md) сравнивает code-owned
workflow, agent-orchestrator, bounded hybrid и более простые альтернативы по
свойствам задачи и риску действий.
Все двадцать пять опубликованы после отдельных content/publication gates;
оставшиеся 2 темы — core-план 25 и optional extension 26.
Для остальных тем подготовлены [индивидуальные todo-планы](../../plan/steps/lections/README.md)
и [реестр источников](../../plan/steps/lections/SOURCES.md).

Формат, схемы и будущая HTML-сборка: [технические требования](../technical-requirements.md).

Курс рассматривает жёсткий workflow, управление командой агентом-оркестратором и гибридные
архитектуры. Наша Agentic Data Platform служит иллюстрацией подтверждённых решений; динамический
manager и Kubernetes не объявляются реализованными возможностями.

Лабораторных работ и практических заданий нет. После написания каждой лекции обязательны
редакторская вычитка, проверка технических утверждений и источников, повторная проверка после
исправлений и фиксация проверенной версии. Планы остаются в `plan/steps/lections/`.
