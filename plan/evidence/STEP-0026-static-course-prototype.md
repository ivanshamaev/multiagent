# STEP-0026 — static course prototype evidence

Date: 2026-09-15

Status: completed

## Persistent summary

Implemented repository-owned Markdown AST builder, locked Mermaid CLI renderer, fail-closed
SVG/CSS validation, allowlisted output and loopback preview. Four diagrams and three HTML pages;
lecture authoring/publication is not part of this prototype. Skills actually used:
technical-markdown-lectures (own diagram prose/semantics) and playwright (real UI checks).

## Verified commands

- `make course-renderer-install`: exit 0; npm ci with scripts disabled, rebuild local Node,
  then Puppeteer under local Node. Bootstrap reports Node 18 engine warnings before local Node
  is available; actual renderer runs under pinned Node 22.22.0. Global packages unchanged.
- `make course-build`: exit 0, 21 managed files, four diagrams.
- `uv run python -m course.build --output build/course-verify`: exit 0, same site SHA256
  `83adc2c67fd6c6bf85c4aaa13dac8ae16a94a186366e6a2f3e5123bb052eaed1`.
- Read-only byte comparison: exit 0, all 22 files including ownership marker identical.
- Actual `render_cli` malformed flowchart fixture: renderer exit 1, expected rejection;
  assertion wrapper exit 0. Existing output preservation also covered by regression test.
- `PATH="$PWD/course/node_modules/node/bin:$PATH" npm audit --prefix course --json`:
  exit 0, zero reported vulnerabilities on this date; not a security audit.
- Playwright CLI `run-code` with `course/prototype/browser-check.js`: exit 0.
  Four SVGs: unique IDs, title/desc/ARIA, Cyrillic font loaded, zero labels outside viewBox,
  zero inline script/style, zero page/console errors, failed or outbound requests.
  Zoom independence, wheel, pointer pan, keyboard/reset, fullscreen/fallback/Escape/focus,
  Tab cycle, 360px local scroll, light/dark/reduced motion, no-JS and print checks PASS.
  Print uses full original viewBoxes and restores zoom afterwards. Touch pan verified with
  Chromium CDP emulation, not hardware. `/course/` CSP and outside-root request rejection PASS.
- `uv run pytest tests/policy/test_course_build.py tests/policy/test_course_governance.py -q`:
  exit 0, 53 passed in 32.03s. Unsafe SVG/CSS, randomized IDs, invalid output paths,
  publication allowlist, secrets-free renderer environment and failed-render preservation covered.
- `make check`: exit 0; Ruff/format, 504 tests in 63.65s, plan/course governance and
  Compose config validation PASS. No services started.
- Read-only HTML parser check: exit 0, 31 local links/assets/anchors valid.
- `uv lock --check --offline` and `git diff --check`: exit 0.

## Toolchain

Node 22.22.0 local (global Node unchanged), CLI 11.17.0, Mermaid 11.16.1,
Puppeteer 25.11.0, Chrome for Testing 153.0.8010.36; Noto Sans npm package 5.2.8,
markdown-it-py 4.0.0, tinycss2 1.4.0. Generated `diagram-index.json` records source,
diagram, npm lock, builder, config, packaged font and system render-font hashes.
Browser CLI 0.1.20 used local Node; Chromium sandbox enabled, no no-sandbox flags.

Executed browser assertion command (working directory `output/playwright/step26/`,
existing CLI session opened against loopback preview with sandboxed Chromium):

```bash
PATH="/home/ivan/codex/multiagent/course/node_modules/node/bin:$PATH" \
PLAYWRIGHT_CLI_SESSION=course26 \
bash /home/ivan/.codex/skills/playwright/scripts/playwright_cli.sh \
run-code "$(< /home/ivan/codex/multiagent/course/prototype/browser-check.js)"
```

After final record edits, `make plan-check course-check` and `git diff --check`: exit 0.
Only the own `course26` browser session was closed; loopback preview stopped intentionally
with Ctrl-C (exit 130). Generated static files remain; restart preview with `make course-preview`.

## Findings and limits

PRB-0053: skip installed dependency docs in course checker, regression covered.
PRB-0054: explicit native fullscreen Escape and focus restoration, real rerun PASS.
PRB-0055: shorten overlapping state labels and preserve conditions in adjacent prose;
final visual inspection PASS after actual rebuild. Geometry containment alone does not detect overlap.
An optional standalone XML SVG screenshot timed out in Chromium; HTML-embedded SVG checks pass.
First full gate after status edits failed because this evidence target did not exist yet;
create the actual record and rerun, without weakening link checks.

Manually inspected desktop.png, dark.png, mobile.png, state-diagram.png and
bounded-loop-diagram.png. The last two use print CSS to expose complete embedded SVGs:
Russian labels readable, shortened state labels no longer overlap, tool-loop branches match
the adjacent text. Tall diagrams remain locally scrollable on screen; white SVG canvas is
intentional in both themes. HTML-embedded full-SVG screenshot command exit 0.

Screenshots/PDF: ignored `output/playwright/step26/`; persistent assertions reside in
`course/prototype/browser-check.js`. Full screen-reader/hardware/cross-browser audit and visual
PDF proofreading are not claimed. CLI layout uses fingerprinted host Noto Sans: reproducibility
proven locally, not across hosts. `prototype-verified` does not unlock lecture publication.

Primary references: [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli),
[Markdown AST](https://markdown-it-py.readthedocs.io/en/latest/using.html),
[tinycss2 API](https://doc.courtbouillon.org/tinycss2/stable/api_reference.html).
