# STEP-0025 — Phase L: каркас глубокого теоретического курса

Status: complete

Owner: Codex

Updated: 2026-09-15

## Goal и актуальный scope

Спланировать и затем создать Markdown-каркас курса **Multi-Agent Engineering: теория управляемых
команд агентов для Data Engineering**. Цель — глубокая теоретическая база: модели, архитектура,
инварианты, причинно-следственные связи, ограничения и trade-offs. Наша Agentic Data Platform —
сквозной иллюстративный пример, а не лабораторное задание.

По уточнению пользователя **лабораторные работы и практика полностью исключены**. Нет coding
tasks, инструкций студенту по развёртыванию, обязательных запусков, submissions, hidden grading,
paid tracks и capstone-задания. Возможны схемы, короткие фрагменты кода/SQL и разборы исторических
отказов, если они объясняют теорию; от читателя не требуется их выполнять.

Созданы todo-планы, source registry и course scaffold; тексты лекций ещё не написаны.
Лекции предназначены только для `course/lectures/`; планы — для `plan/steps/lections/`.
В `course/lectures/` только README; остальные course documents/outlines/checker и editorial skills созданы.
STEP-0025 завершён после проверки каркаса; следующая реализация требует отдельного шага.

Проверки текущего среза: [индивидуальные планы и источники](../evidence/STEP-0025-lecture-todo-source-planning.md).

Разрешённый scope текущей revision: STEP-0025, ADR-0034/index, planning evidence, progress/roadmap/
status, `plan/steps/lections/**`, вводные course statements в README/Claude. При реализации: `course/**`, course policy tests
и Make integration. Не менять `init/`, runtime, agents, policies, Data Platform, grader и corpora.

## Источники, аудитория и адаптация

- [Исходный syllabus](../../init/init_cource_plan.md): прочитан полностью; сохраняем тематические
  IDs 0–25, но не требования 60% практики, 70–100 часов, labs и capstone implementation.
- [ADR-0034](../decisions/ADR-0034-theory-course-and-editorial-gates.md) заменяет учебные practice/
  grading требования [ADR-0007](../decisions/ADR-0007-evidence-based-course.md), сохраняя provenance.
- [Roadmap](../development-plan.md), code/config и `plan/{decisions,problems,experiments,evidence}/`
  подтверждают примеры нашей системы. `init/` не является execution evidence.
- [STEP-0024](../evidence/STEP-0024-phase-k-evaluation-benchmark.md): offline invariant checks
  отделены от historical live model quality; в лекциях это различие обязательно.

Аудитория: Data Engineers с Python/SQL и базовым пониманием data pipelines. Agent concepts
объясняются от определений до advanced system design. Не ограничивать материал уровнем «101»:
после интуитивной модели давать строгие условия, контрпримеры, сравнение альтернатив и ограничения.
Прежняя оценка 89 часов (theory + practice) снята. Объём лекций/чтения оценивается после пилота;
часы реализации системы не превращаются в часы теоретического курса.

Конфликты исходного syllabus с примером нашей реализации отмечаются явно:

- Analyst → PM → DE → Validator → QA → Reviewer, а не PM-first/direct A2A.
- Ubuntu `uv`/`.venv` и Bubblewrap identities; Docker — Data Platform/observability, не пять role containers.
- PM tool-free, QA read-only; независимые checks принадлежат Validator, исправления — DE.
- Airflow GET observer отделён от controlled approved/idempotent dev-DAG trigger; нет agent admin scope.
- Telemetry content-free: никаких prompts/raw tool outputs/credentials/exception bodies.
- Live requirements подтвердил `BLOCKED/needs_user`; fully-live six-role READY/merge не доказан.

A2A, memory, skills и Kubernetes можно объяснять теоретически с первичными источниками и пометкой
«не реализовано в нашем примере». CLV/automated release не выдавать за возможности текущей системы.

## Дополнение: два способа управления командой и согласованность лекций

По новому запросу пользователя курс равноценно рассматривает code-owned жёсткий workflow и
LLM agent-orchestrator: planner/manager выбирает исполнителя, декомпозицию и перепланирование.
Dynamic orchestration не равна A2A: supervisor может быть in-process и вызывать агентов как tools.
Теоретическое описание не разрешает менять runtime, который остаётся deterministic control plane.

Лекция 15 владеет механикой workflow, 16 — механикой agent-orchestrator (теперь core), новая 26 —
сравнением/применимостью/гибридом. Лекция 01 ограничена декомпозицией ответственности; 25 синтезирует
наш пример без повторного обзора паттернов. 24 остаётся необязательным Kubernetes extension.
Итого: 27 отдельных todo-планов, 26 core topics + одно extension; исходные IDs 0–25 сохранены.

