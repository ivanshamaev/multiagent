# STEP-0026 — Markdown → SVG → static HTML prototype

Status: completed

Owner: Codex

Updated: 2026-09-15

## Goal и scope

Создать локальный воспроизводимый prototype сборки Markdown в static HTML с build-time Mermaid
SVG, общим accessible viewer и реальными render/browser checks. Это contributor prototype,
не написание/публикация лекций и не student lab. STEP-0025 завершён.

Разрешены `course/**`, Makefile, .gitignore, pinned course npm dependencies/lockfile,
tests/policy и planning/status/evidence docs. Runtime, policies, Data Platform/oracle/corpora
не менять; pyproject/uv.lock разрешены для pinned tinycss2 parsing, без изменений runtime deps.
Не запускать Docker/LLM/production, не читать/публиковать secrets.

## Acceptance criteria

1. `make course-build` извлекает Mermaid через Markdown AST и рендерит sequence/flow/state SVG;
   включает полный bounded tool loop из technical requirements и несколько diagrams на странице.
2. Source .md не изменяются; allowlisted static output только под ignored build directory.
   Links/anchors/subpath работают; нет raw plan/runtime checkout в public output.
3. Renderer dependencies lock/pin, input/toolchain fingerprints, unique SVG IDs, SVG allowlist,
   отсутствие внешних refs/scripts/foreignObject. CSP не требует unsafe-inline scripts/styles.
4. Shared zoom/pan/reset/fullscreen, keyboard/Escape/focus, no-JS fallback, mobile/local scroll,
   light/dark/print. Не выдавать автоматические проверки за полноценный screen-reader audit.
5. Две сборки дают одинаковый static output; malformed diagram/unsafe SVG/path regression tests.
6. Реальный browser check и screenshots; `make course-check`, targeted tests, `make check`,
   `git diff --check`. Persist exact exit codes и remaining risks.

## План

- [x] Проверить renderer versions/engines; принять ADR до реализации.
- [x] Добавить pin/lock и локальную установку CLI/browser, без глобальных project packages.
- [x] Добавить diagram fixtures, AST builder, SVG validation/normalization и static template/assets.
- [x] Добавить CLI Make targets, local preview и fail-closed output boundaries.
- [x] Добавить regression tests и real render + two-build checks.
- [x] Проверить viewer через Playwright CLI, visually inspect screenshots, no-JS/subpath/CSP/print.
- [x] Выполнить full gates, обновить status/evidence и закрыть шаг при выполненной приёмке.

## Risks и permissions

Network/download failures — bounded retry и фиксировать gap. Browser sandbox не отключать
молча; renderer выполняет только repository-owned prototype input. Generated CSS/IDs Mermaid
нуждаются в normalization и central asset extraction для CSP. Font/browser variations ограничивают
переносимость byte reproducibility: фиксировать локально проверенные versions/fingerprints.
Static server bind только loopback. Public course deployment и полноценный a11y audit — non-goals.

## Verification

`make course-build`, two-build digest comparison, course policy tests, Playwright CLI browser checks,
`make check`, `git diff --check`. Record commands/results in STEP-0026 evidence.

## Work log

- 2026-09-15: scope и acceptance определены до реализации; skills technical-markdown-lectures/playwright.
- 2026-09-15: приёмка выполнена: четыре SVG, три HTML, две побайтово одинаковые сборки;
  browser checks PASS, targeted 53 tests PASS, `make check` exit 0 (504 tests).
  PRB-0053/0054/0055 закрыты с regression evidence. Не запускались Docker services или LLM.
  [Результаты и ограничения](../evidence/STEP-0026-static-course-prototype.md).
