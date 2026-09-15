# PRB-0057 — Long inline tokens overflow mobile page

Status: resolved

Date: 2026-09-15

At 360px technical-requirements page scrollWidth was 456px: unbroken slash-separated
metadata/transition tokens inside list items exceeded their 296px content width.
Tables and SVG already had local scroll; those were not the cause.
Apply inherited overflow-wrap:anywhere to main; preserve preformatted code's local scrolling.
Regression: site-browser-check includes technical requirements/prototype at all four widths;
diagram browser-check explicitly rejects pageOverflow. Final rerun recorded in STEP-0028 evidence.
