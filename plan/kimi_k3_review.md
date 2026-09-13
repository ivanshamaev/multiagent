# Аудит хода работ проекта — ревью репозитория

Date: 2026-09-13
Reviewer: kimi-k3 (техлид-ревьюер, внешний аудит)
Scope: весь репозиторий — governance (`plan/`), control-plane (`contracts/`, `orchestrator/`,
`runtime/`, `policies/`, `agents/`), Data Platform (`platform/`, `docker-compose.yml`),
scenario harness и grader (`scenarios/`, `grader/`), тесты (`tests/`), корневые рулбуки
(`AGENTS.md`, `Claude.md`, `README.md`).
Method: read-only аудит. Код не изменялся; выполнялись только проверки (см. раздел 2).

---

## 1. Резюме

Проект находится в **хорошем состоянии и опережает типичные ожидания для 9 дней работы**
(2026-09-04 → 2026-09-13). Из 13 фаз roadmap (0, A–L) полностью завершены восемь (0, A–H),
Phase I (Airflow integration) завершена примерно на 80%. Заявленные в плане инварианты —
«workflow кодом, а не промптами», deny-by-default, evidence-first, изолированный hidden
grader — **подтверждены чтением кода, а не только документацией**. Это редкое и ценное
свойство: большинство агентных проектов декларирует эти принципы, здесь они реализованы
в коде (`orchestrator/transitions.py`, `policies/tool_policy.py`, `runtime/tools/mcp_gateway.py`).

Критичных дефектов, блокирующих дальнейшую работу, **не обнаружено**. Текущее состояние
воспроизводимо: `make check` зелёный (371 тест), Compose-конфигурация валидна, сервисы
подняты и healthy.

Главные системные риски:

1. **Дрейф процесса журналирования в поздних фазах.** Код STEP-0015 (~1600 строк в коммите
   `ec31fa6 "update"`) уже в репозитории, но ни одной записи в `progress.md`, work log или
   evidence нет — прямое нарушение собственного обязательного цикла. Дисциплина
   документирования в фазах G–I заметно ниже, чем в 0–F, и держится на ручном труде без
   автоматической проверки.
2. **Supply-chain риск `httpx2`** — малоизвестный форк `httpx` в пути, где формируется
   `Authorization: Bearer $API_TOKEN`, без ADR и обоснования происхождения.
3. **Негерметичность тестов** — unit/integration-тесты выполняют `reset_workspace` на живом
   репозитории, что создаёт риски гонок и конфликтов с параллельным `make scenario-run`.

Общая оценка зрелости: **4 / 5** (см. раздел 8).

## 2. Проверенное аудитором состояние (evidence)

| Команда | Exit | Результат |
|---|---|---|
| `git status --porcelain` | 0 | рабочее дерево чистое, HEAD = `ec31fa6 "update"` (2026-09-13 14:34) |
| `uv run ruff check .` | 0 | All checks passed |
| `uv run ruff format --check .` | 0 | 122 files already formatted |
| `uv run pytest -q` | 0 | **371 passed** за 17.6 c (в evidence STEP-0014 — 350; прирост = тесты STEP-0015) |
| `docker compose config --quiet` | 0 | конфигурация валидна |
| `docker compose ps` | 0 | clickhouse, postgres, api-server, scheduler, dag-processor — Up 4 hours (healthy) |
| `ls -la .env` | 0 | `-rw-rw-r--` — права **0664** (см. F-03) |
| `df -h /` | 0 | 9.9 GiB свободно — риск из progress.md (STEP-0003, 2.3 GiB) снят |

Проверка «документация = факт» выполнена выборочно вручную: число тестов, отсутствие
OTel/Jaeger в compose, статусы PRB-0007/PRB-0026, отсутствие ADR-0025 в индексе,
наличие кода trigger-слоя STEP-0015, содержимое reliability sample STEP-0009.

## 3. Прогресс против roadmap

