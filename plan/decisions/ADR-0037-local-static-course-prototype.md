# ADR-0037 — local AST builder and locked Mermaid renderer

Status: accepted

Date: 2026-09-15

## Context

STEP-0026 implements ADR-0036 with real SVG/HTML checks, while all lecture texts remain unwritten.
A local prototype must prove rendering, safe static output and shared controls without publication.

## Decision

Use existing pinned markdown-it-py AST with a small repository-owned Python static generator.
No new large site framework is needed for the bounded prototype; review publishing remains separate.
Use locally installed Node 22.22.0, Mermaid CLI 11.17.0, Mermaid 11.16.1 override and
Puppeteer 25.11.0 (Chrome for Testing 153.0.8010.36). Bootstrap the local Node package before
Puppeteer install scripts; global Node 18 remains untouched. Older initial pins were rejected after
engine warnings and npm audit findings. Record actual resolved browser/font fingerprints.

Only explicit prototype Markdown and technical requirements are rendered; no recursive checkout
copy. Output under build/course, loopback preview. External repository evidence links use a fixed
repository browser mapping, never file URLs. Documents remain source Markdown, SVG generated.

SVG is parsed/validated before embedding. Scripts/events/foreignObject/external references are
rejected. Normalize IDs and references; move generated styles to external local CSS, preserving
selector isolation. Browser controls use external local JS/CSS and strict CSP, no unsafe-inline.
Local Cyrillic/Latin fonts are packaged by a pinned npm font dependency and copied as assets.
CLI layout currently uses host Noto Sans metrics: record its byte fingerprint. Packaged web fonts
are pinned, but identical rendering across other hosts is not proven; two-build checks are local.

Prototype proves local render/interaction/byte reproducibility, not complete course publication,
arbitrary untrusted diagram execution, independent review or a full screen-reader audit.
Use regression tests and real Playwright CLI checks; retain screenshots/report evidence.
