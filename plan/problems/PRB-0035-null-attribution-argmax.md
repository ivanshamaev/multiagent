# PRB-0035 — QA found NULL attribution loss in canonical candidate

- Status: resolved
- Detected: 2026-09-12
- Scope: canonical Net Revenue model and independent QA oracle

## Reproduction

The full public validator passed, and the immutable QA semantic diff returned zero rows. Live QA
still rejected the canonical model after inspecting its SQL: ClickHouse `argMax` skips nullable
values, so a latest attribution event with a NULL channel could select an older non-NULL channel.
When all values were NULL, the aggregate could also produce an empty default that a later `ifNull`
would not normalize.

## Cause and fix

Both the candidate and initial oracle normalized the channel only after aggregation, so their empty
diff shared the same semantic blind spot. Normalize with `ifNull(acquisition_channel, 'unknown')`
inside `argMax`, and repeat the normalization at the per-order selection boundary. The public probe
uses the same business rule but remains independently authored and code-owned.

## Regression check

Both the canonical model and independent semantic oracle now normalize nullable channels with
`ifNull(..., 'unknown')` before `argMax`. The repeated canonical live QA run passed with an empty
semantic diff; dbt 78/78, public SQL and all five isolated hidden checks also passed. The first
failing live record remains evidence that QA—not the validator or hidden grader—identified the
defect.
