# PRB-0055 — Long state transition labels overlap

Status: resolved

Date: 2026-09-15

## Reproduction и cause

STEP-0026 desktop screenshot showed overlapping candidate/FAIL labels on the two return paths
into DE. SVG label containment checks passed: staying inside viewBox does not prove absence
of overlap. Mermaid state layout placed long budget conditions on adjacent transitions.

## Fix и regression

Shorten edge labels to FAIL/rework/exhausted; preserve budget conditions in the immediately
following textual equivalent. Rebuild the actual SVG and visually inspect state-diagram.png.
Keep visual review mandatory: automated geometry checks must not be described as exhaustive
semantic/layout validation. STEP-0026 evidence records final screenshot inspection.
