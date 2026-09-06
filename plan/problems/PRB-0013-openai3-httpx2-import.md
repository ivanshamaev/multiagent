# PRB-0013 — OpenAI 3 uses the `httpx2` package

Status: closed

Date: 2026-09-06

## Reproduction

After installing pinned `agent-framework-openai==1.14.2`, collection of
`tests/unit/test_model_provider.py` failed with `ModuleNotFoundError: No module named 'httpx'`.
`uv tree` showed `openai==3.8.0 → httpx2==2.12.0`.

## Cause

The current OpenAI 3 dependency stack imports the separately distributed `httpx2` package. The
catalog adapter had assumed the older package name `httpx` from prior SDK generations.

## Fix

Declare `httpx2==2.12.0` as a direct runtime dependency because project code uses it, and import it
as `httpx` locally so request/response type names remain readable. Do not install a second legacy
HTTP client solely to preserve an obsolete import.

## Regression check

`test_model_provider.py` imports the declared package and exercises `AsyncClient`, `MockTransport`,
authenticated catalog success, HTTP failure and invalid schema. Dependency policy checks pin every
runtime dependency.