| Фаза | Содержание | Статус | Комментарий аудитора |
|---|---|---|---|
| 0 | Governance, bootstrap | ✅ завершена | STEP-0001; evidence живёт в step-файле, а не в `evidence/` (F-16) |
| A | Golden Data Platform | ✅ завершена | STEP-0002…0004; детерминированный seed, 68 dbt-тестов, Airflow 3.3.1 + Cosmos 1.15.0, 11-тасковый граф, failure-probe |
| B | Scenario Harness | ✅ завершена | STEP-0005; транзакционный reset, fingerprint-воспроизводимость, изолированный grader |
| C | Contracts + state machine | ✅ завершена | STEP-0006; frozen Pydantic-контракты, чистый reducer, hash-chain событий |
| D | Local Agent Runtime | ✅ завершена | STEP-0007; GateLLM-провайдер поверх MAF, cost-first выбор модели |
| E | Tool/policy layer | ✅ завершена | STEP-0008; официальные MCP в изолированных контейнерах, AST-гейт SQL |
| F | Milestone 1: autonomous DE | ✅ завершена | STEP-0009; 10-run sample: **8/10 public, 7/10 hidden**, 0 policy violations, медиана 1.94 ₽/run |
| G | Quality loop (QA + Reviewer) | ✅ завершена | STEP-0010/0011; QA mutation detection 5/5, Reviewer false approval 0/4 |
| H | Requirements pipeline | ✅ завершена | STEP-0012/0013; Analyst → typed handoff → PM с детерминированным `blocked/needs_user` |
| I | Airflow integration | 🔶 ~80% | STEP-0014 (read-only MCP) завершён; STEP-0015 (controlled trigger): код закоммичен, live-гейты и журнальный цикл не закрыты |
| J | Reliability/observability/isolation | ⬜ не начата | checkpoints/resume, OTel, runner isolation — впереди |
| K | Evaluation benchmark | ⬜ не начата | нужно ≥10 сценариев (сейчас 1 — net-revenue) |
| L | Курс | ⬜ не начата | материал (ADR/PRB/EXP) уже накапливается и пригоден |

Расхождений «заявлено завершённым, но не подтверждено evidence» для фаз 0–H не найдено.
Единственное расхождение статуса — STEP-0015 (см. F-01).

## 4. Сильные стороны (зафиксировать как стандарт)

1. **Сквозная прослеживаемость:** step → ADR → PRB → experiment → evidence → progress.
   15 шагов, 25 ADR без дыр в нумерации, 41 problem record, 4 эксперимента. Evidence-файлы
   содержат команды и exit codes — аудит возможен постфактум, что и доказано этим ревью.
2. **Инварианты в коде, не в промптах:** таблица переходов и гейты — чистый reducer
   (`orchestrator/transitions.py`); LLM возвращает только draft'ы без identity/evidence;
   QA/Reviewer сверяют хэши аргументов инструментов с кодовым планом; направление слоёв
   `contracts ← policies ← orchestrator ← runtime` закреплено AST-тестом.
3. **Честные метрики Milestone 1/2:** 7/10 end-to-end — не «всё зелёное», а измеренная
   реальность с разбором отказов (PRB-0033 и др.); mutation-корпуса для QA (5/5) и
   Reviewer (0/4 false approval) — редкая практика измерения false pass/approval.
4. **Изоляция и минимизация blast radius:** internal-only сети для grader/mcp,
   `cap_drop: ALL`, `no-new-privileges`, non-root, read-only FS, tmpfs, loopback-порты,
   SELECT-only ClickHouse-identity для MCP, dbt-записи ограничены disposable-схемой
   `analytics.*`.
5. **Гигиена зависимостей:** `uv.lock` с hashes, digest-pin почти всех образов,
   hash-locked requirements в dbt-mcp, запрет floating versions — и это enforced
   policy-тестами.
6. **Тестовая дисциплина:** 371 тест, ноль `skip`/`xfail`/ослабленных assert,
   поведенческие фейки вместо MagicMock в логике, выделенные policy- и adversarial-слои
   с конкретными deny-кодами.

## 5. Находки

### 5.1 Governance и дисциплина журналирования

