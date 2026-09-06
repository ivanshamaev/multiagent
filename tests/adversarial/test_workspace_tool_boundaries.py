from pathlib import Path

import pytest

from contracts import ToolRequest
from policies import CapabilityProfile, ToolUsage
from runtime.scenario_harness import parse_manifest, reset_workspace
from runtime.tools import WorkspaceBoundaryError, WorkspaceToolAdapter


def _request(request_id: str, call: dict[str, object]) -> ToolRequest:
    return ToolRequest(
        request_id=request_id,
        task_id="task-workspace",
        actor_id="data-engineer-1",
        role="data-engineer",
        call=call,  # type: ignore[arg-type]
    )


def _adapter(tmp_path: Path) -> tuple[WorkspaceToolAdapter, Path, Path]:
    repository = tmp_path / "repository"
    (repository / "project/models").mkdir(parents=True)
    (repository / "project/models/base.sql").write_text("select 1\n", encoding="utf-8")
    task = repository / "scenarios/adversarial-tool/task.md"
    task.parent.mkdir(parents=True)
    task.write_text("# Adversarial tool\n", encoding="utf-8")
    manifest = parse_manifest(
        {
            "schema_version": 1,
            "id": "adversarial-tool",
            "version": "1.0.0",
            "task_file": "scenarios/adversarial-tool/task.md",
            "source": {
                "commit": "7" * 40,
                "snapshot_paths": ["project"],
                "excluded_names": ["target"],
            },
            "workspace": {
                "editable_paths": ["project/models/**"],
                "required_paths": ["TASK.md", "project/models/base.sql"],
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
                "oracle_sha256": "8" * 64,
            },
        }
    )
    profile = CapabilityProfile(
        profile_id="adversarial-tool-profile",
        role="data-engineer",
        allowed_tools=("workspace.read_file", "workspace.write_file"),
        readable_paths=("TASK.md", "project/**"),
        writable_paths=("project/models/**",),
        max_query_rows=10,
        max_query_chars=1_000,
        max_read_bytes=1_000,
        max_write_bytes=1_000,
        max_tool_calls=5,
        max_wall_time_seconds=60,
        max_output_bytes=10_000,
    )
    reset = reset_workspace(repository, manifest)
    workspace = Path(str(reset["workspace"]))
    return WorkspaceToolAdapter(repository, manifest, profile), repository, workspace


def test_workspace_symlink_is_rejected_before_read(tmp_path: Path) -> None:
    adapter, _, workspace = _adapter(tmp_path)
    (workspace / "project/models/link.sql").symlink_to(workspace / "project/models/base.sql")

    with pytest.raises(WorkspaceBoundaryError):
        adapter.execute(
            _request(
                "read-symlink",
                {"tool": "workspace.read_file", "path": "project/models/link.sql"},
            ),
            ToolUsage(),
        )
    assert (workspace / "project/models/link.sql").is_symlink()


def test_evidence_symlink_cannot_redirect_retained_output(tmp_path: Path) -> None:
    adapter, repository, _ = _adapter(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    evidence = repository / ".scenario-state/evidence"
    evidence.parent.mkdir(exist_ok=True)
    evidence.symlink_to(outside, target_is_directory=True)

    with pytest.raises(WorkspaceBoundaryError, match="evidence path contains a symlink"):
        adapter.execute(
            _request("read-evidence-link", {"tool": "workspace.read_file", "path": "TASK.md"}),
            ToolUsage(),
        )

    assert list(outside.iterdir()) == []
