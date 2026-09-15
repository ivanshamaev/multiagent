# PRB-0052 — Checkpoint publication permission race

Status: resolved

Date: 2026-09-15

## Reproduction and cause

After two 51/51 benchmark samples, `make check` failed at receipt crash recovery (449 PASS/one FAIL):
`checkpoint must have mode 0600`. MAF FileCheckpointStorage writes `.json.tmp` with default file
mode then replaces the final `.json`; SecureCheckpointStorage chmods only after delegate.save returns.
A concurrent reader can therefore see a final checkpoint before the permission change.

## Planned fix and regression

Delegate encoding/writing into a private staging directory, set 0600 before publication, and hard-link
the completed file to its final name atomically without overwriting existing IDs. Readers ignore only
well-formed owner-only staging directories. Keep fail-closed permission checks. A deterministic test
observes storage while delegate.save has finished but final publication has not happened; no final
checkpoint may be listed. Repeat benchmark and full checks after the fix.

Implemented: MAF serialization runs in mode-0700 staging; the completed file is chmod-0600 and
fsynced before atomic create-only publication. Staging cleanup races are ignored only when the
entry disappeared; malformed/symlink/loose-mode entries fail closed. Targeted checkpoint/recovery
selection passed seven tests (exit 0); final full-gate results are retained in STEP-0024 evidence.
