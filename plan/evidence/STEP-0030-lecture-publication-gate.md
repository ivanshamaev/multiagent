# STEP-0030 — Publication gate evidence

Date: 2026-09-15

## Реализовано

ADR-0039: content review и publication receipt разделены. `course.publication`
проверяет identity/UTC/freshness/12 actual pass flags, renderer и artifact hashes.
Publication digest связывает content review с builder/site/gate/preview/CSS/JS,
renderer lock и uv.lock. Обычный `course.build` публикует только reviewed;
candidate requires technical review и отдельную labelled directory.
Before-write gates проверяют actual renderer fingerprint и rendered body+TOC hash.

Reader сохраняет `topic-NNNN.html`, roadmap/sidebar/pager; SVG CSS загружается
для конкретной темы. Outline links и lecture links имеют stable URLs, code/evidence
показываются через reference metadata, checkout не копируется. Lecture SVG min-width
выбирается по валидированной геометрии, print отменяет это ограничение.

## Actual verification

- Первые targeted course tests: 76 PASS; после rendered-hash/fingerprint и geometry
  regression: 78 PASS / 43.11s, exit 0. Fixture proofs explicitly fake, не live evidence.
- `make check`: exit 0, 529 tests / 75.86s, Ruff/format/plan/course/Compose PASS.
  Первый запуск остановлен Ruff UP012 в ASCII fixture; исправлен bytes literal.
- Candidate 00 pinned CLI: exit 0, 80 files / 5 diagrams; actual Node 22.22.0,
  CLI 11.17.0 / Mermaid 11.16.1 / Chrome 153.0.8010.36.
- Browser candidate `/course/`: desktop 1440×1000, mobile 360×800, light/dark
  preference, no-JS disclosure navigation/text/SVG, TOC anchor, keyboard zoom/pan/reset,
  fullscreen/Escape/focus, print clipping, main landmark и diagram name/description
  в AX tree (1106 nodes), local HTTP links, header CSP, zero CSP/page errors/external
  requests: successful run exit 0. Все семь screenshots вычитаны автором.
- `make course-build` и repeat labelled build: exit 0 каждый, 80 files / 5 diagrams,
  identical site SHA-256 `dd9e3ff5c09b94d7db260f6dbb722d3304fd52333663f10b7f8b6a18c740ff2e`.
  `diff -qr build/course build/course-published-repeat`: exit 0.
- Final topic HTTP probe: 200. Основной preview 8099 не останавливался.
- Post-publication targeted course suite: 78 PASS / 44.40s, exit 0.
  Реальная navigation в published reader 8099 показала полный текст и новый TOC.

Content/renderer/publication fingerprints и screenshot hashes:
`course/reviews/LECTURE-0000.json`, `course/reviews/PUBLICATION-0000.json`.
Ignored browser artifacts: `output/playwright/step30/lecture-0/`; actual generated
manifest/diagram index: `build/course/diagram-index.json`.

## Ограничения и честность

Это local publication, не deployment. Полный текст опубликован только для 00;
26 остальных страниц — outlines. Редакторские проходы выполняет автор, не independent
reviewer. Проверена AX разметка, не actual Orca/NVDA/VoiceOver navigation (explicit false
в receipt). Fixed dark Cyberpunk palette проверена при обеих browser preferences;
print и diagram canvas светлые. PDF/paper/hardware touch/cross-browser audit не выполнен.

До успешного browser run исправлены одноразовые CLI harness ошибки: VM не предоставляет
dynamic import/require/URL; helper передаётся CLI целиком, hashes снимаются shell.
Anchor comparison декодирует русские URL. Эти ошибки не выдаются за product defects/PASS.
Следующий шаг — STEP-0031, теоретическая лекция 01 с отдельными review passes.
