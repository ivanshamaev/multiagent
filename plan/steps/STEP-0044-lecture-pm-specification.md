# STEP-0044 — Phase L: лекция 13, PM и формальная спецификация

Status: complete

Owner: Codex

Updated: 2026-09-18

## Цель и границы

После лекции 12 написать и опубликовать theory-only лекцию 13 о
business metric definition, требованиях к readiness и корректном
`NEEDS_USER` при material unknowns. Различить business intent, факты
Analyst, решение владельца смысла и проверяемые acceptance criteria.
Показать human-authored Net Revenue specification отдельно от
исторического live PM `BLOCKED`. Не повторять provenance 12,
implementation authority 14 или механику reducer 06. Нет labs,
runtime/Docker изменений и платных LLM вызовов.

## Порядок и критерии приёмки

- [x] Сверить первичные S15/S14 с `runtime/agent_runtime.py`,
  `runtime/specification.py`, контрактом, сценарием и STEP-0013.
- [x] Написать причинную модель metric definition/readiness, таблицу,
  Mermaid-схему READY/BLOCKED, контрпример, ограничения, вопросы и переход.
- [x] Провести отдельные полную редакторскую вычитку, фактчекинг, recheck;
  сохранить content receipt с hashes и source anchors.
- [x] Собрать candidate и проверить реальный HTML/SVG в браузере:
  desktop/mobile, light/dark, no-JS, keyboard, print, AX, CSP, links.
- [x] Сохранить publication receipt, обновить manifest/todo/index/evidence,
  проверить две идентичные сборки, `make check`, preview 8099.

## Риски

Формальная полнота полей READY не доказывает правильность бизнес-смысла.
`NEEDS_USER` — осмысленный исход gate, но текущий BLOCKED terminal в v1;
не заявлять незреализованный in-place clarification loop. Нельзя выдавать
human-authored ready spec за live агентное READY. AX не заменяет
реальную AT-навигацию; STEP-0013 — историческое наблюдение.

## Work log

2026-09-18: план создан после todo 13, кода PM, human-authored spec и
STEP-0013, до авторства лекции.

2026-09-18: текст, отдельные editorial/technical/recheck и actual Chrome
visual gate завершены. Content/publication receipts актуальны; две сборки
совпали побайтно; `make check` и preview 8099 проверены. Подробности —
[evidence](../evidence/STEP-0044-lecture-pm-specification.md).
