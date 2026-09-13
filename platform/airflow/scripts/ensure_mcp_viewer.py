#!/usr/bin/env python3
"""Idempotently provision the local read-only Airflow MCP identity."""

from __future__ import annotations

import json
import os
import signal
import subprocess


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
    print("Airflow local users: ready")


if __name__ == "__main__":
    main()
