# STEP-0040 — Phase L: лекция 09, MCP как интерфейс

Status: complete

Owner: Codex

Updated: 2026-09-17

## Goal и boundaries

После завершённой лекции 08 написать и опубликовать theory-only 09 о
MCP host/client/server, жизненном цикле соединения, согласовании capabilities
и семантическом дизайне tools. Показать на нашем MCP gateway разницу между
protocol envelope, выбором инструмента и code-owned политикой исполнения.

Не повторять SQL resource envelope (10), dbt semantics (11), Airflow operations
(18) и authentication/authorization threat model (19). Нет labs, runtime
changes, платных вызовов или Docker mutation.

## Acceptance и verification

- [x] Перечитать S11/S08, нормативные MCP architecture/lifecycle/tools docs,
  текущие gateway/stdio code и датированное STEP-0008 evidence.
- [x] Написать глубокую модель ролей, transport, capability negotiation,
  semantic tool surface, ошибку и границы гарантий; Mermaid, контрпример,
  вопросы и переход к 10.
- [x] Отдельные авторство, полная редакторская вычитка, technical/source/code
  verification, исправления/recheck и content receipt.
- [x] Candidate build и фактическая browser/visual проверка desktop/mobile,
  light/dark, no-JS, keyboard, print, AX, CSP, subpath и ссылок.
- [x] Publication receipt, reviewed manifest, профильные тесты, две побайтно
  одинаковые сборки, `make check`, evidence и preview 8099.

## Risks

Важны версии спецификации: не превращать пример stdio в утверждение обо
всех transports; negotiated protocol capabilities не означают permission.
Старое evidence STEP-0008 ограничено своим offline scope; не выдавать его
за качество LLM или fully-live six-role READY. OAuth детали — не владелец 09.

## Work log

2026-09-17: план создан после закрытия STEP-0039, до текста лекции 09.
2026-09-17: normative MCP `2026-07-28` отменяет обязательный session
`initialize` в пользу self-contained requests и per-request capabilities.
Pinned local `mcp==1.26.0` advertises `2025-11-25`; lecture must distinguish
these protocol eras, not imply an upgrade or feature parity.
2026-09-17: отдельные editorial/technical/recheck, браузерный visual gate и
content/publication receipts завершены. Схема исправлена после выявленного
наложения подписей стрелок; Mermaid parse error после замены схемы также
исправлен и повторно проверен. `make check`: 531 PASS; evidence в
`plan/evidence/STEP-0040-lecture-mcp-interface.md`.