- **F-01 (high). STEP-0015: код без журнального следа.** Коммит `ec31fa6 "update"` вносит
  ~1625 строк: `runtime/tools/airflow_trigger.py` (256), `runtime/tools/airflow_approval.py`
  (223), `contracts/airflow.py`, `policies/profiles/airflow_trigger_v1.json`, MCP-сервер,
  smoke, 3 тестовых файла, ADR-0025, PRB-0040. При этом: в `progress.md` нет записей после
  STEP-0014; в `plan/evidence/` нет файла STEP-0015; step-файл не содержит work log /
  фактических результатов, хотя `Claude.md:11-20` объявляет их обязательными; сообщение
  коммита «update» нарушает собственный commit-гайдлайн из AGENTS.md. Формально шаг
  `in progress` — но implementation checklist выполнен на ~6 из 8 пунктов. Это ровно тот
  тип рассинхрона, который обесценивает `plan/` как «источник истины».
- **F-04 (medium). `PROBLEM-0011` вне нейминг-схемы.** Создан 2026-09-13 при уже
  существующих PRB-0001…0037: префикс `PROBLEM-` вместо `PRB-` и номер `0011`, занятый
  `PRB-0011-cosmos-runtime-dependencies.md`. Два дефекта делят один идентификатор; запись
  навсегда выпала из последовательности и из индекса.
- **F-05 (medium). PRB-0007 завис в `Status: validating`**, хотя его regression check
  (fresh transcript STEP-0002) выполнен и `progress.md:30` заявляет «закрыты
  PRB-0004…PRB-0008». Ложный «открытый» дефект в каталоге.
- **F-06 (medium). PRB-0026 — единственный `open` без диспозиции.** Требуемый им phased
  execution реализован (ADR-0019), но запись не закрыта и не переквалифицирована как
  accepted upstream limitation. Невозможно отличить живой риск от забытого статуса.
- **F-07 (medium). Устарели индексы каталогов:** `plan/decisions/README.md` не содержит
  ADR-0025; `plan/problems/README.md` покрывает менее половины записей (нет
  PRB-0031…0036, 0038…0040, PROBLEM-0011). Кроме того, ADR-0010/0011 объявляют
  `Supersedes`, но ADR-0009/0010 не получили обратное `Superseded by` — читатель видит
  три «accepted» решения в одной области.
- **F-13 (low). AGENTS.md отстал от репозитория:** не упомянуты `mcp/`, `grader/`
  (security-critical!), `scenarios/`, `plan/experiments/`, `plan/progress.md`; нет
  gate-команд фаз G–I (`mcp-smoke`, `airflow-mcp-smoke`, `scenario-repro-test`,
  `scenario-grade-baseline-test`, `airflow-trigger-*`). Все перечисленные команды валидны —
  устарел scope, а не факты. Нет cross-link на `Claude.md`, хотя оба файла объявляют
  совместный приоритет и не задают правило разрешения расхождений.
- **F-15 (low). Дрейф словарей и шаблонов:** статусы шагов `done`/`complete`/`completed`,
  статусы проблем `resolved`/`closed`/`validating`/`open` с разным синтаксисом;
  STEP-0011/0012/0013 без work log; ADR-0011, 0022…0025 без секции Alternatives.
  Корневая причина всех находок 5.1 — консистентность `plan/` ничем не enforced:
  нет линтера/CI-проверки статусов, индексов, нейминга и обязательных секций.
- **F-16 (low).** У STEP-0001 нет evidence-файла, тогда как `plan/README.md:26` утверждает
  «persistent gate summaries сохранены в `evidence/`» для STEP-0001–0014.

### 5.2 Control-plane код

- **F-02 (high). Зависимость `httpx2==2.12.0`** (`pyproject.toml:10`,
  `runtime/model_provider.py:14` — `import httpx2 as httpx`). Малоизвестный форк с именем,
  почти совпадающим с `httpx` (классический вектор typosquatting), используется в коде,
  формирующем `Authorization: Bearer $API_TOKEN`. Hash-pin в `uv.lock` защищает от тихой
  подмены артефакта, но не решает вопрос доверия к происхождению пакета. Нужен ADR с
  обоснованием либо переход на `httpx` (PRB-0013 упоминает причину появления httpx2 —
  совместимость с openai3 — но ADR по supply-chain решению нет).
