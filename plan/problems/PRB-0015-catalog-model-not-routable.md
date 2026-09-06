# PRB-0015 — Catalog cheapest model is not routable

Status: closed

Date: 2026-09-06

Follow-up: PRB-0016 supersedes the text-only capability check with a strict schema probe.

## Reproduction and evidence

The first controlled `make llm-smoke` failed closed with a sanitized
`ChatClientException → NotFoundError → HTTPStatusError`, HTTP 404. A direct one-token request without
`response_format` also returned 404 for catalog-cheapest `inclusionai/ling-2.6-flash`, proving the
failure was neither MAF nor structured-output handling. No usage was reported for failed requests.

A cost-ordered probe stopped at `mistralai/mistral-nemo`, which returned HTTP 200 with 6 input and
1 output token. At the 2026-09-06 catalog price (5.7/9 ₽ per million), it is the cheapest observed
routable CHAT model.

## Root cause

Catalog presence and price do not prove live routing availability. Selecting solely from
`GET /models` treated metadata as a capability guarantee.

## Accepted fix

The opt-in live selector probes cost-ordered CHAT candidates with `max_tokens=1` and stops at the
first valid completion. HTTP 400/404 marks only that candidate unavailable. Auth, balance,
rate-limit, server and transport failures stop selection instead of silently escalating spend.
Offline tests use mock transport; normal imports and `make check` still make no model calls.

## Regression check

Unit tests prove 404 skips exactly one candidate, success stops the loop, and 401/402/429/500 do not
fall through to a more expensive model. Live evidence records every probed model, status and usage
without response text.
