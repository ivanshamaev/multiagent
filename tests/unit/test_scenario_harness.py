import json
import stat
from pathlib import Path

import pytest

from runtime.scenario_harness import (
    ExitCode,
    HarnessError,
    build_baseline,
    load_manifest,
    parse_manifest,
    reproducibility_fingerprint,
    reset_workspace,
)

ROOT = Path(__file__).resolve().parents[2]


def _payload() -> dict[str, object]:
    return {
        "schema_version": 1,
        "id": "unit-scenario",
        "version": "1.2.3",
        "task_file": "scenarios/unit-scenario/task.md",
        "source": {
            "commit": "a" * 40,
            "snapshot_paths": ["project"],
            "excluded_names": ["target", "logs"],
        },
        "workspace": {
            "editable_paths": ["project/models/**"],
            "required_paths": ["TASK.md", "project/project.yml"],
        },
        "budgets": {
            "wall_time_seconds": 60,
            "tool_calls": 5,
            "model_tokens": 100,
            "rework_attempts": 0,
        },
        "setup": {"commands": ["make seed"]},
        "public_validation": {"commands": ["make validate"]},
        "hidden_grade": {
            "interface_version": 1,
            "command": "make grade",
            "container_service": "scenario-grader",
            "oracle_sha256": "b" * 64,
        },
    }


def _repository(tmp_path: Path) -> tuple[Path, object]:
    repository = tmp_path / "repository"
    (repository / "project/models").mkdir(parents=True)
    (repository / "project/project.yml").write_text("name: fixture\n", encoding="utf-8")
    (repository / "project/models/base.sql").write_text("select 1\n", encoding="utf-8")
    task = repository / "scenarios/unit-scenario/task.md"
    task.parent.mkdir(parents=True)
    task.write_text("# Unit task\n", encoding="utf-8")
    return repository, parse_manifest(_payload())


def test_repository_manifest_is_strict_and_builds_public_projection() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    baseline = build_baseline(ROOT, manifest)
    public = json.loads(baseline.contents[".scenario/manifest.json"])

    assert manifest.scenario_id == "net-revenue"
    assert public["source"]["fingerprint"] == baseline.source_fingerprint
    assert "oracle_sha256" not in json.dumps(public)
    assert all(not path.startswith("grader/") for path in baseline.files)


def test_manifest_rejects_unknown_fields() -> None:
    payload = _payload()
    payload["unexpected"] = True

    with pytest.raises(HarnessError, match="keys mismatch"):
        parse_manifest(payload)


def test_reset_has_stable_content_addressed_fingerprint(tmp_path: Path) -> None:
    repository, manifest = _repository(tmp_path)
    first = reset_workspace(repository, manifest)
    second = reset_workspace(repository, manifest)

    assert first["baseline_fingerprint"] == second["baseline_fingerprint"]
    assert first["source_fingerprint"] == second["source_fingerprint"]
    workspace = Path(str(second["workspace"]))
    assert not (workspace / ".git").exists()
    assert stat.S_IMODE(workspace.stat().st_mode) == 0o755
    assert (workspace / "TASK.md").read_text(encoding="utf-8") == "# Unit task\n"


def test_fingerprint_requires_recorded_data(tmp_path: Path) -> None:
    repository, manifest = _repository(tmp_path)
    reset_workspace(repository, manifest)

    with pytest.raises(HarnessError, match="has not been recorded"):
        reproducibility_fingerprint(repository, manifest)


def test_exit_codes_are_stable() -> None:
    assert ExitCode.OK == 0
    assert ExitCode.INVALID_STATE == 20
    assert ExitCode.STALE_SOURCE == 21
    assert ExitCode.PROTECTED_CHANGE == 22
    assert ExitCode.UNSAFE_PATH == 23
