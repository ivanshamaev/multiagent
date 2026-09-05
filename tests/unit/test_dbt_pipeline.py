import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "platform" / "airflow" / "dags"))
import dbt_pipeline


def _completed(code=0, stdout="ok", results=None):
    def fake(argv, **kwargs):
        target = argv[argv.index("--target-path") + 1]
        if results is not None:
            with open(f"{target}/run_results.json", "w", encoding="utf-8") as handle:
                json.dump(
                    {"metadata": {"invocation_id": "unit-invocation"}, "results": results}, handle
                )
        return subprocess.CompletedProcess(argv, code, stdout, "")

    return fake


def test_run_dbt_uses_fixed_argv_and_allowlisted_environment(tmp_path, monkeypatch):
    calls = []

    def fake(argv, **kwargs):
        calls.append((argv, kwargs))
        target = argv[argv.index("--target-path") + 1]
        (tmp_path / "unused").mkdir(exist_ok=True)
        with open(f"{target}/run_results.json", "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "metadata": {"invocation_id": "unit-invocation"},
                    "results": [{"status": "success", "unique_id": "model.x"}],
                },
                handle,
            )
        return subprocess.CompletedProcess(argv, 0, "safe", "")

    monkeypatch.setattr(dbt_pipeline, "ARTIFACTS", str(tmp_path))
    monkeypatch.setenv("API_TOKEN", "must-not-leak")
    monkeypatch.setenv("AIRFLOW__CORE__SQL_ALCHEMY_CONN", "must-not-leak")
    monkeypatch.setattr(dbt_pipeline.subprocess, "run", fake)
    evidence = dbt_pipeline.run_dbt("dbt_staging", "manual/run", 2)
    argv, kwargs = calls[0]
    assert argv == [
        dbt_pipeline.DBT_BIN,
        "run",
        "--project-dir",
        dbt_pipeline.DBT_PROJECT,
        "--profiles-dir",
        dbt_pipeline.DBT_PROJECT,
        "--target-path",
        evidence["artifact_dir"],
        "--log-path",
        str(Path(evidence["artifact_dir"]) / "logs"),
        "--fail-fast",
        "--full-refresh",
        "--select",
        "path:models/staging",
    ]
    assert (
        "API_TOKEN" not in kwargs["env"] and "AIRFLOW__CORE__SQL_ALCHEMY_CONN" not in kwargs["env"]
    )
    assert kwargs["shell"] is False
    assert kwargs["cwd"] == Path(evidence["artifact_dir"])
    assert kwargs["timeout"] == 90
    assert evidence["invocation_id"] == "unit-invocation"
    assert evidence["result_count"] == 1
    assert (
        tmp_path / dbt_pipeline._safe_id("manual/run") / "dbt_staging" / "2" / "stdout.txt"
    ).read_text().strip() == "safe"


@pytest.mark.parametrize("scenario", ["nonzero", "timeout", "empty", "failed"])
def test_run_dbt_rejects_failures_and_empty_results(tmp_path, monkeypatch, scenario):
    monkeypatch.setattr(dbt_pipeline, "ARTIFACTS", str(tmp_path))
    if scenario == "timeout":

        def fake(*args, **kwargs):
            raise subprocess.TimeoutExpired(args[0], kwargs["timeout"], output="partial")
    else:
        results = (
            []
            if scenario == "empty"
            else [{"status": "fail" if scenario == "failed" else "pass", "unique_id": "x"}]
        )
        fake = _completed(1 if scenario == "nonzero" else 0, results=results)
    monkeypatch.setattr(dbt_pipeline.subprocess, "run", fake)
    with pytest.raises(dbt_pipeline.DbtPipelineError):
        dbt_pipeline.run_dbt("dbt_tests", "failure", 1)


