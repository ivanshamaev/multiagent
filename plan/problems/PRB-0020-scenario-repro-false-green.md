# PRB-0020 — scenario reproducibility gate returned false green

Status: closed
Detected: 2026-09-11
Resolved: 2026-09-11

## Symptom and reproduction

While Docker registry DNS was unavailable, `make scenario-repro-test` printed two failed
`scenario-reset` executions but returned exit code 0 and empty fingerprints.

## Root cause

The multi-command Make recipe did not enable shell fail-fast behavior. A failed command substitution
inside the `first=...` or `second=...` assignment was followed by later successful commands, and two
empty strings incorrectly satisfied the equality check.

## Accepted fix

The recipe now starts with `set -e`, so either failed reset/fingerprint aborts immediately. A
repository policy test protects the fail-fast prefix from accidental removal.

## Regression check

With a failing `scenario-reset`, `make scenario-repro-test` must return non-zero at the first failed
precondition. It must never print an empty fingerprint as success.
`make scenario-repro-test MAKE=false` returned exit code `2`, confirming the negative path.
