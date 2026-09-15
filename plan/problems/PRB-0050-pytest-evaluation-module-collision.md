# PRB-0050 — Evaluation test modules collided under pytest import mode

Status: resolved

Date: 2026-09-14

## Symptom and reproduction

`make evaluation-test` stopped during collection: unit and policy files both named
`test_evaluation_benchmark.py` resolved to one top-level Python module and produced an import-file
mismatch. No benchmark case ran.

## Cause

Test category directories are not Python packages. Pytest's current prepend import mode therefore
requires unique basenames across simultaneously selected directories.

## Fix and regression

Policy coverage is named `test_evaluation_policy.py`; Make references the unique path. Re-running
the same combined `make evaluation-test` selection is the regression check.