Для каждого плана нужны boundaries «входит/не входит», prerequisites, ссылки на соседние темы,
уникальное владение concepts и проверенные интернет-статьи с точным способом переиспользования идей.
Общий index/concept map контролирует повторы и порядок; при авторстве определяется одна primary
лекция для определения термина, остальные только применяют его и ссылаются на владельца.
Подбор источников ограничен известными широко обсуждаемыми первичными статьями; popularity не
подменяется fabricated view/citation counts и не считается доказательством технической истинности.

## Текущий срез: технический формат лекций и диаграмм

До написания лекций определить `course/technical-requirements.md`: Markdown-профиль,
формат диаграмм, доступность, контракты будущей сборки static HTML и gates проверки.
Разрешённые изменения этого среза: этот шаг, ADR/index, course requirements/README,
индекс todo-планов, Claude.md и planning evidence/progress. Сборщик, установка dependencies
и публикация сайта сейчас не входят в scope.

- [x] Изучить диаграмму взаимодействия из указанного пользователем материала DataTalks.
- [x] Зафиксировать решение до оформления требований: Mermaid в Markdown, SVG на build stage.
- [x] Описать последовательности, ветвления, подписи, accessible fallback и zoom/pan/fullscreen.
- [x] Добавить собственный Markdown-пример полного tool loop без копирования чужого SVG.
- [x] Проверить документы и ссылки; отдельно указать, что render/build ещё не реализован.

Документ: [технические требования](../../course/technical-requirements.md).
Решение: [ADR-0036](../decisions/ADR-0036-markdown-diagrams-static-svg.md).
Результаты: [planning evidence](../evidence/STEP-0025-lecture-technical-requirements.md).

Приёмка: requirements доступны всем lecture plans, содержат пример `sequenceDiagram`,
чётко отделяют Markdown source от HTML enhancement и задают критерии будущей сборки.
Риски: различия Markdown engines, версии Mermaid, SVG/CSP, маленькие экраны и ложные claims
о проверке ненаписанного renderer; mitigation — pinned build toolchain и будущие render tests.

## Требования: Skills для авторства и редакторской работы

| Skill | Назначение | Доступность и обязательность |
| --- | --- | --- |
| `technical-markdown-lectures` | Русская техническая проза, определения, логика лекции, схемы, примеры, резюме | Доступен: `/home/ivan/.codex/skills/technical-markdown-lectures/SKILL.md`; обязателен при авторстве и структурной вычитке |
| `technical-editorial-review` | Отдельный проход: язык, связность, терминология, повторы, переходы, соответствие глубины аудитории | Создан: course/skills и локальная копия; validated, обязателен при вычитке |
| `technical-claim-verification` | Отдельный проход: реестр утверждений, проверка первичных источников/code/evidence, соответствие схем и чисел | Создан: course/skills и локальная копия; validated, обязателен при technical review |
| `skill-creator` | Создать два указанных локальных skills с checklists и форматом review records | Доступен; применять при отдельной подготовке skills, не подменять им вычитку |
| `openai-docs` | Проверка утверждений именно об OpenAI API/SDK/models, если они появятся в лекции | Доступен; условный, не источник документации MAF/MCP/GateLLM и не общий редактор |

Это редакторские инструменты автора, не skills layer внутри Agentic Data Platform. Плагины и
runtime skills не менялись. В implementation slice подготовлены два self-contained skill,
прочитаны инструкции и выполнен quick_validate. При будущем review каждой лекции usage/versions
фиксируются отдельно; наличие установленного skill само по себе не доказывает выполненный review.

Для каждого использованного skill читать полный `SKILL.md` и обязательные references перед работой.
В lecture review record отмечать применённые skills и их версии/источники. Пользовательское
требование глубокой теории важнее default «101»; практические элементы исходного шаблона исключены.

## Обязательная вычитка и перепроверка каждой лекции

Статусы: `outline → draft → editorial-reviewed → technically-verified → reviewed`.
Переходы отражают реальные проходы, а не автоматическую проверку наличия файла.

1. **Авторство:** сверить prerequisites/outcomes, определить термины, построить объяснение
   от модели до ограничений, добавить релевантный пример нашей системы и первичные источники.
2. **Редакторская вычитка после написания:** прочитать всю лекцию отдельным проходом, исправить
   русский язык, смысловые скачки, неоднозначные формулировки, англицизмы, повторы и несогласованные
   термины; сверить объём с соседними лекциями, проверить читаемость схем/таблиц.
