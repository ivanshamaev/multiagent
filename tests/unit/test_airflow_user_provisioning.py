"""Regression checks for secret-safe, retryable local Airflow user provisioning."""

from __future__ import annotations

import importlib.util
import signal
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _module() -> ModuleType:
    path = ROOT / "platform/airflow/scripts/ensure_mcp_viewer.py"
    spec = importlib.util.spec_from_file_location("ensure_mcp_viewer", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_airflow_cli_sigsegv_is_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _module()
    results = iter(
        [
            subprocess.CompletedProcess([], -signal.SIGSEGV, "", "native crash"),
            subprocess.CompletedProcess([], 0, "[]", ""),
        ]
    )
    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: next(results))

    assert module._run(["airflow", "users", "list"]).returncode == 0


def test_airflow_cli_failure_does_not_echo_password(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _module()
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess([], 2, "", "bad"),
    )

    with pytest.raises(RuntimeError) as captured:
        module._run(["airflow", "users", "create", "--password", "do-not-leak"])

    assert "do-not-leak" not in str(captured.value)


def test_compose_uses_only_repository_user_bootstrap() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "_AIRFLOW_WWW_USER_CREATE" not in compose
    assert "command: python /opt/airflow/ensure_mcp_viewer.py" in compose
