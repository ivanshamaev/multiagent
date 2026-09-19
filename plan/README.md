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
- [STEP-0043](steps/STEP-0043-lecture-analyst-provenance.md) публикует лекцию 12
  об ограниченном discovery и evidence-backed data facts перед PM handoff.
  Опубликованы 00–12; далее 13, PM specification.
- [STEP-0044](steps/STEP-0044-lecture-pm-specification.md) публикует лекцию 13
  о business metric definition, readiness и корректном NEEDS_USER при
  существенной неопределённости. Опубликованы 00–13; далее 14, DE.
- [STEP-0045](steps/STEP-0045-lecture-data-engineer.md) публикует лекцию 14
  об implementation authority, изолированном candidate и semantic repair.
  Публикационный gate v2 проверяет только текст и статическую собираемость,
  без скриншотов/визуальной вычитки. Опубликованы 00–14; далее 15, QA.
- [STEP-0046](steps/STEP-0046-lecture-qa-evidence.md) публикует лекцию 15
  о независимом QA-probe, mutation detection и evidence-backed defect.
  Text-only gate сохранён. Опубликованы 00–15; далее 16, Reviewer.
- [STEP-0047](steps/STEP-0047-lecture-reviewer-authority.md) публикует
  лекцию 16 о праве Reviewer принять или вернуть candidate, качестве кода
  и рисках false approval/rejection. Опубликованы 00–16; далее 17, Recovery.
- [STEP-0048](steps/STEP-0048-lecture-recovery-idempotency.md) публикует
  лекцию 17 о checkpoint, role receipt и идемпотентности внешнего эффекта.
  Опубликованы 00–17; далее 18, Airflow API.
- [STEP-0049](steps/STEP-0049-lecture-airflow-operations.md) публикует
  лекцию 18 о границе Airflow data DAG и агентского workflow, read-only
  Observer и approved dev-DAG Trigger. Опубликованы 00–18; далее 19, Security.
- [STEP-0050](steps/STEP-0050-lecture-security-authority.md) публикует
  лекцию 19 об indirect prompt injection, scoped identity, code-owned
  authorization и пределах локального bearer. Опубликованы 00–19;
  далее 20, Observability.
- [STEP-0051](steps/STEP-0051-lecture-observability.md) публикует лекцию 20
  о trace causality, propagation, sampling, cardinality и retention.
  Опубликованы 00–20; далее 21, Evaluation.
- [STEP-0052](steps/STEP-0052-lecture-evaluation.md) публикует лекцию 21
  о task/trial/outcome/grader, режимах evaluation, baseline и
  статистической неопределённости. Опубликованы 00–21; далее 22,
  Failure modes.
- [STEP-0053](steps/STEP-0053-lecture-failure-taxonomy.md) публикует лекцию
  22 о root-cause taxonomy, propagation, common-mode failures и retry
  amplification. Опубликованы 00–22; далее 23, Cost/performance.
- [STEP-0054](steps/STEP-0054-lecture-cost-performance.md) публикует лекцию
  23 о total cost, budgets, critical path, parallel work и
  quality-constrained optimization. Опубликованы 00–23; далее 24,
  orchestration comparison.
- [STEP-0055](steps/STEP-0055-lecture-orchestration-comparison.md) публикует
  лекцию 24 о выборе между fixed workflow, agent-orchestrator, bounded hybrid
  и более простой альтернативой. Опубликованы 00–24; далее 25,
  architecture synthesis.
- [STEP-0057](steps/STEP-0057-lecture-architecture-synthesis.md) публикует
  лекцию 25 об architectural closure, четырёх слоях платформы и
  evidence-bounded system claims. Все core-лекции 00–25 опубликованы;
  далее optional deployment theory 26.
- [STEP-0058](steps/STEP-0058-lecture-kubernetes-tenancy.md) публикует
  optional лекцию 26 о Kubernetes tenancy, resource governance и выборе
  deployment boundary. Курс содержит проверенные тексты 00–26; Kubernetes
  runtime остаётся `not-implemented`.
- [STEP-0059](steps/STEP-0059-github-repository-links.md) заменяет placeholder
  references на прямые GitHub blob links с сохранением fragments и оставляет
  `references.html` кликабельным индексом repository examples.