3. **Техническая перепроверка после вычитки:** проверить определения, предпосылки, причинность,
   архитектурные заявления, числа/версии/даты, код/SQL и соответствие схем тексту. Каждое существенное
   проверяемое утверждение должно иметь source anchor или быть явно помечено как предположение.
4. **Исправления:** записать замечание → источник → решение → исправленный фрагмент; перепроверить
   затронутые разделы и согласованность всей лекции. Существенная переработка требует полной вычитки.
5. **Gate публикации:** нет unresolved factual/structural issues; источники и ссылки валидны;
   `reviewed` разрешён только при завершении обоих review passes и повторной проверки исправлений.

Условия проверки: примеры реализации — code + dated evidence; общие технические положения —
первичная документация/стандарты/оригинальные papers. Не обобщать наш design choice до универсального
правила и не выдавать unit-test PASS за качество LLM. Актуальные внешние версии/API/цены проверять
при авторстве; исторические измерения оставлять с датой и provenance. Неразрешимая неопределённость
означает ограничить/удалить утверждение или честно обозначить границу, а не придумывать подтверждение.

Review record на каждую лекцию: lecture ID/content hash, дата, reviewer, skills, проверенные
sources/claims, editorial/factual findings, исправления, unresolved issues и итог. Изменение текста
после review делает receipt stale и требует новой проверки. Проходы может выполнять тот же автор:
они раздельные, но **не называются независимым review**, если другой reviewer не участвовал.
Внешний редактор/субагент не обязателен; этот план не даёт разрешения на делегирование.

## Предлагаемая полная структура — пока не реализована

```text
course/
  README.md                    # аудитория, теоретический формат, маршруты, статусы
  syllabus.md                  # outcomes, prerequisites, последовательность лекций
  manifest.json                # stable IDs, paths, authoring status, source anchors
  source-index.md              # init → тема → theory sources → наш пример/evidence
  glossary.md                  # единые определения и терминология
  editorial-guidelines.md      # глубина, стиль, обязательные review gates, skills
  technical-requirements.md   # создан: Markdown, Mermaid, SVG и static HTML contract
  templates/
    module.md
    lecture.md
    review.md
  modules/
    module-00-agentic-baseline/README.md
    ...                        # 26 core outlines, включая 16/26
  lectures/                    # только тексты лекций LECTURE-NNNN-*.md
  extensions/
    module-24-kubernetes-runtime/README.md
  reviews/                     # per-lecture вычитка и technical verification records
  check.py                     # offline metadata/link/review-receipt checks
```

Не создавать `labs/`, lab templates, assessment/submission рубрики или capstone assignments.
Manifest — canonical metadata; numbering сохраняет связь с `init/`, но не задаёт teaching order.
Статус authoring отделён от evidence примера (`offline-proven`, `historical-live`,
`not-implemented`). Теоретическая extension может быть reviewed при проверенных источниках,
но это не меняет implementation status нашей системы.

## Тематическая карта 0–26

Для каждой темы нужно объяснение общего принципа, trade-offs и границ применимости; code anchors
иллюстрируют принцип, а не превращают лекцию в построчный walkthrough или задание.

