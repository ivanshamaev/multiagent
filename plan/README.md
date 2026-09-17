# План и журнал разработки

Папка `plan/` — источник истины о ходе создания Agentic Data Platform. Исходные материалы в `init/` задают направление, но не подтверждают, что компонент уже реализован. Факт реализации подтверждают код, выполненная проверка и запись в журнале.

## Структура

- `development-plan.md` — общий roadmap, зависимости и контрольные точки.
- `steps/` — пошаговые рабочие планы. Одновременно активен только один основной шаг.
- `decisions/` — ADR с принятыми архитектурными решениями.
- `problems/` — воспроизводимые проблемы, причины, исправления и regression checks.
- `experiments/` — эксперименты с агентами, метрики и ссылки на evidence.
- `evidence/` — компактные persistent summaries выполненных validation gates.
- `progress.md` — короткая хронология фактически выполненной работы.

## Обязательный цикл работы

1. До изменения кода создать или актуализировать файл в `steps/`: цель, non-goals, затрагиваемые слои, риски, шаги и acceptance criteria.
2. До архитектурного выбора создать ADR. Принятое ADR не переписывать задним числом: новое решение должно явно заменить старое.
3. После каждого изменения выполнить узкую проверку, затем проверку затронутого слоя. Записать команду, exit code и путь к артефакту, если он сохраняется.
4. Любую нетривиальную или повторяемую проблему вынести в `problems/`. Закрывать системную проблему только после появления regression check.
5. Эксперименты с LLM проводить на фиксированном scenario baseline; сохранять модель, конфигурацию, число прогонов, метрики и наблюдаемые отказы.
6. По завершении шага обновить `progress.md`, остаточные риски и следующий шаг.

## Текущий статус

- Завершены [`STEP-0001`](steps/STEP-0001-repository-bootstrap.md)–[`STEP-0015`](steps/STEP-0015-controlled-dev-dag-trigger.md) и audit-remediation [`STEP-0017`](steps/STEP-0017-kimi-audit-remediation.md); summaries сохранены в `evidence/`.
- Phase G завершена: QA и Reviewer разделены, bounded rework повторяет validator/QA/Reviewer, а
  false pass/approval измерены на независимых мутациях.
- Phase H завершена: read-only Analyst discovery передаёт evidence-backed typed handoff tool-free
  PM, который выдаёт полный spec либо детерминированный `blocked / needs_user`.
- Phase I завершена: read-only observer отделён от approved/idempotent trigger единственного
  dev-DAG; identities, profiles и MCP processes не пересекаются.
- STEP-0018…0023 закрыли durable MAF checkpoints, branching/receipt idempotency, content-free OTel,
  отдельные Bubblewrap identities, authenticated MCP и operational observability backend. Phase J
  завершена. STEP-0024 добавляет Phase K offline regression benchmark и historical live provenance;
  свежая оценка качества модели остаётся отдельным opt-in платным gate.
- Завершён [STEP-0025](steps/STEP-0025-phase-l-course-scaffold.md): Phase L,
  [теоретический каркас](../course/README.md), 27 outlines, editorial Skills и обязательные
  review gates каждой лекции. `make course-check` подключён к `make check`.
  Тексты создаются отдельно в `course/lectures/`; пилотная лекция 00 написана в STEP-0029.
  [27 todo-планов](steps/lections/README.md) описывают границы, prerequisites, источники и comparison;
  тексты будут отдельно в `course/lectures/`.
- STEP-0026 добавляет [SVG/static HTML prototype](../course/build-status.md): locked renderer,
  allowlisted build, viewer и browser checks. Это не публикационный gate лекций.
- STEP-0027 зафиксировал [дизайн сайта](../course/design/site-design.md): Cyberpunk landing,
  SVG roadmap, программа слева и lecture TOC справа.
- STEP-0028 реализует этот UI для Markdown outlines: landing, linked roadmap, reader shell,
  responsive/no-JS navigation и build-time local link/ID checks; publication gate лекций не изменён.
- STEP-0029 добавляет пилотную теоретическую лекцию 00 с отдельными editorial/technical
  проверками и receipt; публикация выполнена следующим STEP-0030.
- [STEP-0030](steps/STEP-0030-lecture-publication-gate.md) вводит отдельные publication receipts,
  isolated candidate и проверенный full reader. Missing/stale passes запрещают публикацию.
- [STEP-0031](steps/STEP-0031-lecture-organization.md) добавляет лекцию 01, отдельную вычитку,
  primary-source verification и browser gate. Лекции 00/01 доступны в локальном reader;
  остальные 25 тем — outlines. Далее по teaching order — лекция 03, не 02.
- [STEP-0032](steps/STEP-0032-lecture-contracts.md) публикует лекцию 03 о schema,
  invariants, cross-task binding и пределах evidence. Лекции 00/01/03 доступны;
  остальные 24 темы — outlines. Далее по teaching order — лекция 04.
- [STEP-0033](steps/STEP-0033-lecture-harness-context.md) публикует лекцию 04 о harness,
  per-turn context selection и structured response boundary. Лекции 00/01/03/04
  доступны; остальные 23 темы — outlines. Далее по teaching order — лекция 17.
- [STEP-0034](steps/STEP-0034-course-sequential-numbering.md) перенумеровывает курс
  по порядку обучения: core 00–25, optional Kubernetes 26. Записи STEP-0031–0033
  выше исторические; текущие опубликованные ID — 00/01/02/03, далее 04.
- [STEP-0035](steps/STEP-0035-lecture-state-memory.md) публикует лекцию 04 о
  состоянии и памяти после content/browser gates. Опубликованы 00–04; далее 05.
- [STEP-0036](steps/STEP-0036-lecture-maf-executors.md) публикует лекцию 05 о
  MAF executors/edges и typed graph boundary. Опубликованы 00–05; далее 06.
- [STEP-0037](steps/STEP-0037-lecture-strict-workflow.md) публикует лекцию 06
  о code-owned transitions и bounded rework. Опубликованы 00–06; далее 07.
- [STEP-0038](steps/STEP-0038-lecture-agent-orchestrator.md) публикует лекцию 07
  о model-directed manager как альтернативе, не реализации. Опубликованы 00–07; далее 08.
- [STEP-0039](steps/STEP-0039-lecture-isolation.md) публикует лекцию 08 об
  изоляции исполнения и границах offline evidence. Опубликованы 00–08; далее 09.
- [STEP-0040](steps/STEP-0040-lecture-mcp-interface.md) публикует лекцию 09
  о MCP, semantic tool surface и границе protocol/policy. Опубликованы 00–09;
  далее 10, аналитический SQL.
- [STEP-0041](steps/STEP-0041-lecture-analytical-sql.md) публикует лекцию 10
  о read capability, SQL AST/resource envelope и границах materialization.
  Опубликованы 00–10; далее 11, dbt semantics.
- [STEP-0042](steps/STEP-0042-lecture-dbt-semantics.md) публикует лекцию 11
  о grain, lineage и границах dbt validation, отличая dbt-граф от Airflow DAG
  и агентского workflow. Опубликованы 00–11; далее 12, Analyst provenance.
