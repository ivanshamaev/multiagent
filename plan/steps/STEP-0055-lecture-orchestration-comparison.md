# STEP-0055 — Phase L: лекция 24, Workflow vs agent-orchestrator

Status: complete

Owner: Codex

Updated: 2026-09-19

## Цель и границы

Написать theory-only лекцию 24 о выборе между code-owned workflow,
model-directed agent-orchestrator, bounded hybrid и более простой
альтернативой без multi-agent orchestration. Сравнить подходы по единой
rubric: известность декомпозиции, coupling, риск side effects, ownership
остановки, audit/replay, cost/latency и evaluation. Разобрать не менее восьми
data-engineering scenarios без объявления универсального победителя.

Не повторять механику fixed graph из лекции 06, внутренний manager loop из
лекции 07, authority model из 19, evaluation design из 21 и cost equations
из 23. Итоговый сквозной разбор всей платформы оставить лекции 25. Текущий
runtime описывать только как `offline-proven` code-owned baseline; dynamic
manager и hybrid execution — `not-implemented` варианты.

Затрагиваемые пути: `course/lectures/`, module24/manifest/reviews/index,
`plan/steps/lections/`, `plan/evidence/`, course/plan status records.

## Порядок и критерии приёмки

- [x] Проверить Anthropic S01/S02, Cognition S03/S04, ADR-0035, текущий
  reducer/runtime graph и датированное STEP-0020 evidence.
- [x] Написать лекцию с decision rubric, сравнительной матрицей, bounded
  hybrid envelope, минимум восемью DE scenarios и контрпримером.
- [x] Явно различить topology, control ownership, transport и authority;
  не переносить vendor observations за пределы исходного setting.
- [x] Выполнить отдельные editorial, technical, diagram semantics и recheck
  passes; сохранить schema-v2 content receipt с source anchors/hashes.
- [x] Проверить Markdown/links и candidate/static build; сохранить text-only
  publication receipt без screenshots/browser/visual/AX review.
- [x] Обновить todo/manifest/index/evidence; две production-сборки побайтно
  совпадают, `make check`, governance и `git diff --check` проходят.

## Риски и ограничения

Сравнение легко превратить в ложную дихотомию: fixed workflow может иметь
ветвление, циклы и parallelism, а dynamic manager может работать внутри
жёстких policy gates. Независимость read subtasks не переносится на
конфликтующие writes. Статьи описывают разные задачи, модели и периоды;
их выводы служат источником критериев, но не benchmark нашей платформы.
Нельзя объявлять hypothetical manager реализованным или выводить quality
из offline workflow tests.

## Work log

2026-09-19: план создан до авторства; прочитаны обязательные skills, todo,
technical requirements, adjacent owners и первичные статьи S01–S04.
2026-09-19: лекция опубликована, same-author content/publication receipts
сохранены; две production-сборки совпали; `make check` — 532 passed.
Первый production gate отклонил ошибочно записанный full-page hash; receipt
исправлен на canonical `body + TOC` hash из candidate diagram index.
[Evidence](../evidence/STEP-0055-lecture-orchestration-comparison.md).
