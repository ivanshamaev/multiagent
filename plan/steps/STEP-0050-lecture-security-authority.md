# STEP-0050 — Phase L: лекция 19, Security и полномочия

Status: complete

Owner: Codex

Updated: 2026-09-19

## Цель и границы

Написать theory-only лекцию 19 об indirect prompt injection, различии
authentication/authorization/role/approval и запрете capability escalation
через content или delegation. Показать request-bound local MCP bearer и
deny-by-default gateway на нашем примере, не переобъясняя filesystem/network
isolation (08), MCP-протокол (09), Airflow operation (18), а также будущую
deployment tenancy (26). Planner-agent — теоретический контраст, не runtime.
Не менять runtime/Data Platform, не запускать paid models или Docker services.

Затрагиваемые пути: `course/lectures/`, module19/manifest/reviews/index,
`plan/steps/lections/`, `plan/evidence/`, course/plan status records.

## Порядок и критерии приёмки

- [x] Проверить S25/S10 на первичных страницах и актуальные normative MCP
  security claims по официальной спецификации; сверить runtime, policies,
  adversarial tests, STEP-0022 и границы их доказательства.
- [x] Написать глубокую лекцию: threat model, четыре разных authority понятия,
  цепочка content → proposal → code gate, fixed/planner comparison,
  counterexample и Mermaid-диаграмма с текстовым эквивалентом.
- [x] Выполнить отдельные editorial, technical, diagram semantics и recheck
  passes с разрешением findings; сохранить schema-v2 content receipt.
- [x] Проверить Markdown/links, candidate/static publication build; сохранить
  text-only publication receipt без screenshots/browser/visual/AX review.
- [x] Обновить todo/manifest/index/evidence; две production-сборки побайтно
  совпадают, `make check`, governance и `git diff --check` проходят.

## Риски и ограничения

Нельзя считать модельные инструкции или prompt-injection detection
полномочиями, а локальный HS256 bearer — OAuth. Authenticated request ещё
должен пройти authorization. Replay возможен до истечения срока токена для
того же exact request; отсутствие секретов у runner и network isolation
ограничивают, но не устраняют все угрозы. Пример не даёт production гарантий.

## Work log

2026-09-19: план создан до авторства лекции.
2026-09-19: лекция опубликована, same-author content/publication receipts
сохранены; две production-сборки совпали; `make check` — 532 passed.
[Evidence](../evidence/STEP-0050-lecture-security-authority.md).
