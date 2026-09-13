# ADR-0025 — Airflow trigger is a separate approved idempotent capability

Status: accepted

Date: 2026-09-13

## Context

Phase I needs to start one local development pipeline, but STEP-0014 deliberately made the observer
incapable of writes. Airflow's trigger API is state-changing, retries can duplicate work, and MAF's
interactive approval metadata alone does not protect direct gateway or MCP callers.

## Decision

Create a second repository-owned stdio MCP server and `airflow-trigger-v1` capability profile. It
exposes one trigger tool for `ecommerce_acceptance`; minimal read-back operations may be included
only to reconcile the created run. It uses a dedicated FAB identity whose exact permissions are
derived from and verified against pinned Airflow 3.3.1. It never reuses Admin or Viewer credentials.

Trigger input contains only DAG ID, a bounded opaque idempotency key, and approval ID. A local
code-owned approval command creates a short-lived mode-0600 record outside the task workspace. The
record binds those values and an approver identity. The trigger process validates and locks it;
models cannot create or amend approvals. MAF additionally declares `always_require`, while the
approval record remains mandatory for non-MAF callers.

The Airflow run ID is deterministically derived from DAG ID and idempotency key. Before POST, the
adapter reads that exact run ID: an existing matching run is the idempotent result; 404 permits one
fixed POST with code-owned run ID and empty `conf`. A timeout is reconciled by the same GET on retry.
The approval becomes consumed only after an existing or newly created run is confirmed. Reuse for a
different operation or after consumption/expiry is denied.

## Consequences

The read-only observer remains unchanged and usable without approval. Triggering requires an
explicit local human step and cannot fan out to arbitrary DAGs or payloads. Approval storage and
crash reconciliation add code and tests, but make retries deterministic and independently auditable.
Any future pause, retry, backfill, production DAG, or non-empty configuration requires another ADR,
identity/profile, and threat-specific gate.

