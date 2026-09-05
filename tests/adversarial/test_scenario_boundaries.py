from pathlib import Path

import pytest

from runtime.scenario_harness import (
    ProtectedChangeError,
    StaleSourceError,
    UnsafePathError,
    parse_manifest,
    reset_workspace,
    validate_relative_path,
    validate_scenario_id,
    verify_workspace,
)


def _fixture(tmp_path: Path):
    repository = tmp_path / "repository"
    (repository / "project/models").mkdir(parents=True)
    (repository / "project/project.yml").write_text("name: fixture\n", encoding="utf-8")
    (repository / "project/models/base.sql").write_text("select 1\n", encoding="utf-8")
    task = repository / "scenarios/boundary-test/task.md"
    task.parent.mkdir(parents=True)
    task.write_text("# Boundary test\n", encoding="utf-8")
    manifest = parse_manifest(
        {
            "schema_version": 1,
            "id": "boundary-test",
            "version": "1.0.0",
            "task_file": "scenarios/boundary-test/task.md",
            "source": {
                "commit": "3" * 40,
                "snapshot_paths": ["project"],
                "excluded_names": ["target"],
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
                "oracle_sha256": "4" * 64,
            },
        }
    )
    return repository, manifest


@pytest.mark.parametrize("value", ["../grader", "a/b", "UPPER", "a--b", "-bad", "bad-"])
def test_scenario_id_rejects_ambiguous_or_traversing_values(value: str) -> None:
    with pytest.raises(UnsafePathError):
        validate_scenario_id(value)


@pytest.mark.parametrize("value", ["../grader", "/etc/passwd", "a/../../b", "a\\b", "a//b"])
def test_relative_path_rejects_escape_attempts(value: str) -> None:
    with pytest.raises(UnsafePathError):
        validate_relative_path(value, "fixture")


def test_reset_refuses_unmanaged_existing_target(tmp_path: Path) -> None:
    repository, manifest = _fixture(tmp_path)
    target = repository / ".scenario-state/workspaces/boundary-test"
    target.mkdir(parents=True)
    protected = target / "user-owned.txt"
    protected.write_text("keep\n", encoding="utf-8")

    with pytest.raises(UnsafePathError, match="sentinel"):
        reset_workspace(repository, manifest)

    assert protected.read_text(encoding="utf-8") == "keep\n"


def test_protected_change_is_denied(tmp_path: Path) -> None:
    repository, manifest = _fixture(tmp_path)
    result = reset_workspace(repository, manifest)
    workspace = Path(str(result["workspace"]))
    (workspace / "project/project.yml").write_text("name: tampered\n", encoding="utf-8")

    with pytest.raises(ProtectedChangeError, match=r"project/project\.yml"):
        verify_workspace(repository, manifest)


def test_changed_source_marks_workspace_stale(tmp_path: Path) -> None:
    repository, manifest = _fixture(tmp_path)
    reset_workspace(repository, manifest)
    (repository / "project/models/base.sql").write_text("select 999\n", encoding="utf-8")

    with pytest.raises(StaleSourceError, match="scenario-reset"):
        verify_workspace(repository, manifest)


def test_snapshot_rejects_symlink_even_when_it_stays_inside_repository(tmp_path: Path) -> None:
    repository, manifest = _fixture(tmp_path)
    (repository / "project/models/link.sql").symlink_to(repository / "project/models/base.sql")

    with pytest.raises(UnsafePathError, match="symlink"):
        reset_workspace(repository, manifest)


def test_state_root_cannot_escape_repository(tmp_path: Path) -> None:
    repository, manifest = _fixture(tmp_path)
    outside = tmp_path / ".scenario-state"

    with pytest.raises(UnsafePathError, match="repository-local"):
        reset_workspace(repository, manifest, requested_state_root=outside)
