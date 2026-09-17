# STEP-0041 — Phase L: лекция 10, ограниченный аналитический SQL

Status: complete

Owner: Codex

Updated: 2026-09-17

## Цель и границы

После лекции 09 написать и опубликовать theory-only лекцию 10 о минимально
достаточном доступе к аналитическим данным: metadata/profile/aggregate,
составлении read capability и ресурсном envelope запроса. Объяснить,
почему синтаксис `SELECT`, `LIMIT` и MCP schema по отдельности не доказывают
безопасность или достаточность данных.

Не пересказывать dbt/grain/lineage (11), provenance фактов Analyst (12),
authentication/threat model (19) и query tuning. Нет labs, runtime changes,
платных LLM вызовов или Docker mutation.

## Порядок и критерии приёмки

- [x] Сверить S08/S16 и первичную ClickHouse документацию с текущими
  `tool_policy.py`, MCP gateway, SQL grants, тестами и датированным STEP-0008.
- [x] Написать причинную модель scope, AST gate, DB identity, row/time/output
  bounds и их несовпадающих гарантий; добавить диаграмму, контрпример,
  ограничения materialization, вопросы и переход к 11.
- [x] Провести отдельную полную редакторскую вычитку, technical verification
  по источникам/коду, исправления и recheck; сохранить content receipt.
- [x] Собрать candidate, проверить настоящий HTML/SVG в браузере desktop,
  mobile, light/dark, no-JS, keyboard, print, AX, CSP, subpath и links;
  сохранить publication receipt без заявления о независимом review.
- [x] Опубликовать reviewed manifest, выполнить профильные тесты, две
  побайтно равные сборки, `make check`, evidence и проверить preview 8099.

## Риски

SQL parser — не исполняющий движок и не доказательство отсутствия побочного
эффекта всех ClickHouse функций. Top-level `LIMIT` ограничивает строки
ответа, но не цену сканирования; gateway timeout может не отменить
удалённую работу. Гранты `mcp_reader` ограничивают операции и базы,
не устанавливают семантическую допустимость всех строк/столбцов внутри
`raw` и `analytics`. STEP-0008 — датированное evidence, не текущий
live benchmark и не fully-live six-role READY.

## Work log

2026-09-17: план составлен после чтения todo 10 и до авторства лекции.
2026-09-17: same-author editorial/source/code/recheck и browser visual gate
завершены. TD-схема начиналась вне мобильного viewport; после LR-правки
семь финальных screenshots осмотрены. Временный сбой Chrome совпал с
заполнением раздела (17 МБ свободно); восстановимый npm cache очищен,
после чего проверка прошла. `make check`: 531 PASS. Evidence:
`plan/evidence/STEP-0041-lecture-analytical-sql.md`.