- **F-09 (medium). Системное дублирование в `runtime/`:** `_identifier` ×6,
  `_domain_evidence` ×4, usage-агрегаторы ×4, атомарная запись с mode 0600 ×5,
  live-boilerplate `run_live`+CLI ×5. Часть дублей — security-релевантные хелперы
  (права файлов, evidence-формирование); рассинхрон копий размоет единые инварианты.
- **F-10 (medium). `model_copy(update=...)` без валидации** подменяет тип поля
  `allowed_tools` (tuple → frozenset) в `reviewer_live.py:69-74`, `qa_live.py:101`,
  `data_engineer_live.py:234` и др. Контракт фактически нарушен; работает случайно.
- **F-19 (low).** `assert` для control flow в `runtime/qa.py:294-296` — отбрасывается под
  `python -O`; выбор repair-файла эвристикой по ключевым словам
  (`data_engineer_workflow.py:310-325`); детект ошибок dbt по текстовым префиксам
  (`mcp_gateway.py:58,193`); вводящий в заблуждение reason при отсутствующем адаптере
  (`mcp_gateway.py:150-166`); `cast` вокруг model_id из CLI (`model_provider.py:556`).
- **F-22 (low). Полумёртвый код:** нефазовые `build_data_engineer_workflow` /
  `AutonomousDataEngineerExecutor` живут ради тестов; `connect_data_engineer_mcp_tools` —
  ради smoke. Пометить или удалить, чтобы не размывать supported surface.

### 5.3 Data Platform

- **F-12 (medium). ClickHouse — единственный внешний образ без digest-pin**
  (`docker-compose.yml:41`, только tag `25.8.33.6`) — нарушение правила «Pin dependencies
  and Docker images» из AGENTS.md на фоне образцового pin всего остального.
- **F-11 (medium). Hidden grader: две оговорки.** (а) «Скрытость» оракула — на уровне
  policy/манифеста, файл `grader/hidden/grade.py` физически читаем в репозитории; это
  осознанный дизайн (ADR-0013), но границу доверия стоит явно признать в рисках.
  (б) Grader ходит в ClickHouse под полномощной identity `agentic`
  (`docker-compose.yml:173-175`), защита — только параметром `readonly=1`; выделенный
  grader-пользователь сузил бы blast radius.
- **F-20 (low).** Пароль передаётся argv-аргументом в `ensure_mcp_viewer.py:117-118`
  (docstring утверждает обратное); креды в healthcheck ClickHouse видны через
  `docker inspect`; Airflow-контейнеры получают полную пару ClickHouse credentials при
  read-only характере `seed_readiness`; JWT в `airflow_api.py` кэшируется без обработки
  401/refresh; мёртвый exit-код `INTEGRITY_FAILURE` в `grade.py:15`.
- Зафиксировано как **соответствие стандарту** (не дефекты): детерминированный seed без
  `rand()`, точные счётчики edge cases, отсутствие `SELECT *`, явные grains, naming
  `stg_/int_/fct_/dim_` 8/8, Cosmos `AFTER_ALL` gate, failure-probe DAG.

### 5.4 Тесты

- **F-08 (medium). Тесты мутируют живой репозиторий.** `test_data_engineer.py`,
  `test_qa_mutations.py`, `test_analyst_workflow.py`, `test_data_engineer_workflow.py`,
  `test_qa_workflow.py`, `test_reviewer_workflow.py` вызывают
  `load_manifest(ROOT, "net-revenue")` + `reset_workspace(ROOT, ...)` на реальном checkout.
  Последствия: негерметичность, гонки при параллельном запуске, конфликт с
  `make scenario-run`, падения при переименовании сценария. Дополнительно
  `_FailingValidator` в `test_data_engineer_workflow.py:240-243` накапливает evidence-мусор
  в `.scenario-state/` без очистки.
- **F-17 (low).** Двойной импорт тестовых модулей: `tests/workflow/__init__.py` есть,
  у остальных каталогов нет; кросс-импорты `from tests.integration.test_... import ...`
  создают два экземпляра модуля — сейчас спасает duck-typing, сломается на первом
  `isinstance`.
