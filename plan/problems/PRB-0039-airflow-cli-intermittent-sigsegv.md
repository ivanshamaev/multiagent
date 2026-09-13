# PRB-0039 — Airflow user-provisioning CLI intermittently received SIGSEGV

Status: resolved

Date: 2026-09-13

## Reproduction

During final STEP-0014 regression, the first `make platform-test` reached `airflow-validate`, where
`airflow dags list-import-errors` exited `139`. A second run failed earlier: the Compose entrypoint's
automatic admin creation and the repository Viewer bootstrap each received `SIGSEGV` while the
already-running Airflow stack was being revalidated. The same CLI read succeeded immediately when
run alone, identifying an intermittent native-process failure rather than a DAG import error.

## Cause and risk

Each Compose invocation repeated the entrypoint's unconditional admin-user CLI and then launched
more user CLI subprocesses. Besides making a transient native crash fatal, a failed `users create`
could expose its password-bearing argument list through `CalledProcessError`.

## Fix and regression

Automatic entrypoint user creation is disabled. One repository bootstrap now idempotently verifies
both the Admin and exact Viewer identity, retries only `SIGSEGV` at most three times, captures child
output, and reports credential-free errors. The read-only DAG validation CLI uses the same bounded
signal-specific retry wrapper; all other exit codes propagate unchanged. Unit tests cover retry,
exit-code propagation, and error secrecy. Repeated init, `make airflow-mcp-smoke`, and the full
`make platform-test` are the live regression gates.
