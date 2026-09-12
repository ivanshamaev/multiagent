# PRB-0022 — cost-first capability probe aborted on schema-invalid HTTP 200

Status: closed
Detected: 2026-09-12
Resolved: 2026-09-12

## Symptom and reproduction

The live cost-order probe stopped with `GateLLM capability response is invalid` when the first
candidate returned HTTP 200 but did not satisfy the strict `{ "ok": true }` schema. More expensive
candidates inside the configured bound were never evaluated.

## Root cause

The selector treated 400/404 as a candidate-level incompatibility but classified a schema-invalid
2xx response as a catalog-wide fatal error. Model capability and provider availability were mixed.

## Accepted fix

Record the candidate as unavailable, retain any valid usage counters, and continue in deterministic
price/model-ID order. Authentication, balance, rate-limit, server, and transport failures still
abort immediately because trying more models could increase cost or conceal an account outage.

## Regression check

A fake transport now returns invalid JSON with token usage for the cheapest model and valid strict
JSON for the next model. The selector must return the second model, preserve both probe outcomes,
and retain the eight tokens consumed by the rejected candidate.
