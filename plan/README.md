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

- Завершены [`STEP-0001`](steps/STEP-0001-repository-bootstrap.md)–[`STEP-0014`](steps/STEP-0014-read-only-airflow-mcp.md); persistent gate summaries сохранены в `evidence/`.
- Phase G завершена: QA и Reviewer разделены, bounded rework повторяет validator/QA/Reviewer, а
  false pass/approval измерены на независимых мутациях.
- Phase H завершена: read-only Analyst discovery передаёт evidence-backed typed handoff tool-free
  PM, который выдаёт полный spec либо детерминированный `blocked / needs_user`.
- Phase I начата: локальный Airflow MCP читает allowlisted DAG/run/task/log metadata через stable
  `/api/v2` под отдельным Viewer и deny-by-default policy.
- Следующий шаг Phase I — controlled trigger только для dev-DAG под отдельной write-capability.
