# PRB-0021 — MAF handler shadowed Executor execution entrypoint

Status: closed
Detected: 2026-09-12
Resolved: 2026-09-12

## Symptom and reproduction

The first offline Data Engineer workflow failed before its handler ran with
`AutonomousDataEngineerExecutor.execute() got an unexpected keyword argument 'trace_contexts'`.
The failure was reproduced by the end-to-end workflow integration test.

## Root cause

The decorated message handler was named `execute`, shadowing the framework-owned
`Executor.execute` dispatch method. MAF called the replacement with its internal dispatch
arguments rather than routing the message through the registered typed handler.

## Accepted fix

Rename the role handler to `run_attempt`. The framework entrypoint remains inherited and the
decorator registers the typed `DataEngineerRunRequest` handler normally.

## Regression check

`tests/integration/test_data_engineer_workflow.py` executes the complete MAF graph and asserts a
verified event chain ending at `VALIDATED`. The targeted suite passed 35 tests after the rename.
