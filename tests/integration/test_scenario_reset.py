import json
from pathlib import Path

import pytest

from runtime.agent_runtime import prepare_scenario_specification_request
from runtime.context import build_scenario_context
from runtime.scenario_harness import (
    ProtectedChangeError,
    inspect_workspace,
    parse_manifest,
    record_data_fingerprint,
    reproducibility_fingerprint,
    reset_workspace,
    verify_workspace,
)


def _fixture(tmp_path: Path):
    repository = tmp_path / "repository"
    (repository / "project/models").mkdir(parents=True)
    (repository / "project/project.yml").write_text("name: fixture\n", encoding="utf-8")
    (repository / "project/models/base.sql").write_text("select 1\n", encoding="utf-8")
    task = repository / "scenarios/reset-test/task.md"
    task.parent.mkdir(parents=True)
    task.write_text("# Reset test\n", encoding="utf-8")
    payload = {
        "schema_version": 1,
        "id": "reset-test",
        "version": "1.0.0",
        "task_file": "scenarios/reset-test/task.md",
        "source": {
            "commit": "1" * 40,
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
            "rework_attempts": 1,
        },
        "setup": {"commands": ["make seed"]},
        "public_validation": {"commands": ["make validate"]},
        "hidden_grade": {
            "interface_version": 1,
            "command": "make grade",
            "container_service": "scenario-grader",
            "oracle_sha256": "2" * 64,
        },
    }
    manifest_path = repository / "scenarios/reset-test/manifest.json"
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    manifest = parse_manifest(payload)
    return repository, manifest


def test_two_resets_recover_contamination_and_match(tmp_path: Path) -> None:
    repository, manifest = _fixture(tmp_path)
    first = reset_workspace(repository, manifest)
    workspace = Path(str(first["workspace"]))
    record_data_fingerprint(repository, manifest, b"logical-clickhouse-state\n")
    first_fingerprint = reproducibility_fingerprint(repository, manifest)

    (workspace / "project/models/base.sql").write_text("select 2\n", encoding="utf-8")
    (workspace / "project/models/new.sql").write_text("select 3\n", encoding="utf-8")
    (workspace / "project/target").mkdir()
    (workspace / "project/target/runtime.json").write_text("{}\n", encoding="utf-8")
    allowed_status = verify_workspace(repository, manifest)
    assert allowed_status["ok"]
    assert allowed_status["modified"] == ["project/models/base.sql"]
    assert allowed_status["added"] == ["project/models/new.sql"]

    reset_workspace(repository, manifest)
    record_data_fingerprint(repository, manifest, b"logical-clickhouse-state\n")
    second_fingerprint = reproducibility_fingerprint(repository, manifest)
    status = inspect_workspace(repository, manifest)

    assert first_fingerprint == second_fingerprint
    assert status["actual_fingerprint"] == status["baseline_fingerprint"]
    assert status["added"] == status["deleted"] == status["modified"] == []
    assert not (workspace / "project/models/new.sql").exists()
    assert not (workspace / "project/target").exists()


def test_context_is_read_only_from_verified_managed_workspace(tmp_path: Path) -> None:
    repository, manifest = _fixture(tmp_path)
    reset_workspace(repository, manifest)

    context = build_scenario_context(
        repository,
        manifest.scenario_id,
        relative_paths=("TASK.md", "project/project.yml"),
    )

    assert context.workspace_fingerprint
    assert tuple(document.path for document in context.documents) == (
        "TASK.md",
        "project/project.yml",
    )
    assert all(not document.path.startswith("grader/") for document in context.documents)

    request = prepare_scenario_specification_request(
        repository,
        manifest.scenario_id,
        workflow_id="workflow-context-test",
        correlation_id="correlation-context-test",
    )
    assert request.context == build_scenario_context(repository, manifest.scenario_id)
    assert request.budget_limits.model_tokens == 100
    assert request.task.task_id == "scenario-reset-test"


def test_request_preparation_rejects_protected_workspace_change(tmp_path: Path) -> None:
    repository, manifest = _fixture(tmp_path)
    reset_result = reset_workspace(repository, manifest)
    workspace = Path(str(reset_result["workspace"]))
    (workspace / "project/project.yml").write_text("name: tampered\n", encoding="utf-8")

    with pytest.raises(ProtectedChangeError, match=r"project/project\.yml"):
        prepare_scenario_specification_request(
            repository,
            manifest.scenario_id,
            workflow_id="workflow-protected-test",
            correlation_id="correlation-protected-test",
        )
