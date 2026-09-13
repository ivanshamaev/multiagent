#!/usr/bin/env python3
"""Idempotently provision the local read-only Airflow MCP identity."""

from __future__ import annotations

import json
import os
import signal
import subprocess

TRIGGER_ROLE = "AgenticDataTrigger"
TRIGGER_PERMISSIONS = frozenset(
    {
        ("can_create", "DAG Runs"),
        ("can_read", "DAG Runs"),
        ("can_edit", "DAG:ecommerce_acceptance"),
        ("can_read", "DAG:ecommerce_acceptance"),
        ("can_read", "Website"),
    }
)


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable {name} is missing")
    return value


def _run(arguments: list[str], *, attempts: int = 3) -> subprocess.CompletedProcess[str]:
    """Run an Airflow CLI operation without leaking credential-bearing arguments."""

    for attempt in range(1, attempts + 1):
        result = subprocess.run(arguments, check=False, capture_output=True, text=True)
        if result.returncode == 0:
            return result
        if result.returncode != -signal.SIGSEGV or attempt == attempts:
            raise RuntimeError("Airflow local-user provisioning command failed")
    raise RuntimeError("Airflow local-user provisioning retries were exhausted")


def _users() -> list[dict[str, object]]:
    result = _run(["airflow", "users", "list", "--output", "json"])
    payload = json.loads(result.stdout)
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise RuntimeError("Airflow user listing returned an invalid response")
    return payload


def _ensure_trigger_role() -> None:
    _run(["airflow", "sync-perm", "--include-dags"])
    roles = json.loads(_run(["airflow", "roles", "list", "--output", "json"]).stdout)
    if not isinstance(roles, list) or not all(isinstance(item, dict) for item in roles):
        raise RuntimeError("Airflow role listing returned an invalid response")
    if TRIGGER_ROLE not in {item.get("name") for item in roles}:
        _run(["airflow", "roles", "create", TRIGGER_ROLE])

    rows = json.loads(_run(["airflow", "roles", "list", "--permission", "--output", "json"]).stdout)
    if not isinstance(rows, list) or not all(isinstance(item, dict) for item in rows):
        raise RuntimeError("Airflow permission listing returned an invalid response")
    actual = {
        (action, str(item.get("resource")))
        for item in rows
        if item.get("name") == TRIGGER_ROLE
        for action in str(item.get("action", "")).split(",")
        if action
    }
    unexpected = actual - TRIGGER_PERMISSIONS
    if unexpected:
        raise RuntimeError("Airflow trigger role has unexpected permissions")
    for action, resource in sorted(TRIGGER_PERMISSIONS - actual):
        _run(
            [
                "airflow",
                "roles",
                "add-perms",
                "-a",
                action,
                "-r",
                resource,
                TRIGGER_ROLE,
            ]
        )

    verified_rows = json.loads(
        _run(["airflow", "roles", "list", "--permission", "--output", "json"]).stdout
    )
    verified = {
        (action, str(item.get("resource")))
        for item in verified_rows
        if item.get("name") == TRIGGER_ROLE
        for action in str(item.get("action", "")).split(",")
        if action
    }
    if verified != TRIGGER_PERMISSIONS:
        raise RuntimeError("Airflow trigger role does not have the exact permission set")


def _ensure_user(
    *,
    username: str,
    password: str,
    firstname: str,
    lastname: str,
    role: str,
    email: str,
) -> None:
    matched = [item for item in _users() if item.get("username") == username]
    if not matched:
        _run(
            [
                "airflow",
                "users",
                "create",
                "--username",
                username,
                "--password",
                password,
                "--firstname",
                firstname,
                "--lastname",
                lastname,
                "--role",
                role,
                "--email",
                email,
            ],
        )
        matched = [item for item in _users() if item.get("username") == username]
    if len(matched) != 1 or matched[0].get("roles") != [role]:
        raise RuntimeError("Airflow local identity is missing or has an unexpected role")


def main() -> None:
    _ensure_trigger_role()
    _ensure_user(
        username=_required("AIRFLOW_ADMIN_USERNAME"),
        password=_required("AIRFLOW_ADMIN_PASSWORD"),
        firstname="Airflow",
        lastname="Admin",
        role="Admin",
        email="airflow-admin@example.invalid",
    )
    _ensure_user(
        username=_required("AIRFLOW_MCP_USERNAME"),
        password=_required("AIRFLOW_MCP_PASSWORD"),
        firstname="Airflow",
        lastname="Observer",
        role="Viewer",
        email="airflow-observer@example.invalid",
    )
    _ensure_user(
        username=_required("AIRFLOW_TRIGGER_USERNAME"),
        password=_required("AIRFLOW_TRIGGER_PASSWORD"),
        firstname="Airflow",
        lastname="Trigger",
        role=TRIGGER_ROLE,
        email="airflow-trigger@example.invalid",
    )
    print("Airflow local users: ready")


if __name__ == "__main__":
    main()
