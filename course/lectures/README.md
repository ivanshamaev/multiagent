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
наблюдений Analyst и границу фактов, предположений и вопросов. Все тринадцать
опубликованы после отдельных content/publication gates; остальные 14 тем — планы.
Для остальных тем подготовлены [индивидуальные todo-планы](../../plan/steps/lections/README.md)
и [реестр источников](../../plan/steps/lections/SOURCES.md).

Формат, схемы и будущая HTML-сборка: [технические требования](../technical-requirements.md).

Курс рассматривает жёсткий workflow, управление командой агентом-оркестратором и гибридные
архитектуры. Наша Agentic Data Platform служит иллюстрацией подтверждённых решений; динамический
manager и Kubernetes не объявляются реализованными возможностями.

Лабораторных работ и практических заданий нет. После написания каждой лекции обязательны
редакторская вычитка, проверка технических утверждений и источников, повторная проверка после
исправлений и фиксация проверенной версии. Планы остаются в `plan/steps/lections/`.
