# STEP-0028 — Cyberpunk course site prototype

Status: completed

Owner: Codex

Updated: 2026-09-15

## Goal и scope

Реализовать ADR-0038 в прототипе: landing, manifest-driven SVG roadmap, pages планов тем,
course navigation слева и AST TOC справа. Сохранить старый diagram prototype отдельно.
Разрешены course builder/templates/static assets, policy tests, planning/docs. Runtime/platform,
curriculum/lecture texts/review gates/secrets не менять. Локальный preview оставить доступным.

## Acceptance

Landing в dark Cyberpunk стиле, terminal hero, neon/chamfers/bounded motion; roadmap с
27 реальными ссылками и HTML fallback. 26 core + optional 24, порядок из manifest.
Страницы описаний тем честно outline, не published lectures. Desktop left/right navigation,
mobile native disclosures, active status и previous/next. Сохранены SVG/CSP/no-JS/print.
Regression tests, две одинаковые сборки, browser + visual проверки и make check PASS.

## Checklist

- [x] Изучить specification и текущий builder; определить scope до реализации.
- [x] Добавить templates/tokens, landing, generated roadmap и navigation.
- [x] Интегрировать AST outlines/TOC, сохранить diagram prototype и SVG boundaries.
- [x] Добавить regression checks, build/repro и browser/visual/no-JS/mobile проверки.
- [x] Выполнить gates, записать evidence/status, завершить шаг.

## Risks и verification

Не публиковать unreviewed тексты. Roadmap — trusted generated SVG с ограниченными local URLs,
не generic разрешение linked Mermaid. Локальный Noto Sans сохраняет кириллицу; display mono
пока через системный monospace, новые fonts не устанавливаются. Reduced motion/CSP обязательны.
`make course-build`, labelled second build, targeted pytest, Playwright CLI, `make check`, diff check.

## Work log

- 2026-09-15: изучен read-only пример `/home/ivan/claude/ai-agent-memory/website_builder`:
  shared shell/sidebar/TOC/pager, Markdown heading IDs и local link validation.
  Перенесены архитектурные идеи, не исходный visual style, CDN Mermaid или Metrika.
- 2026-09-15: landing и 27 AST Markdown outline pages реализованы. Linked roadmap генерируется
  отдельно от Mermaid sanitizer; metadata escaping и fixed numeric local URLs.
  Browser responsive/outline/navigation checks PASS. PRB-0056/0057 исправлены и проверены.
- 2026-09-15: `make check` exit 0 (515 tests), targeted 64 PASS, actual two-build byte comparison
  PASS; expanded browser/diagram suites exit 0. Preview оставлен работающим.
  [Evidence](../evidence/STEP-0028-cyberpunk-course-site-prototype.md).