- **F-18 (low).** Нет coverage-измерения (пробелы: `analyst_live`, `qa_live`,
  `quality_loop_live`, `requirements_live` не покрыты вовсе); `--strict-markers` при нуле
  зарегистрированных маркеров — будущим live-тестам некуда попасть; unit-тест
  `test_airflow_commands.py` запускает реальный `make` с timeout=5 — не unit и потенциально
  флаки.
- **F-21 (low).** Хрупкие строковые policy-assertions (точный матч рецептов Makefile с `\t`,
  хешей образов, разбиение compose по имени следующего сервиса) — ломаются при безобидном
  переформатировании.
- Отмечено как сильная сторона: полный перебор запрещённых рёбер state machine,
  replay/truncation detection hash-chain, adversarial-кейсы на traversal/symlink/
  prompt-injection/self-approval, мутационные корпуса QA/Reviewer.

### 5.5 Безопасность

- **F-03 (medium). `.env` с правами 0664** (проверено аудитором лично): токен GateLLM
  читается группой и прочими пользователями машины. Исправление — `chmod 600 .env`;
  стоит добавить проверку в `make bootstrap` или policy-тест.
- Подтверждено сильное: `API_TOKEN` — `SecretStr(repr=False, exclude=True)`, отсутствует в
  Compose-конфиге и контейнерах; stdio MCP получают изолированный env; subprocess только
  argv-списками без `shell=True`; многослойная защита от path traversal с double-stat
  TOCTOU; evidence/approvals/runs — 0600/0700; `eval`/`exec`/`pickle` не найдены.
- **F-14 (low, документация).** `Claude.md` и раздел 2 `development-plan.md` упоминают
  «observability»/OTel+Jaeger в составе Data Platform — в compose их нет (это Phase J);
  формулировки стоит пометить как целевое состояние, чтобы не выдавать план за факт
  (нарушение принципа из самого `plan/README.md:3`).

## 6. Сводная таблица находок

| ID | Severity | Область | Суть |
|---|---|---|---|
| F-01 | **high** | governance | STEP-0015: ~1600 строк кода без progress/evidence/work log; коммит «update» |
| F-02 | **high** | код/supply-chain | `httpx2` в пути с `API_TOKEN`, без ADR о доверии |
| F-03 | medium | security | `.env` mode 0664 |
| F-04 | medium | governance | PROBLEM-0011: префикс + коллизия номера с PRB-0011 |
| F-05 | medium | governance | PRB-0007 завис в `validating` при выполненном regression check |
| F-06 | medium | governance | PRB-0026 `open` без диспозиции при реализованном workaround |
| F-07 | medium | governance | устарели индексы decisions/ и problems/ README; нет Superseded by у ADR-0009/0010 |
| F-08 | medium | тесты | unit/integration тесты мутируют живой репозиторий |
| F-09 | medium | код | дублирование security-релевантных хелперов ×4–6 в runtime |
| F-10 | medium | код | `model_copy(update=)` без валидации ломает тип контракта |
| F-11 | medium | platform | grader: hiddenness только policy-уровня + admin-identity в ClickHouse |
| F-12 | medium | platform | ClickHouse без digest-pin |
| F-13 | low | governance | AGENTS.md устарел по scope (mcp/, grader/, scenarios/, команды G–I) |
| F-14 | low | документация | «observability» в рулбуках опережает факт (нет OTel/Jaeger) |
| F-15 | low | governance | дрейф статусных словарей и шаблонов step/ADR/PRB |
| F-16 | low | governance | нет evidence-файла STEP-0001 |
| F-17 | low | тесты | двойной импорт тестовых модулей |
| F-18 | low | тесты | нет coverage/маркеров; make-вызов из unit-теста |
| F-19 | low | код | assert в control flow, эвристики repair, текстовые префиксы dbt |
| F-20 | low | platform | пароль в argv, креды в healthcheck, JWT без refresh, широкие креды у Airflow |
| F-21 | low | тесты | хрупкие строковые policy-assertions |
| F-22 | low | код | полумёртвые executor'ы и helper'ы |

