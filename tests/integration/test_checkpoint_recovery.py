import asyncio
from pathlib import Path

import pytest
from agent_framework import WorkflowCheckpoint
from agent_framework.exceptions import WorkflowCheckpointException

from runtime.checkpoint_smoke import WORKFLOW_NAME, _build, run_crash_recovery
from runtime.checkpoints import SecureCheckpointStorage


def test_real_process_kill_resumes_after_committed_stage(tmp_path: Path) -> None:
    result = asyncio.run(
        run_crash_recovery(
            tmp_path,
            tmp_path / ".scenario-state/checkpoint-smoke",
            timeout_seconds=10,
        )
    )

    assert result == {
        "checkpoint_iteration": 1,
        "finish_stage_calls": 1,
        "resumed": True,
        "start_stage_calls": 1,
        "status": "PASS",
    }


def test_resume_rejects_incompatible_graph_signature(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir(mode=0o700)
    storage = SecureCheckpointStorage(tmp_path, run_dir / "checkpoints")
    checkpoint = WorkflowCheckpoint(
        workflow_name=WORKFLOW_NAME,
        graph_signature_hash="0" * 64,
    )
    checkpoint_id = asyncio.run(storage.save(checkpoint))
    workflow = _build(run_dir, storage)

    with pytest.raises(WorkflowCheckpointException, match="graph has changed"):
        asyncio.run(workflow.run(checkpoint_id=checkpoint_id))