| ID / тема | Теоретический фокус | Пример нашей системы / source anchor |
| --- | --- | --- |
| 00 Agentic Engineering Baseline | Agency, autonomy, stochastic reasoning и deterministic environment | `runtime/agent_runtime.py`; STEP-0007 |
| 01 Designing the Agent Organization | Decomposition, separation of duties, coordination patterns | `policies/profiles/`; STEP-0008 |
| 02 MAF Internals | Executors, edges, graph state, developer-owned control flow | `runtime/role_pipeline.py`; STEP-0019 |
| 03 Agent Contracts | Schemas, invariants, trust boundaries, contract vs prompt | `contracts/artifacts.py`; STEP-0006 |
| 04 Agent Harness | Context assembly, structured output, bounded retries и model abstraction | `runtime/model_provider.py`, `runtime/context.py`; STEP-0007 |
| 05 Environment Isolation | Process/filesystem/network/identity boundaries и fail-closed behavior | `runtime/runner_isolation.py`; STEP-0022 |
| 06 MCP Fundamentals | Protocol architecture, capability negotiation, transport vs authorization | `runtime/tools/mcp_gateway.py`; STEP-0008 |
| 07 ClickHouse MCP | Analytical read capabilities, SQL policy и resource bounds | `policies/tool_policy.py`; STEP-0008 |
| 08 dbt MCP | Declarative transformations, grain, lineage, validation и orchestration | `platform/dbt/`, Cosmos; STEP-0004 |
| 09 Airflow MCP | API boundaries, read/write separation, approvals и idempotency | `runtime/airflow_mcp_server.py`, trigger server; STEP-0014/0015 |
| 10 PM Agent | Specification semantics, unresolved requirements, epistemic limits | `runtime/specification.py`; STEP-0013 |
| 11 Data Analyst Agent | Facts vs assumptions, provenance, discovery-before-specification | `runtime/analyst.py`; STEP-0012 |
| 12 Data Engineer Agent | Bounded autonomy, semantics of metric implementation, validation vs reasoning | `runtime/data_engineer.py`, Net Revenue; STEP-0009 |
| 13 QA Agent | Independent evidence, mutation detection и defect acceptance | `runtime/qa_workflow.py`; STEP-0010 / EXP-0003 |
| 14 Reviewer Agent | Review authority, false approval, separation from implementation | `runtime/reviewer_workflow.py`; STEP-0011 / EXP-0004 |
| 15 Multi-Agent Workflow | Reducers, branching, convergence, terminal states и bounded rework | `runtime/role_pipeline.py`, `orchestrator/`; STEP-0020 |
| 16 Agent-orchestrator | Planning/delegation/replanning, workers-as-tools, task/progress ledgers; не равно A2A | Core theory alternative: manager-agent у нас не реализован; ADR-0035 |
| 17 State, Memory and Artifacts | Context vs durable state vs knowledge, consistency и visibility | `runtime/context.py`, contracts; STEP-0019; long-term memory не реализована |
| 18 Checkpointing and Recovery | Commit boundaries, failure windows, receipts, idempotency vs exactly-once | `runtime/checkpoints.py`, `runtime/role_receipts.py`; STEP-0018/0024 |
| 19 Security Engineering | Untrusted content, least privilege, authentication vs permission enforcement | `runtime/mcp_auth.py`, adversarial tests; STEP-0022 |
| 20 Observability & Debugging | Trace causality, content-free telemetry, sampling/cardinality/retention | `runtime/telemetry.py`, `observability/`; STEP-0021/0023 |
| 21 Evaluation Engineering | Reliability vs model quality, baselines, sampling uncertainty и regression | `evals/phase_k/`; STEP-0024 |
| 22 Multi-Agent Failure Modes | Root-cause taxonomy, premature success, correlated failures и retry amplification | PRB-0035/0051/0052; regression evidence |
| 23 Cost & Performance Engineering | Budget allocation, quality/cost trade-off, dated pricing и context limits | `runtime/model_provider.py`; STEP-0009 sample / EXP-0001 |
| 24 Kubernetes Agent Runtime | Deployment identity, cgroups/seccomp/network policies, trade-offs локального runtime | Extension: Kubernetes не реализован; ADR-0001 |
| 25 Итоговый архитектурный синтез | Как контракты, control flow, tools, isolation и evidence складываются в систему | Net Revenue design review, не capstone-задание; STEP-0010/0020/0024 |
| 26 Сравнение orchestration approaches | Workflow vs manager-agent vs hybrid: trade-offs и task scenarios | Теоретическое сравнение, наш workflow как baseline; ADR-0035 |

Маршрут, prerequisites и primary topic ownership теперь заданы в [lecture index](lections/README.md)
и `lections/lecture-map.json`; они заменяют прежнюю последовательность.
16 теперь core theory, 24 — optional extension; 26 предшествует архитектурному синтезу 25.

## Контракт лекции

Обязательные части: цель/место в системе → термины → интуитивная модель → строгие условия и
инварианты → устройство/полезная схема → альтернативы и trade-offs → границы/контрпримеры →
иллюстрация нашей системой с источниками → типичные ошибочные представления → резюме → переход.
3–5 концептуальных self-check questions допустимы как часть текста без заданий на запуск/реализацию.

Глубина означает объяснять «почему» и «при каких условиях», а не увеличивать объём повторениями.
Код/SQL только минимальный для демонстрации концепции; командные инструкции и exercises исключены.
Структурные схемы должны соответствовать изложению; Mermaid/ASCII/table используются по необходимости.

## План реализации каркаса

Implementation slice 2026-09-15: разрешены `course/**`, два локальных editorial skills,
`tests/policy/test_course_governance.py`, Makefile и pinned dev dependency/uv.lock для Markdown AST.
Основной gate — offline scaffold checker. HTML/SVG renderer остаётся отдельным prototype slice
после каркаса: acceptance STEP-0025 не требует publication/browser checks, но требует честного
backlog и отсутствия published/reviewed лекций без соответствующих checks. Docker не запускается.

