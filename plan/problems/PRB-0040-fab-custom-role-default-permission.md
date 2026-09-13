# PRB-0040 — FAB custom role receives a default Website permission

Status: resolved

Date: 2026-09-13

## Reproduction and cause

The first live `make airflow-init` after creating `AgenticDataTrigger` failed the exact-permission
check. `airflow roles list --permission --output json` showed that FAB automatically attaches
`can_read` on `Website` when an empty custom role is created. The repository had assumed no default
permission.

## Resolution and regression

The exact role manifest explicitly includes this FAB-required base permission alongside the four
operation permissions: create/read `DAG Runs` and edit/read only
`DAG:ecommerce_acceptance`. Any other permission still fails bootstrap. Unit policy checks assert
that broad `can_edit` on `DAGs` is absent; live bootstrap and API tests verify the effective role.
