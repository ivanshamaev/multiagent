import importlib
import sys
from pathlib import Path
from urllib.error import HTTPError

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "platform" / "airflow" / "dags"))
seed_readiness = importlib.import_module("seed_readiness")


def test_clickhouse_environment_is_strictly_allowlisted(monkeypatch):
    monkeypatch.setenv("CLICKHOUSE_HOST", "clickhouse")
    monkeypatch.setenv("CLICKHOUSE_USER", "unit-user")
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "unit-password")
    monkeypatch.setenv("API_TOKEN", "must-not-propagate")

    assert seed_readiness.clickhouse_env() == {
        "CLICKHOUSE_HOST": "clickhouse",
        "CLICKHOUSE_USER": "unit-user",
        "CLICKHOUSE_PASSWORD": "unit-password",
    }


def test_missing_environment_fails_closed(monkeypatch):
    for key in ("CLICKHOUSE_HOST", "CLICKHOUSE_USER", "CLICKHOUSE_PASSWORD"):
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(seed_readiness.PipelineCheckError, match="incomplete"):
        seed_readiness.clickhouse_env()


def test_missing_sql_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(seed_readiness, "RAW_CHECKS", str(tmp_path / "missing.sql"))

    with pytest.raises(seed_readiness.PipelineCheckError, match="unavailable"):
        seed_readiness.verify_seed_readiness()


def test_seed_readiness_uses_readonly_requests(tmp_path, monkeypatch):
    checks = tmp_path / "checks.sql"
    checks.write_text("SELECT 1; SELECT 2;", encoding="utf-8")
    monkeypatch.setattr(seed_readiness, "RAW_CHECKS", str(checks))
    monkeypatch.setenv("CLICKHOUSE_HOST", "clickhouse")
    monkeypatch.setenv("CLICKHOUSE_USER", "unit-user")
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "unit-password")
    requests = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b""

    class Opener:
        def open(self, request, timeout):
            requests.append((request, timeout))
            return Response()

    monkeypatch.setattr(seed_readiness, "build_opener", lambda *args: Opener())
    evidence = seed_readiness.verify_seed_readiness()

    assert evidence["status"] == "success"
    assert evidence["assertions_passed"] == 2
    assert len(requests) == 2
    assert all("readonly=1" in request.full_url for request, _ in requests)
    assert all(request.method == "POST" and timeout == 5 for request, timeout in requests)
    assert all(request.get_header("X-clickhouse-key") == "unit-password" for request, _ in requests)


def test_empty_seed_failure_has_no_response_or_secret_reflection(tmp_path, monkeypatch):
    checks = tmp_path / "checks.sql"
    checks.write_text("SELECT throwIf(1, 'empty');", encoding="utf-8")
    monkeypatch.setattr(seed_readiness, "RAW_CHECKS", str(checks))
    monkeypatch.setenv("CLICKHOUSE_HOST", "clickhouse")
    monkeypatch.setenv("CLICKHOUSE_USER", "unit-user")
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "private-password")

    class Opener:
        def open(self, request, timeout):
            raise HTTPError(request.full_url, 500, "private-password", {}, None)

    monkeypatch.setattr(seed_readiness, "build_opener", lambda *args: Opener())
    with pytest.raises(seed_readiness.PipelineCheckError) as exc_info:
        seed_readiness.verify_seed_readiness()

    assert "private-password" not in str(exc_info.value)