## 7. Рекомендации (по приоритету)

**Немедленно (до следующего коммита):**

1. `chmod 600 .env` (F-03); добавить проверку прав в `make bootstrap` или policy-тест.
2. Закрыть журнальный цикл STEP-0015: work log в step-файле, запись в `progress.md`,
   evidence после прогона live-гейтов; впредь не коммитить реализацию раньше записей (F-01).

**Текущий шаг / неделя:**

3. ADR по `httpx2` (происхождение, дифф с httpx, риски) или миграция на `httpx` (F-02).
4. Диспозиция зависших PRB: PRB-0007 → resolved, PRB-0026 → closed как accepted upstream
   limitation; PROBLEM-0011 → переименовать в PRB-0041 с redirect-строкой (F-04…F-06).
5. Обновить индексы `plan/decisions/README.md` (ADR-0025, Superseded by) и
   `plan/problems/README.md`; обновить AGENTS.md по scope и командам (F-07, F-13).
6. Digest-pin ClickHouse (F-12).

**Краткосрочно (фаза I–J):**

7. Линтер `plan/`: CI-проверка статусов против progress.md, полноты индексов, нейминга
   PRB/ADR, обязательных секций шаблонов — устраняет корневую причину F-01/F-04…F-07/F-15/F-16.
8. Герметичные тесты: workspace-фикстуры на `tmp_path` с копией манифеста вместо живого
   репозитория; очистка evidence-мусора; coverage + маркер `live` (F-08, F-17, F-18).
9. Рефакторинг дублей runtime в общий модуль; валидирующий конструктор вместо
   `model_copy(update=)` (F-09, F-10).
10. Выделенный read-only ClickHouse-пользователь для grader; узкая identity для
    `seed_readiness` в Airflow (F-11, F-20).

**Среднесрочно (по roadmap):**

11. Phase J: checkpoints/resume, OTel traces, isolation — после закрытия Phase I.
12. Phase K: расширение сценариев с 1 до ≥10 — сейчас весь eval-бенчмарк держится на
    net-revenue, статистическая устойчивость выводов ограничена.
13. Устранить assert из control flow, эвристику repair-цели и текстовый детект ошибок dbt
    при ближайшем касании соответствующих модулей (F-19).

## 8. Оценки зрелости

| Область | Оценка | Ключевое обоснование |
|---|---|---|
| Governance / журналирование | 4 / 5 | образцовая прослеживаемость фаз 0–F; дрейф G–I и отсутствие enforcement |
| Control-plane код | 4 / 5 | инварианты в коде, чистый reducer, hash-chain; дубли, httpx2, мелкие хрупкости |
| Data Platform | 4 / 5 | детерминизм, 68 тестов, изоляция; ClickHouse pin, grader identity |
| Тесты | 4 / 5 | 371 тест, ноль ослабленных assert, adversarial/policy слои; негерметичность, нет coverage |
| Безопасность | 4 / 5 | deny-by-default реализован, секреты изолированы; `.env` 0664, httpx2, dev-defaults |
| **Итого** | **4 / 5** | зрелый инженерный проект с управляемым техническим долгом |

## 9. Вывод

Проект развивается в правильной архитектурной траектории и с редкой для агентных систем
честностью: метрики измеряются, отказы фиксируются, gates не ослабляются ради «зелёного»
результата (PRB-0020, сохранение 7/10 как факта — тому доказательства). Код и платформа
соответствуют заявленным в плане инвариантам — это главный итог аудита.

Основной риск — не технический, а процессный: с ростом скорости разработки (фазы G–I)
ручная дисциплина журналирования начала проседать, и `plan/` постепенно перестаёт быть
безусловным «источником истины». Поскольку конечный продукт проекта — курс, построенный
на достоверности именно этих записей, инвестиция в автоматический линтер `plan/`
(рекомендация 7) окупится первой. Второй приоритет — supply-chain гигиена (`httpx2`),
третий — герметичность тестов.

Блокеров для завершения STEP-0015 и перехода к Phase J нет.
