import json
from pathlib import Path

import pytest

from contracts import ToolRequest
from policies import CapabilityProfile, PolicyCode, ToolUsage
from runtime.scenario_harness import parse_manifest, reset_workspace, verify_workspace
from runtime.tools import (
    WorkspaceAuthorizationError,
    WorkspaceBoundaryError,
    WorkspaceToolAdapter,
)


def _fixture(tmp_path: Path) -> tuple[Path, object, CapabilityProfile, Path]:
    repository = tmp_path / "repository"
    (repository / "project/models").mkdir(parents=True)
    (repository / "project/project.yml").write_text("name: fixture\n", encoding="utf-8")
    (repository / "project/models/base.sql").write_text("select 1\n", encoding="utf-8")
    task = repository / "scenarios/workspace-tool/task.md"
    task.parent.mkdir(parents=True)
    task.write_text("# Workspace tool\n", encoding="utf-8")
    manifest = parse_manifest(
        {
            "schema_version": 1,
            "id": "workspace-tool",
            "version": "1.0.0",
            "task_file": "scenarios/workspace-tool/task.md",
            "source": {
                "commit": "5" * 40,
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
                "oracle_sha256": "6" * 64,
            },
        }
    )
    profile = CapabilityProfile(
        profile_id="workspace-tool-profile",
        role="data-engineer",
        allowed_tools=("workspace.read_file", "workspace.write_file"),
        readable_paths=("TASK.md", "project/**"),
        writable_paths=("project/models/**",),
        allowed_databases=(),
        max_query_rows=10,
        max_query_chars=1_000,
        max_read_bytes=1_000,
        max_write_bytes=1_000,
        max_tool_calls=5,
        max_wall_time_seconds=60,
        max_output_bytes=10_000,
    )
    result = reset_workspace(repository, manifest)
    return repository, manifest, profile, Path(str(result["workspace"]))


def _request(request_id: str, call: dict[str, object]) -> ToolRequest:
    return ToolRequest(
        request_id=request_id,
        task_id="task-workspace",
        actor_id="data-engineer-1",
        role="data-engineer",
        call=call,  # type: ignore[arg-type]
    )


def test_workspace_read_returns_content_addressed_retained_result(tmp_path: Path) -> None:
    repository, manifest, profile, _ = _fixture(tmp_path)
    adapter = WorkspaceToolAdapter(repository, manifest, profile)

    result = adapter.execute(
        _request("read-task", {"tool": "workspace.read_file", "path": "TASK.md"}),
        ToolUsage(),
    )

    assert result.content == "# Workspace tool\n"
    assert result.evidence.output is not None
    retained = repository / result.evidence.output.path
    assert retained.read_bytes() == result.content.encode("utf-8")
    assert retained.stat().st_mode & 0o777 == 0o600
    assert result.evidence.arguments_sha256 not in result.content


def test_workspace_write_is_atomic_and_reports_pre_post_hashes(tmp_path: Path) -> None:
    repository, manifest, profile, workspace = _fixture(tmp_path)
    adapter = WorkspaceToolAdapter(repository, manifest, profile)
    call = {
        "tool": "workspace.write_file",
        "path": "project/models/marts/fct_example.sql",
        "content": "select 2\n",
    }

    first = adapter.execute(_request("write-first", call), ToolUsage())
    second = adapter.execute(_request("write-second", call), ToolUsage(completed_calls=1))
    first_metadata = json.loads(first.content)
    second_metadata = json.loads(second.content)

    assert first_metadata["changed"] is True
    assert first_metadata["previous_sha256"] is None
    assert second_metadata["changed"] is False
    assert second_metadata["previous_sha256"] == second_metadata["sha256"]
    assert (workspace / "project/models/marts/fct_example.sql").read_text() == "select 2\n"
    assert verify_workspace(repository, manifest)["ok"]


def test_workspace_adapter_reauthorizes_paths_and_remaining_output_budget(tmp_path: Path) -> None:
    repository, manifest, profile, _ = _fixture(tmp_path)
    adapter = WorkspaceToolAdapter(repository, manifest, profile)

    with pytest.raises(WorkspaceAuthorizationError) as protected:
        adapter.execute(
            _request(
                "write-protected",
                {
                    "tool": "workspace.write_file",
                    "path": "project/project.yml",
                    "content": "tampered\n",
                },
            ),
            ToolUsage(),
        )
    with pytest.raises(WorkspaceAuthorizationError) as exhausted:
        adapter.execute(
            _request("read-no-budget", {"tool": "workspace.read_file", "path": "TASK.md"}),
            ToolUsage(output_bytes=9_995),
        )

    assert protected.value.decision.code is PolicyCode.PATH_DENIED
    assert exhausted.value.decision.code is PolicyCode.BUDGET_DENIED


def test_workspace_adapter_rejects_profile_broader_than_manifest(tmp_path: Path) -> None:
    repository, manifest, profile, _ = _fixture(tmp_path)
    payload = profile.model_dump()
    payload["writable_paths"] = ("project/**",)
    broader = CapabilityProfile.model_validate(payload)

    with pytest.raises(WorkspaceBoundaryError, match="write scope"):
        WorkspaceToolAdapter(repository, manifest, broader)


def test_failed_atomic_replace_preserves_existing_file(tmp_path: Path, monkeypatch) -> None:
    repository, manifest, profile, workspace = _fixture(tmp_path)
    adapter = WorkspaceToolAdapter(repository, manifest, profile)
    target = workspace / "project/models/base.sql"

    def fail_replace(source, destination) -> None:
        raise OSError("synthetic replace failure")

    monkeypatch.setattr("runtime.tools.workspace.os.replace", fail_replace)
    with pytest.raises(OSError, match="synthetic"):
        adapter.execute(
            _request(
                "failed-replace",
                {
                    "tool": "workspace.write_file",
                    "path": "project/models/base.sql",
                    "content": "select 999\n",
                },
            ),
            ToolUsage(),
        )

    assert target.read_text(encoding="utf-8") == "select 1\n"
    assert list(target.parent.glob(".agent-write-*")) == []
