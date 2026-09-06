# PRB-0014 — GateLLM catalog contains virtual model IDs

Status: closed

Date: 2026-09-06

## Reproduction and evidence

The typed catalog adapter accepted its offline fixture but rejected the live `/v1/models` response
with a sanitized `ModelCatalogError`. A metadata-only `jq` probe found 13 IDs beginning with `~`,
such as provider `latest` aliases; every other checked field satisfied the documented types and
bounds. No token or full catalog was printed.

## Root cause

The initial model-ID pattern required an alphanumeric first character. GateLLM's concrete model IDs
meet that assumption, but its virtual routing aliases use `~` as the leading marker.

## Accepted fix

Allow a single leading `~` in `ModelIdentifier` while retaining the bounded allowlist for all other
characters. This identifier is never interpreted as a filesystem path or shell fragment. Cost-first
selection still uses exact catalog fields and a deterministic ID tie-breaker.

## Regression check

The offline catalog fixture contains `~provider/latest`; the full fixture must validate and still
select the cheapest concrete CHAT model. The live typed catalog probe must complete successfully.
