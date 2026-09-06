# PRB-0016 — Text probe did not predict structured model reliability

Status: closed

Date: 2026-09-06

## Reproduction and evidence

After the first valid Mistral Nemo smoke, two final controlled runs failed closed with sanitized
HTTP 504 after bounded SDK retries. The earlier one-token text probe still returned 200. A
cost-ordered comparison then observed: Ling 3.0 failed the schema capability gate; IBM Granite
Micro passed that gate but returned an artifact rejected by Pydantic; Llama 3.1 8B passed both the
gate and full workflow. Failed payloads and provider response bodies were not persisted.

## Root cause

The live selector tested routing of unconstrained text. Catalog presence and a short text response
do not prove JSON-schema support, full-request reliability, or conformance to the domain contract.

## Accepted fix

The capability request now uses a strict, minimal JSON schema and at most eight output tokens.
Cost-first selection remains the default, while a versioned `LLM_DEFAULT_MODEL` can constrain the
probe to one measured role candidate. Candidate 400/404 outcomes are reported only as model ID and
HTTP status; auth, balance, rate-limit, server, and transport failures stop immediately. The
verified PM default is `meta-llama/llama-3.1-8b-instruct` pending repeated evaluation.

## Regression check and follow-up

Mock-transport tests verify schema request shape, cost order, explicit override, safe all-failed
diagnostics, and no fall-through on 401/402/429/500. A small schema probe is not a quality proof;
STEP-0008 must preserve policy boundaries, and repeated quality/cost evaluation belongs to Phase K.
Usage from a response that fails artifact validation is not yet an accepted workflow event and is
recorded as a residual observability risk.
