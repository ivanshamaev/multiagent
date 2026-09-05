"""Deterministic ClickHouse seed-readiness check used by Airflow tasks."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

RAW_CHECKS = "/opt/airflow/checks/001_smoke.sql"
_CLICKHOUSE_ENV_KEYS = ("CLICKHOUSE_HOST", "CLICKHOUSE_USER", "CLICKHOUSE_PASSWORD")


class PipelineCheckError(RuntimeError):
    """Raised when a deterministic platform boundary check fails."""


class _NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def clickhouse_env() -> dict[str, str]:
    missing = [key for key in _CLICKHOUSE_ENV_KEYS if not os.environ.get(key)]
    if missing:
        raise PipelineCheckError("required ClickHouse environment is incomplete")
    return {key: os.environ[key] for key in _CLICKHOUSE_ENV_KEYS}


def verify_seed_readiness() -> dict[str, Any]:
    """Run reviewed, read-only raw-data assertions through ClickHouse HTTP."""
    try:
        sql = Path(RAW_CHECKS).read_text(encoding="utf-8")
    except OSError:
        raise PipelineCheckError("seed-readiness SQL is unavailable") from None

    statements = [part.strip() for part in sql.split(";") if part.strip()]
    credentials = clickhouse_env()
    passed = 0
    try:
        for statement in statements:
            request = Request(
                "http://clickhouse:8123/?readonly=1&max_execution_time=5",
                data=statement.encode("utf-8"),
                headers={
                    "X-ClickHouse-User": credentials["CLICKHOUSE_USER"],
                    "X-ClickHouse-Key": credentials["CLICKHOUSE_PASSWORD"],
                },
                method="POST",
            )
            with build_opener(_NoRedirects()).open(request, timeout=5) as response:
                response.read()
            passed += 1
    except (HTTPError, URLError, OSError) as exc:
        if isinstance(exc, HTTPError):
            exc.close()
        raise PipelineCheckError("raw seed readiness assertions failed") from None

    return {
        "status": "success",
        "assertions_passed": passed,
        "finished_at": datetime.now(UTC).isoformat(),
    }
