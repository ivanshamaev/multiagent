# Источники для теоретических лекций

Checked: 2026-09-15

## Правила отбора и переиспользования

Отобраны известные первичные инженерные статьи Anthropic, Cognition, Microsoft, LangChain, AWS,
Google, dbt, ClickHouse и Kubernetes, а также классические научные статьи ReAct/Dapper.
«Популярные» здесь — редакторский фильтр известных профессиональных публикаций и широко
обсуждаемых архитектурных материалов, не количественный рейтинг. Просмотры/число цитирований
для большинства страниц не опубликованы; не придумывать их и не приравнивать популярность
издателя к измеренной популярности каждой статьи. Для ключевых agent articles распространение
видно по публичным cross-references; для domain articles отбор основан на известных первичных
инженерных площадках. Перед авторством уточнять актуальность и source-specific claims.

Для каждой лекции ниже в её todo-плане указаны минимум две статьи, конкретная идея и ограничение.
Ссылки открыты при планировании; это не означает проверку каждой будущей формулировки лекции.
Своими словами пересказать выбранную концепцию, снабдить attribution и отделить её от нашего
design rationale. Не копировать статьи, полные переводы, чужие diagrams или их структуру целиком.
Критические позиции сопоставлять с ответами/обновлениями авторов; рекомендации не выдавать за theorem.
Стандарты и официальная документация будут дополнительными источниками проверки деталей при
авторстве, но список для идей состоит из статей, а не SDK documentation tutorials.

## S01 — Building effective agents

- Статья: [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).
- Авторская площадка: Anthropic.
- Что использовать и как ограничить перенос: Архитектурное различие workflows/agents; использовать определения, не копировать весь каталог паттернов.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S02 — How we built our multi-agent research system

- Статья: [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system).
- Авторская площадка: Anthropic.
- Что использовать и как ограничить перенос: Декомпозиция исследовательского поиска и делегирование; внутренние показатели не переносить на Data Engineering.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S03 — Don’t Build Multi-Agents

- Статья: [Don’t Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents).
- Авторская площадка: Cognition.
- Что использовать и как ограничить перенос: Скрытые решения и согласованность контекста; критика конкретных условий, не универсальный запрет.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S04 — Multi-Agents: What’s Actually Working

