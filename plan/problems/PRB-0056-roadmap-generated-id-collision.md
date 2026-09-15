# PRB-0056 — Roadmap section and figure shared an ID

Status: resolved

Date: 2026-09-15

Browser responsive/IDs check rejected landing: section and figure both used roadmap.
Use course-roadmap figure identity; keep section anchor roadmap. Build now verifies IDs,
local targets/anchors for every generated HTML/SVG before writing output.
Regression: test_generated_output_rejects_duplicate_ids_and_broken_links, actual browser rerun.
Standalone roadmap links also use ../topic URLs, distinct from embedded SVG page-relative URLs.
