# PRB-0030 — Repeated capability probes amplified provider rate limits

- Status: resolved
- Detected: 2026-09-12
- Scope: repeated live Data Engineer runs

## Cause and impact

Every CLI process fetched the catalog, then repeated schema and tool probes for an unchanged model
before starting phased work. This added two paid requests per run and contributed to HTTP 429 at
the first phase finalization, making a 10-run sample measure probe pressure rather than agent quality.

## Fix

Persist only redacted capability metadata for one hour in a mode-0600 local cache. A hit requires
the same complete catalog capability fingerprint, requested model ID, two successful probes, and
an unexpired timezone-aware timestamp. Any model/category/context/pricing change or malformed,
stale, symlinked cache forces fresh probes. Cache use is explicit in each run record; cached probe
tokens are not attributed to the current execution.

## Regression check

Unit tests verify private permissions, TTL expiry, requested model binding, and invalidation after a
catalog pricing change. The first post-change live run recorded `capability_cache_hit=false` and
created the cache before a later provider 429.
