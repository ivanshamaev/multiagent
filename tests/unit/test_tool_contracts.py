from datetime import UTC, datetime, timedelta
from hashlib import sha256

import pytest
from pydantic import ValidationError

from contracts import (
    ArtifactReference,
    ToolCallEvidence,
    ToolCallStatus,
    ToolRequest,
    WorkspaceWriteCall,
    tool_arguments_sha256,
)


def _at(second: int) -> datetime:
    return datetime(2026, 9, 6, 9, 0, second, tzinfo=UTC)


def _artifact(contents: bytes = b"bounded output") -> ArtifactReference:
    return ArtifactReference(
        path=".evidence/tool-output.json",
        sha256=sha256(contents).hexdigest(),
        media_type="application/json",
        size_bytes=len(contents),
    )


def _success_evidence() -> ToolCallEvidence:
    artifact = _artifact()
    return ToolCallEvidence(
        evidence_id="tool-evidence-1",
        request_id="request-1",
        task_id="task-1",
        producer_id="tool-runtime",
        tool="clickhouse.run_query",
        arguments_sha256="a" * 64,
        started_at=_at(0),
        completed_at=_at(1),
        status=ToolCallStatus.SUCCESS,
        exit_code=0,
        duration_ms=12,
        output_bytes=artifact.size_bytes,
        output=artifact,
    )


def test_tool_request_uses_closed_discriminated_contract() -> None:
    request = ToolRequest(
        request_id="request-1",
        task_id="task-1",
        actor_id="data-engineer-1",
        role="data-engineer",
        call={"tool": "workspace.read_file", "path": "TASK.md"},
    )

    assert request.call.tool == "workspace.read_file"
    with pytest.raises(ValidationError, match="frozen"):
        request.role = "admin"  # type: ignore[misc]
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ToolRequest.model_validate({**request.model_dump(), "environment": {"TOKEN": "x"}})


@pytest.mark.parametrize(
    "call",
    [
        {"tool": "shell.exec", "command": "id"},
        {"tool": "workspace.read_file", "path": "../.env"},
        {"tool": "workspace.write_file", "path": "/tmp/model.sql", "content": "select 1"},
        {"tool": "clickhouse.run_query", "query": "x" * 20_001},
        {"tool": "clickhouse.list_tables", "database": "raw; DROP TABLE raw.orders"},
    ],
)
def test_tool_request_rejects_unknown_or_unsafe_arguments(call: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ToolRequest(
            request_id="request-1",
            task_id="task-1",
            actor_id="data-engineer-1",
            role="data-engineer",
            call=call,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "selector",
    ["--profiles-dir /tmp", "tag:daily; id", "tag:daily$(id)", "tag:daily\n--debug"],
)
def test_dbt_selector_rejects_option_and_shell_injection(selector: str) -> None:
    with pytest.raises(ValidationError, match=r"selector|options"):
        ToolRequest(
            request_id="request-1",
            task_id="task-1",
            actor_id="data-engineer-1",
            role="data-engineer",
            call={
                "tool": "dbt.build",
                "node_selection": selector,
            },
        )


def test_workspace_write_preserves_content_and_hashes_only_normalized_arguments() -> None:
    first = WorkspaceWriteCall(
        path="platform/dbt/models/example.sql",
        content="  select 1\n",
    )
    same = WorkspaceWriteCall(
        path="platform/dbt/models/example.sql",
        content="  select 1\n",
    )
    changed = WorkspaceWriteCall(
        path="platform/dbt/models/example.sql",
        content="select 2\n",
    )

    assert first.content == "  select 1\n"
    assert tool_arguments_sha256(first) == tool_arguments_sha256(same)
    assert tool_arguments_sha256(first) != tool_arguments_sha256(changed)
    assert len(tool_arguments_sha256(first)) == 64


def test_tool_evidence_requires_consistent_status_output_and_timestamps() -> None:
    evidence = _success_evidence()

    assert evidence.status is ToolCallStatus.SUCCESS
    for update, message in [
        ({"exit_code": 1}, "successful"),
        ({"output_bytes": evidence.output_bytes + 1}, "size"),
        ({"completed_at": evidence.started_at - timedelta(seconds=1)}, "before"),
        ({"status": "error", "exit_code": 0, "error_type": "ProcessError"}, "non-zero"),
    ]:
        with pytest.raises(ValidationError, match=message):
            ToolCallEvidence.model_validate({**evidence.model_dump(), **update})


def test_denial_evidence_never_contains_process_output() -> None:
    denied = ToolCallEvidence(
        evidence_id="tool-evidence-denied",
        request_id="request-1",
        task_id="task-1",
        producer_id="tool-runtime",
        tool="workspace.read_file",
        arguments_sha256="b" * 64,
        started_at=_at(0),
        completed_at=_at(0),
        status="denied",
        duration_ms=0,
        output_bytes=0,
        error_type="path_denied",
    )

    assert denied.exit_code is None
    assert denied.output is None
