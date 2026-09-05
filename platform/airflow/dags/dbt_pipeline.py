"""Deterministic dbt subprocess runner and ecommerce DAG factory."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

DBT_BIN = "/opt/airflow/dbt-venv/bin/dbt"
DBT_PROJECT = "/opt/airflow/dbt"
FAILURE_PROJECT = "/opt/airflow/fixtures/failing_dbt"
ARTIFACTS = "/opt/airflow/dbt-artifacts"
RAW_CHECKS = "/opt/airflow/checks/001_smoke.sql"
_STAGES = ("load_raw", "dbt_staging", "dbt_intermediate", "dbt_marts", "dbt_tests")
_LAYER_SELECT = {
    "dbt_staging": "path:models/staging",
    "dbt_intermediate": "path:models/intermediate",
    "dbt_marts": "path:models/marts",
}
_ENV_KEYS = (
    "PATH",
    "PYTHONUTF8",
    "PYTHONIOENCODING",
    "LANG",
    "LC_ALL",
    "CLICKHOUSE_HOST",
    "CLICKHOUSE_PORT",
    "CLICKHOUSE_USER",
    "CLICKHOUSE_PASSWORD",
)


class DbtPipelineError(RuntimeError):
    """Raised when dbt fails or does not produce passing evidence."""


class _NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _verify_seed(artifact_dir: Path) -> None:
    """Execute the immutable baseline assertions before potentially vacuous dbt tests."""
    # This reviewed SQL fixture has no semicolons inside strings/comments. This is
    # deliberately not a SQL parser or an interface for agent-provided queries.
    statements = [part.strip() for part in Path(RAW_CHECKS).read_text().split(";") if part.strip()]
    record: dict[str, Any] = {"status": "failed", "assertions_passed": 0}
    try:
        for statement in statements:
            request = Request(
                "http://clickhouse:8123/?readonly=1&max_execution_time=5",
                data=statement.encode("utf-8"),
                headers={
                    "X-ClickHouse-User": os.environ["CLICKHOUSE_USER"],
                    "X-ClickHouse-Key": os.environ["CLICKHOUSE_PASSWORD"],
                },
                method="POST",
            )
            with build_opener(_NoRedirects()).open(request, timeout=5) as response:
                response.read()
            record["assertions_passed"] += 1
        record["status"] = "success"
    except (OSError, HTTPError, URLError) as exc:
        if isinstance(exc, HTTPError):
            exc.close()
        raise DbtPipelineError("raw seed readiness assertions failed") from None
    finally:
        record["finished_at"] = datetime.now(UTC).isoformat()
        (artifact_dir / "seed-readiness.json").write_text(json.dumps(record), encoding="utf-8")


def _safe_id(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _environment() -> dict[str, str]:
    environment = {key: os.environ[key] for key in _ENV_KEYS if key in os.environ}
    environment.setdefault("PATH", "/usr/local/bin:/usr/bin:/bin")
    environment.setdefault("PYTHONUTF8", "1")
    return environment


def _argv(stage: str, project: str, target: str) -> list[str]:
    common = [
        "--project-dir",
        project,
        "--profiles-dir",
        DBT_PROJECT,
        "--target-path",
        target,
        "--log-path",
        str(Path(target) / "logs"),
        "--fail-fast",
    ]
    if stage == "load_raw":
        return [DBT_BIN, "test", *common, "--select", "source:*"]
    if stage in _LAYER_SELECT:
        return [DBT_BIN, "run", *common, "--full-refresh", "--select", _LAYER_SELECT[stage]]
    if stage == "dbt_tests":
        return [DBT_BIN, "test", *common]
    raise ValueError(f"unsupported dbt stage: {stage}")


def _sanitized(text: str | bytes | None) -> str:
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    text = text or ""
    password = os.environ.get("CLICKHOUSE_PASSWORD")
    if password:
        text = text.replace(password, "[redacted]")
    return "\n".join(
        "[redacted credential output]"
        if any(word in line.lower() for word in ("password", "secret", "api_token"))
        else line
        for line in text.splitlines()
    )


def run_dbt(
    stage: str, run_id: str, try_number: int = 1, project_dir: str = DBT_PROJECT
) -> dict[str, Any]:
    """Run one fixed dbt operation and persist per-attempt evidence."""
    if stage not in _STAGES:
        raise ValueError(f"unsupported dbt stage: {stage}")
    if project_dir != DBT_PROJECT and not (stage == "dbt_tests" and project_dir == FAILURE_PROJECT):
        raise ValueError("dbt project is not allowlisted for this stage")
    if not run_id or try_number < 1:
        raise ValueError("dbt run identity and attempt must be valid")
    artifact_dir = Path(ARTIFACTS) / _safe_id(run_id) / stage / str(try_number)
    # Never accept output from a previous execution of the same attempt.
    artifact_dir.mkdir(parents=True, exist_ok=False)
    argv = _argv(stage, project_dir, str(artifact_dir))
    command = {
        "stage": stage,
        "run_id": run_id,
        "try_number": try_number,
        "argv": argv,
        "started_at": datetime.now(UTC).isoformat(),
        "exit_code": None,
        "timed_out": False,
    }
    command_file = artifact_dir / "command.json"
    command_file.write_text(json.dumps(command, sort_keys=True), encoding="utf-8")
    if stage == "load_raw":
        _verify_seed(artifact_dir)
    try:
        completed = subprocess.run(
            argv,
            check=False,
            shell=False,
            capture_output=True,
            text=True,
            timeout=90,
            env=_environment(),
            cwd=artifact_dir,
        )
    except subprocess.TimeoutExpired as exc:
        command.update(timed_out=True, finished_at=datetime.now(UTC).isoformat())
        command_file.write_text(json.dumps(command, sort_keys=True), encoding="utf-8")
        (artifact_dir / "stdout.txt").write_text(
            _sanitized(exc.stdout) + "\n" + _sanitized(exc.stderr), encoding="utf-8"
        )
        raise DbtPipelineError(f"dbt {stage} timed out") from None
    command.update(exit_code=completed.returncode, finished_at=datetime.now(UTC).isoformat())
    command_file.write_text(json.dumps(command, sort_keys=True), encoding="utf-8")
    (artifact_dir / "stdout.txt").write_text(
        _sanitized(f"{completed.stdout or ''}\n{completed.stderr or ''}"), encoding="utf-8"
    )
    if completed.returncode != 0:
        raise DbtPipelineError(f"dbt {stage} failed with exit code {completed.returncode}")
    result_file = artifact_dir / "run_results.json"
    if not result_file.is_file():
        raise DbtPipelineError(f"dbt {stage} produced no run_results.json")
    try:
        payload = json.loads(result_file.read_text(encoding="utf-8"))
        results = payload["results"]
        invocation_id = payload["metadata"]["invocation_id"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        raise DbtPipelineError(f"dbt {stage} produced invalid run_results.json") from None
    if not isinstance(invocation_id, str) or not invocation_id:
        raise DbtPipelineError(f"dbt {stage} produced no invocation identity")
    if (
        not isinstance(results, list)
        or not results
        or any(
            not isinstance(item, dict)
            or item.get("status") not in {"pass", "success"}
            or not isinstance(item.get("unique_id"), str)
            or not item["unique_id"]
            for item in results
        )
    ):
        raise DbtPipelineError(f"dbt {stage} produced non-passing run results")
    evidence = {
        "stage": stage,
        "run_id": run_id,
        "invocation_id": invocation_id,
        "result_count": len(results),
        "exit_code": completed.returncode,
        "status": "success",
        "finished_at": command["finished_at"],
        "artifact_dir": str(artifact_dir),
        "result_path": str(result_file),
    }
    (artifact_dir / "evidence.json").write_text(
        json.dumps(evidence, sort_keys=True), encoding="utf-8"
    )
    return evidence


def _publish(upstream: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    if (
        not isinstance(upstream, list)
        or len(upstream) != len(_STAGES)
        or any(
            not isinstance(item, dict)
            or item.get("stage") != expected
            or item.get("run_id") != run_id
            or item.get("status") != "success"
            or item.get("exit_code") != 0
            or not isinstance(item.get("result_count"), int)
            or item["result_count"] <= 0
            or not item.get("invocation_id")
            or not item.get("result_path")
            for item, expected in zip(upstream, _STAGES, strict=True)
        )
    ):
        raise DbtPipelineError("publish requires successful evidence from every preceding stage")
    return {
        "published": True,
        "runner": "dbt-subprocess-v1",
        "stages": [item["stage"] for item in upstream],
        "run_id": run_id,
        "invocation_ids": [item["invocation_id"] for item in upstream],
    }


def build_ecommerce_dag(*, dag_id: str, schedule: str | None, failure_probe: bool = False):
    from airflow.sdk import dag, get_current_context, task

    @dag(
        dag_id=dag_id,
        schedule=schedule,
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        catchup=False,
        max_active_runs=1,
        dagrun_timeout=timedelta(minutes=10),
        is_paused_upon_creation=True,
        default_args={"retries": 0, "execution_timeout": timedelta(minutes=2)},
        tags=["agentic-data-platform", "dbt"],
    )
    def ecommerce_pipeline() -> None:
        def execute(stage: str, project: str = DBT_PROJECT) -> dict[str, Any]:
            context = get_current_context()
            return run_dbt(
                stage,
                str(context["run_id"]),
                int(context["ti"].try_number),
                project_dir=project,
            )

        @task
        def load_raw() -> list[dict[str, Any]]:
            return [execute("load_raw")]

        @task
        def dbt_staging(upstream: list[dict[str, Any]]) -> list[dict[str, Any]]:
            return [*upstream, execute("dbt_staging")]

        @task
        def dbt_intermediate(upstream: list[dict[str, Any]]) -> list[dict[str, Any]]:
            return [*upstream, execute("dbt_intermediate")]

        @task
        def dbt_marts(upstream: list[dict[str, Any]]) -> list[dict[str, Any]]:
            return [*upstream, execute("dbt_marts")]

        @task
        def dbt_tests(upstream: list[dict[str, Any]]) -> list[dict[str, Any]]:
            return [
                *upstream,
                execute("dbt_tests", FAILURE_PROJECT if failure_probe else DBT_PROJECT),
            ]

        @task
        def publish(upstream: list[dict[str, Any]]) -> dict[str, Any]:
            return _publish(upstream, str(get_current_context()["run_id"]))

        a = load_raw()
        b = dbt_staging(a)
        c = dbt_intermediate(b)
        d = dbt_marts(c)
        e = dbt_tests(d)
        publish(e)

    return ecommerce_pipeline()