- [x] Прочитать исходный syllabus и сопоставить его с implementation evidence.
- [x] Принять уточнение пользователя: theory-only; снять labs/practice/hours/capstone requirements.
- [x] Принять ADR-0034 и перечислить Skills с честными availability/usage requirements.
- [x] Создать todo-планы 27 лекций в `plan/steps/lections/`; тексты отделить в `course/lectures/`.
- [x] Подобрать интернет-статьи, идеи для каждого плана и ограничения переноса.
- [x] Развести topic ownership/prerequisites; добавить workflow/manager-agent/comparison plans.
- [x] Создать README/syllabus/manifest/source-index/glossary/editorial-guidelines без student setup.
- [x] Добавить module/lecture/review templates; обязательный per-lecture workflow описать в каждом.
- [x] Создать 26 core outlines и optional extension 24; ID 25 — синтез, 26 — сравнение.
- [x] Добавить checker/policy regressions; `make course-check` подключить к `check`.
- [x] Проверить links/IDs/prerequisites/statuses/review receipts и отсутствие lab/assignment требований.
- [x] Обновить contributor/runbook ссылки, выполнить gates и сохранить scaffold evidence.

Editorial skills подготовлены через `skill-creator`, прочитаны и validated. Далее prototype renderer
и pilot lectures 00/03/08 отдельным шагом. Каждая лекция
проходит весь review cycle сразу после написания, не общую вычитку только в конце курса.

## Acceptance criteria STEP-0025

1. Каркас содержит 27 stable IDs: 26 core topics + extension 24; ID 25 — синтез, ID 26 — сравнение.
2. Нет лабораторных, practical tracks, student setup/tasks/submissions, hidden grading и capstone-задания.
3. Каждый module outline содержит теоретические outcomes/prerequisites, sources, иллюстрацию нашей
   системы и known gaps; mapping к `init/` не выдаёт proposed возможности за implementation.
4. В requirements/templates перечислены Skills, включая availability; отсутствующие skills не
   заявлены используемыми. Структура требует advanced theory и отсутствие повтора соседних лекций.
5. После каждой лекции обязательны вычитка, technical verification, исправления и recheck;
   reviewed запрещён при missing/stale review record или unresolved существенных замечаниях.
6. Checker/tests отклоняют duplicate/missing ID, broken/escaping links, dependency cycles и
   несогласованный review status/hash. Checker не утверждает, что автоматически проверил смысл текста.
7. `make course-check`, policy regressions, `make check`, `git diff --check` проходят; точные exit
   codes и gaps сохраняются в evidence. Runtime/policies/grader не меняются; контейнеры не запускаются.

## Verification и risks

Implemented gates: `make course-check`, course policy regressions, `make check`, `git diff --check`.
Lecture reviews/render gates ещё не выполнены: лекции/renderer отсутствуют. Scaffold PASS
не является публикационным gate будущих текстов.
Не заявлять редакторскую проверку только по Markdown lint. Не вводить в курс секреты/raw payloads.
При необходимости technical verification делает read-only inspection и source lookup, но не
расширяет scope до изменения системы/paid calls. Ссылки/примеры проверяются на актуальную revision.

## Decisions и work log

- 2026-09-15: STEP-0025 завершён. Созданы manifest/syllabus/glossary/source-index, 27 outlines,
  templates, versioned/editorial skills и offline checker. `make check`: exit 0, 479 passed;
  28 новых course tests. PyPI/внешние sources восстановились при повторной проверке.
  [Scaffold evidence](../evidence/STEP-0025-theory-course-scaffold.md) фиксирует команды и gaps.
  Тексты/render/publication не выполнены и не входят в scaffold completion claim.

- ADR-0034 supersedes учебные practice/grading requirements ADR-0007; `init/` остаётся неизменным.
- Первоначальный practical scaffold plan и оценка 89 часов superseded явным уточнением пользователя.
- 2026-09-15: обновлён STEP-0025 под глубокий theory-only курс; добавлены Skills requirements и
  обязательный per-lecture review cycle. Scaffold/skills/lectures пока не реализованы.
- Предыдущее [planning evidence](../evidence/STEP-0025-course-scaffold-planning.md) относится к
  прежней версии; текущая проверка фиксируется в отдельном theory-revision evidence.
- 2026-09-15: подготовлены 27 todo-планов, 30 первичных интернет-статей, ownership map и prerequisites.
  Dedicated сравнение включает десять scenarios. Тексты лекций не написаны; STEP-0025 остаётся активным.