- Статья: [Multi-Agents: What’s Actually Working](https://cognition.com/blog/multi-agents-working).
- Авторская площадка: Cognition.
- Что использовать и как ограничить перенос: Разделение интеллектуального вклада и конкурирующих записей; сопоставить с более ранней позицией автора.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S05 — LangGraph: Multi-Agent Workflows

- Статья: [LangGraph: Multi-Agent Workflows](https://www.langchain.com/blog/langgraph-multi-agent-workflows).
- Авторская площадка: LangChain.
- Что использовать и как ограничить перенос: Graph, supervisor и hierarchical teams; архитектурная модель, не актуальный SDK tutorial.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S06 — Introducing Microsoft Agent Framework: The Open-Source Engine for Agentic AI Apps

- Статья: [Introducing Microsoft Agent Framework: The Open-Source Engine for Agentic AI Apps](https://devblogs.microsoft.com/foundry/introducing-microsoft-agent-framework-the-open-source-engine-for-agentic-ai-apps/).
- Авторская площадка: Microsoft.
- Что использовать и как ограничить перенос: Разделение agent/workflow orchestration; сравнивать с pinned runtime, не обещать все возможности статьи.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S07 — Effective context engineering for AI agents

- Статья: [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
- Авторская площадка: Anthropic.
- Что использовать и как ограничить перенос: Управление ограниченным контекстом; разделить per-turn selection и долговременное состояние.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S08 — Writing effective tools for agents — with agents

- Статья: [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents).
- Авторская площадка: Anthropic.
- Что использовать и как ограничить перенос: Tool ergonomics, ясные границы и полезный output; авторские рекомендации проверять в контексте системы.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S09 — Effective harnesses for long-running agents

- Статья: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).
- Авторская площадка: Anthropic.
- Что использовать и как ограничить перенос: Накопление прогресса и ложное завершение; harness не заменяет durable checkpoint protocol.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S10 — Beyond permission prompts: making Claude Code more secure and autonomous

- Статья: [Beyond permission prompts: making Claude Code more secure and autonomous](https://www.anthropic.com/engineering/claude-code-sandboxing).
- Авторская площадка: Anthropic.
- Что использовать и как ограничить перенос: Filesystem/network containment; продуктовые security statements не являются абсолютной гарантией.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S11 — Introducing the Model Context Protocol

- Статья: [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol).
- Авторская площадка: Anthropic.
- Что использовать и как ограничить перенос: Унифицированный tool/data interface; introduction не заменяет нормативную protocol specification.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S12 — Making retries safe with idempotent APIs

- Статья: [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/).
- Авторская площадка: AWS Builders’ Library.
- Что использовать и как ограничить перенос: Request identity и повторные side effects; не приравнивать idempotency к exactly-once execution.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S13 — Exponential Backoff And Jitter

- Статья: [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/).
- Авторская площадка: AWS Architecture Blog.
- Что использовать и как ограничить перенос: Распределение повторных запросов; инфраструктурный retry отличать от semantic rework.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S14 — Data Mesh Principles and Logical Architecture

- Статья: [Data Mesh Principles and Logical Architecture](https://martinfowler.com/articles/data-mesh-principles.html).
- Авторская площадка: Zhamak Dehghani / Martin Fowler.
- Что использовать и как ограничить перенос: Domain ownership/data product; наша платформа не объявляется реализацией Data Mesh.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S15 — Build and centralize metrics with the dbt Semantic Layer

- Статья: [Build and centralize metrics with the dbt Semantic Layer](https://www.getdbt.com/blog/build-centralize-and-deliver-consistent-metrics-with-the-dbt-semantic-layer).
- Авторская площадка: dbt Labs.
- Что использовать и как ограничить перенос: Согласованные metric definitions; dbt Semantic Layer не реализован в нашем примере.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S16 — Using Materialized Views in ClickHouse

- Статья: [Using Materialized Views in ClickHouse](https://clickhouse.com/blog/using-materialized-views-in-clickhouse).
- Авторская площадка: ClickHouse.
- Что использовать и как ограничить перенос: Аналитическая materialization; не смешивать incremental views с любыми mart tables или refresh semantics.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S17 — What is analytics engineering?

- Статья: [What is analytics engineering?](https://www.getdbt.com/blog/what-is-analytics-engineering).
- Авторская площадка: dbt Labs.
- Что использовать и как ограничить перенос: Моделирование аналитических данных как инженерная ответственность; отделить человеческую роль от agent capability.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S18 — Why data testing is essential for analytics engineering

- Статья: [Why data testing is essential for analytics engineering](https://www.getdbt.com/blog/data-testing).
- Авторская площадка: dbt Labs.
- Что использовать и как ограничить перенос: Data assertions и доверие к данным; реальные SQL assertions проверить по нашему validator.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S19 — Code Health: Google’s Internal Code Quality Efforts

- Статья: [Code Health: Google’s Internal Code Quality Efforts](https://testing.googleblog.com/2017/04/code-health-googles-internal-code.html).
- Авторская площадка: Google Testing Blog.
- Что использовать и как ограничить перенос: Code health beyond binary tests; не переносить организационные выводы на надёжность LLM без измерений.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S20 — Demystifying evals for AI agents

- Статья: [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).
- Авторская площадка: Anthropic.
- Что использовать и как ограничить перенос: Task/trial/grader/outcome, layered evaluation; trajectories не обязаны быть одинаковыми.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S21 — Quantifying infrastructure noise in agentic coding evals

- Статья: [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise).
- Авторская площадка: Anthropic.
- Что использовать и как ограничить перенос: Ресурсы как experimental variables; наши fixture races — отдельное retained evidence.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S22 — Three Tenancy Models For Kubernetes

- Статья: [Three Tenancy Models For Kubernetes](https://kubernetes.io/blog/2021/04/15/three-tenancy-models-for-kubernetes/).
- Авторская площадка: Kubernetes authors.
- Что использовать и как ограничить перенос: Модели разделения tenants; namespaces не объявлять достаточной security boundary.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S23 — ReAct: Synergizing Reasoning and Acting in Language Models

- Статья: [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629).
- Авторская площадка: Yao et al., original research paper.
- Что использовать и как ограничить перенос: Связь reasoning/action/observation; не воспроизводить private chain-of-thought.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S24 — Magentic-One: A Generalist Multi-Agent System for Solving Complex Tasks

- Статья: [Magentic-One: A Generalist Multi-Agent System for Solving Complex Tasks](https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/).
- Авторская площадка: Microsoft Research.
- Что использовать и как ограничить перенос: Task/progress ledgers и replanning; это внешний пример, не реализация нашего runtime.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S25 — Mitigating prompt injection attacks with a layered defense strategy

- Статья: [Mitigating prompt injection attacks with a layered defense strategy](https://blog.google/security/mitigating-prompt-injection-attacks/).
- Авторская площадка: Google GenAI Security Team.
- Что использовать и как ограничить перенос: Indirect injection и defense-in-depth; detection не заменяет permission enforcement.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S26 — Code execution with MCP: Building more efficient agents

- Статья: [Code execution with MCP: Building more efficient agents](https://www.anthropic.com/engineering/code-execution-with-mcp).
- Авторская площадка: Anthropic.
- Что использовать и как ограничить перенос: Стоимость tool definitions/results и альтернативная композиция; не предлагать новый execution scope.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S27 — Scaling Managed Agents: Decoupling the brain from the hands

- Статья: [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents).
- Авторская площадка: Anthropic.
- Что использовать и как ограничить перенос: Session/harness/sandbox как разные boundaries; hosted product не является зависимостью курса.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S28 — Apache Airflow 3 is Generally Available!

- Статья: [Apache Airflow 3 is Generally Available!](https://airflow.apache.org/blog/airflow-three-point-oh-is-here/).
- Авторская площадка: Apache Airflow authors.
- Что использовать и как ограничить перенос: API-first task execution и data orchestration; task execution interface не равен stable REST /api/v2.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S29 — Dapper, a Large-Scale Distributed Systems Tracing Infrastructure

- Статья: [Dapper, a Large-Scale Distributed Systems Tracing Infrastructure](https://research.google/pubs/dapper-a-large-scale-distributed-systems-tracing-infrastructure/).
- Авторская площадка: Google Research, original research paper.
- Что использовать и как ограничить перенос: Distributed trace context и sampling; trace не раскрывает внутреннюю причинность модели.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.

## S30 — Equipping agents for the real world with Agent Skills

- Статья: [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).
- Авторская площадка: Anthropic.
- Что использовать и как ограничить перенос: Progressive disclosure знаний; не смешивать author editorial skills с role runtime skills.
- Todo: [ ] перед лекцией перечитать релевантный раздел, проверить дату/актуальность и claim anchors.


