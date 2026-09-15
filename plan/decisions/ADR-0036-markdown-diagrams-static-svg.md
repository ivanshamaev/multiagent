# ADR-0036 — Markdown diagrams with build-time SVG

Status: accepted

Date: 2026-09-15

## Context

Lecture sources must remain Markdown; publication will be static HTML. The user requests
interaction diagrams similar to the DataTalks tool-calling page, including readable large diagrams.
Inspection of that page's HTML found a handwritten inline SVG and custom zoom/pan/fullscreen
handlers, not Mermaid. Its graphic/code will not be copied.

## Decision

Use fenced `mermaid` blocks as canonical diagram sources inside lectures. Use sequence diagrams
for message exchanges, flowcharts for architecture/control flow, and state diagrams for lifecycle.
Render to SVG at build time with a pinned Mermaid CLI toolchain, then feed staged Markdown/assets
to a static generator. Mermaid CLI supports Markdown-to-Markdown transformation with SVG output:
[official CLI](https://github.com/mermaid-js/mermaid-cli).

Static SVG and adjacent textual explanation must work without JavaScript. A shared locally hosted
HTML component may enhance the SVG with accessible zoom/pan/reset/fullscreen. These controls are
not Markdown or built-in sequence-diagram features. Do not repeat raw HTML/JS across lectures.

Central build configuration sets Mermaid `securityLevel: strict`; SVG output still requires
validation, unique IDs when embedded, and testing under the site's CSP. Accessibility uses
`accTitle`/`accDescr`, meaningful captions and textual fallback. No runtime CDN/render dependency.

The static generator and concrete tool versions remain to be selected and tested during scaffold
implementation. This decision does not install dependencies or implement/publish the site.

## Alternatives and consequences

- Browser-time Mermaid is simpler to integrate but makes the diagram depend on client rendering;
  rejected as the primary publication path.
- Handwritten SVG gives precise visual control but is harder to maintain and review; allowed only
  as an explicitly reviewed exception where Mermaid cannot express the relationship.
- SVG preserves vector clarity, but needs browser/font/CSP and multiple-diagram integration tests.
  Pinned tools alone do not prove bit-for-bit reproducibility; normalize generated IDs/metadata and
  record input/config fingerprints before claiming reproducible builds.

Requirements and examples: `course/technical-requirements.md`. STEP-0025 remains in progress.