def test_publish_requires_all_successful_stage_evidence():
    evidence = [
        {
            "stage": stage,
            "run_id": "r",
            "status": "success",
            "exit_code": 0,
            "invocation_id": stage,
            "result_count": 1,
            "result_path": "/output/run_results.json",
        }
        for stage in ("load_raw", "dbt_staging", "dbt_intermediate", "dbt_marts", "dbt_tests")
    ]
    assert dbt_pipeline._publish(evidence, "r")["published"] is True
    with pytest.raises(dbt_pipeline.DbtPipelineError):
        dbt_pipeline._publish(evidence[:-1], "r")
    with pytest.raises(dbt_pipeline.DbtPipelineError):
        dbt_pipeline._publish(evidence, "different-run")
    evidence[-1]["status"] = "failed"
    with pytest.raises(dbt_pipeline.DbtPipelineError):
        dbt_pipeline._publish(evidence, "r")


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"metadata": {}, "results": []},
        {"metadata": {"invocation_id": "x"}, "results": [None]},
        {"metadata": {"invocation_id": None}, "results": [{"status": "pass", "unique_id": "x"}]},
    ],
)
def test_invalid_result_metadata_is_rejected(tmp_path, monkeypatch, payload):
    monkeypatch.setattr(dbt_pipeline, "ARTIFACTS", str(tmp_path))

    def fake(argv, **kwargs):
        target = Path(argv[argv.index("--target-path") + 1])
        (target / "run_results.json").write_text(json.dumps(payload))
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(dbt_pipeline.subprocess, "run", fake)
    with pytest.raises(dbt_pipeline.DbtPipelineError):
        dbt_pipeline.run_dbt("dbt_tests", "invalid")


def test_attempt_cannot_reuse_stale_results(tmp_path, monkeypatch):
    monkeypatch.setattr(dbt_pipeline, "ARTIFACTS", str(tmp_path))
    monkeypatch.setattr(
        dbt_pipeline.subprocess,
        "run",
        _completed(results=[{"status": "pass", "unique_id": "test.x"}]),
    )
    dbt_pipeline.run_dbt("dbt_tests", "same-run")
    with pytest.raises(FileExistsError):
        dbt_pipeline.run_dbt("dbt_tests", "same-run")


def test_timeout_records_failure_and_redacts_raw_credential(tmp_path, monkeypatch):
    monkeypatch.setattr(dbt_pipeline, "ARTIFACTS", str(tmp_path))
    monkeypatch.setattr(dbt_pipeline, "_verify_seed", lambda target: None)
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "private-credential")

    def fake(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, 90, output=b"failed: private-credential")

    monkeypatch.setattr(dbt_pipeline.subprocess, "run", fake)
    with pytest.raises(dbt_pipeline.DbtPipelineError):
        dbt_pipeline.run_dbt("load_raw", "timeout")
    target = tmp_path / dbt_pipeline._safe_id("timeout") / "load_raw" / "1"
    assert "private-credential" not in (target / "stdout.txt").read_text()
    record = json.loads((target / "command.json").read_text())
    assert record["timed_out"] is True
    assert record["exit_code"] is None
    assert record["finished_at"]


def test_unknown_project_is_rejected_before_execution():
    with pytest.raises(ValueError, match="allowlisted"):
        dbt_pipeline.run_dbt("dbt_tests", "run", project_dir="/tmp/untrusted")


def test_empty_seed_failure_prevents_dbt_execution(tmp_path, monkeypatch):
    from urllib.error import HTTPError

    monkeypatch.setattr(dbt_pipeline, "ARTIFACTS", str(tmp_path))
    checks = Path(__file__).parents[2] / "platform/clickhouse/tests/001_smoke.sql"
    monkeypatch.setattr(dbt_pipeline, "RAW_CHECKS", str(checks))
    monkeypatch.setenv("CLICKHOUSE_USER", "unit-user")
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "unit-secret")
    calls = []

    class EmptySeed:
        def open(self, request, timeout):
            calls.append(request)
            raise HTTPError(request.full_url, 500, "orders count drift", {}, None)

    monkeypatch.setattr(dbt_pipeline, "build_opener", lambda *args: EmptySeed())

    def no_dbt(*args, **kwargs):
        pytest.fail("dbt must not run after seed readiness fails")

    monkeypatch.setattr(dbt_pipeline.subprocess, "run", no_dbt)
    with pytest.raises(dbt_pipeline.DbtPipelineError, match="seed readiness"):
        dbt_pipeline.run_dbt("load_raw", "empty-seed")
    assert len(calls) == 1
    assert "readonly=1" in calls[0].full_url
    target = tmp_path / dbt_pipeline._safe_id("empty-seed") / "load_raw" / "1"
    assert json.loads((target / "seed-readiness.json").read_text())["status"] == "failed"
    assert not (target / "evidence.json").exists()
