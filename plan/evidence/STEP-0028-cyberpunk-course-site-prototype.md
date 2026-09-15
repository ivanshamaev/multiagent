# STEP-0028 — Cyberpunk course site prototype

Date: 2026-09-15

Status: completed

## Persistent summary

Landing implements dark Cyberpunk tokens, neon hero, bounded RGB glitch, circuitry/scanlines,
terminal panel, curriculum cards and manifest-driven linked SVG roadmap. 27 topic pages render
existing Markdown outlines through the same AST pipeline; reader shell has left course navigation,
right H2/H3 TOC, responsive disclosures and canonical-order previous/next. All are explicitly
plans, not unwritten/published lectures. Old Mermaid fixture page remains at prototype.html.

Read-only reference `/home/ivan/claude/ai-agent-memory/website_builder` informed shared shell,
sidebar/TOC/pager, heading IDs and generated link validation. No external repo files modified;
no CDN Mermaid, Metrika, inline scripts or Poetry stack copied. Existing local pinned Noto Sans
used for Russian prose; terminal labels use host monospace. Dedicated reference display fonts
remain a refinement, not silently declared installed.

## Commands and checks

- `make course-build`: exit 0, 78 managed files, 31 HTML pages, four Mermaid diagrams;
  additionally linked course roadmap and decorative conceptual hero SVG.
- `uv run python -m course.build --output build/course-step28-verify`: exit 0, matching site SHA256
  `06b0562b17d1cf137b7ab57e7574fdb41001a8566a42976fa9b815065990d950`.
- Targeted build tests: `uv run pytest tests/policy/test_course_build.py -q`: exit 0,
  35 passed. Covers original sanitizer/output boundaries plus curriculum order, AST outline
  rendering, roadmap escaping/fixed local URLs, standalone links, duplicate IDs and broken anchors.
- `make check`: exit 0, Ruff/format PASS, 515 tests in 66.29s,
  plan/course governance and Compose config validation PASS; no services started by this gate.
- Read-only byte comparison and verify_links on both actual output directories: exit 0,
  79 files including ownership marker identical; all generated HTML/SVG links/anchors/IDs valid.
- `uv run pytest tests/policy/test_course_build.py tests/policy/test_course_governance.py -q`:
  exit 0, 64 passed in 34.70s.
- Playwright CLI site-browser-check: initial rerun passed landing/roadmap navigation, outline
  status, sidebar/TOC, 360/768/1280/1600px, mobile disclosures/reduced-motion/no-JS,
  no page/console errors or external requests. Final expanded coverage also passed:
  all four widths across landing, two topic pages and both service diagram pages;
  exact selected TOC link receives aria-current after navigation. CLI command exit 0.
- Old diagram interaction/browser suite still passes controls, Cyrillic, unique IDs, no inline
  content, full print viewBoxes/restored zoom, no-JS and CDP touch emulation.
  Mobile service-page overflow fixed; final rerun exit 0, no pageOverflow for either service page,
  zero page/console errors, failed requests or external requests.
- Calculated token contrast against #0a0a0f/#12121a: foreground 14.96/14.11,
  quiet 7.76/7.32, green 14.73/13.89, cyan 11.16/10.52. Assertion wrapper exit 0;
  these measurements are not a full accessibility audit.

Browser commands use local Node PATH and own CLI session course28, sandboxed Chrome 153:

```bash
PATH="$PWD/course/node_modules/node/bin:$PATH" PLAYWRIGHT_CLI_SESSION=course28 \
bash /home/ivan/.codex/skills/playwright/scripts/playwright_cli.sh \
run-code "$(< course/prototype/site-browser-check.js)"
```

Same command with `course/prototype/browser-check.js` verifies original diagrams.
Run CLI session from repository root; artifacts are in ignored output/playwright/step28/.
Skill playwright actually used for CLI snapshots, real link clicks, interactions and screenshots.

## Defects and remaining risks

PRB-0056: section/figure ID collision fixed; regression checks now fail build before output writes.
PRB-0057: long inline slash-separated tokens caused mobile overflow; inherited wrap-anywhere
with preformatted local scroll fixes it. Browser coverage expanded to service pages.
An initial integration error shadowed imported url helper with local URL parser variable;
rename imported helper topic_url. Existing reproducibility/boundary tests reproduced and passed.

No runtime/platform/LLM/Docker/secret writes. UI is an outline prototype, not full publisher;
review gates unchanged. No full screen-reader/hardware/cross-browser/PDF visual audit claimed.
Renderer font portability limitations from STEP-0026 remain. Existing loopback preview retained.

Visually inspected landing.png, reader-desktop.png, landing-mobile.png and roadmap.png:
neon dark hierarchy, readable Russian headings, distinct active course/TOC panels,
no roadmap label overlap in the inspected viewport; deep roadmap remains locally scrollable.
Artifacts were relocated from CLI session cwd into ignored output/playwright/step28;
persistent scripts now explicitly use that artifact prefix.
After final documentation edits: `make plan-check course-check`, `git diff --check` exit 0;
preview GET HTTP 200. Only own course28 browser session closed; preview server remains running.
