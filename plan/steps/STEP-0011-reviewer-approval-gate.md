# STEP-0011 — Independent Reviewer approval gate

Status: complete
Owner: primary agent
Started: 2026-09-12
Completed: 2026-09-13

## Goal

Завершить Phase G независимым read-only Reviewer: после `QA_PASSED` он сопоставляет frozen
acceptance criteria с проверенными candidate artifacts и QA report, оценивает maintainability,
security и operational risk, а reducer открывает `DONE`, bounded `REWORK` либо `BLOCKED`.
После любого изменения обязательны полный validator, новый QA и новый Reviewer.

## Scope and non-goals

В scope входят Reviewer instructions/profile, typed draft boundary, code-owned `ReviewReport`,
интеграция с DE/QA loop, review-specific mutation corpus, false-approval metrics и один opt-in live
GateLLM evaluation. Reviewer не получает write, shell, SQL execution, grader, secrets, production,
approval bypass или право рецензировать собственную implementation/QA. Analyst/PM, Airflow tools
и course material остаются следующими фазами.

## Acceptance criteria

- [x] ADR фиксирует ownership и различие QA correctness от Reviewer acceptance/risk approval.
- [x] Deny-by-default profile разрешает только bounded reads нужных dbt artifacts; write, execute,
  grader, protected paths, wrong role и production закрыты policy/adversarial tests.
- [x] Reviewer запускается только из `QA_PASSED`, получает frozen spec и принятый QA report; model
  не управляет IDs, evidence links, authorship, budgets и transitions.
- [x] `APPROVE` требует assessment каждого immutable criterion со статусом PASS, успешное evidence
  и отсутствие HIGH/CRITICAL findings; неполный/невалидный output закрывается без approval.
- [x] Reducer доказывает `QA_PASSED → REVIEW → DONE` и bounded
  `REVIEW REQUEST_CHANGES → DE → validator → QA → REVIEW` без обхода повторных gates.
- [x] Review mutation corpus измеряет false approval минимум для hard-coded relation,
  wildcard/dead code, nondeterministic attribution и misleading contract intent.
- [x] Offline tests закрывают self-review, QA/reviewer identity collision, write attempts, missing
  criteria, invalid output, evidence mismatch и exhausted rework budget.
- [x] Live canonical approval и mutation sample сохраняют model/config/usage/cost/latency; обычные
  tests не расходуют токены.
- [x] `make check`, MCP/policy, reproducibility, Airflow/Cosmos, dbt, public SQL и hidden grader
  остаются green; команды, exit codes и residual risks записаны в evidence.

## Implementation sequence

1. Принять ADR и добавить `reviewer_v1` с минимальным file-read scope.
2. Реализовать drafts, verified request builder и code-owned ReviewReport assembler.
3. Реализовать две fresh review phases с точными file reads и cumulative bounded evidence.
4. Связать Reviewer с существующим phased DE/QA loop и обязательным повтором всех gates.
5. Добавить independent mutation fixtures и offline vertical slices approve/change/rework/invalid.
6. Провести cost-gated live canonical/mutation evaluation на самой дешёвой прошедшей capability
   модели; сохранить private run records без raw prompts/responses.
7. Выполнить полный regression, закрыть evidence/progress и назначить следующий шаг.

## Risks and verification

Риски: Reviewer дублирует QA, approve по prose без coverage, вкусовые LOW findings блокируют DONE,
mutation corpus подгоняется под prompt, hidden oracle попадает в feedback, а review repair обходит
QA. Проверки должны разделять correctness и approval, требовать exact criterion set и доказывать
полный повтор `validator → QA → Reviewer`. Grader и существующие assertions не изменяются.

Planned commands: targeted `pytest`; reviewer mutation eval; one bounded live sample; `make check`;
`make mcp-smoke`; `make scenario-repro-test`; `make platform-test`; canonical public/hidden grade;
secret scan; `git diff --check`.
