import asyncio
import json
import os
from pathlib import Path

import pytest
from agent_framework import FileCheckpointStorage, WorkflowCheckpoint
from agent_framework.exceptions import WorkflowCheckpointException

from runtime.checkpoints import SecureCheckpointStorage


def _checkpoint() -> WorkflowCheckpoint:
    return WorkflowCheckpoint(
        workflow_name="unit-workflow",
        graph_signature_hash="a" * 64,
        messages={},
        state={"value": 1},
    )


def test_checkpoint_round_trip_is_owner_only(tmp_path: Path) -> None:
    storage = SecureCheckpointStorage(tmp_path)
    checkpoint = _checkpoint()

    checkpoint_id = asyncio.run(storage.save(checkpoint))
    loaded = asyncio.run(storage.load(checkpoint_id))

    assert loaded.state == {"value": 1}
    assert storage.storage_path.stat().st_mode & 0o777 == 0o700
    assert (storage.storage_path / f"{checkpoint_id}.json").stat().st_mode & 0o777 == 0o600


def test_checkpoint_storage_rejects_escape_symlink_and_loose_mode(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    with pytest.raises(WorkflowCheckpointException, match="escaped"):
        SecureCheckpointStorage(tmp_path, outside)
    link = tmp_path / "linked"
    link.symlink_to(outside, target_is_directory=True)
    with pytest.raises(WorkflowCheckpointException, match="symlink"):
        SecureCheckpointStorage(tmp_path, link)
    inside = tmp_path / "inside"
    inside.mkdir()
    parent_link = tmp_path / "parent-link"
    parent_link.symlink_to(inside, target_is_directory=True)
    with pytest.raises(WorkflowCheckpointException, match="symlink"):
        SecureCheckpointStorage(tmp_path, parent_link / "checkpoints")
    loose = tmp_path / "loose"
    loose.mkdir(mode=0o755)
    with pytest.raises(WorkflowCheckpointException, match="0700"):
        SecureCheckpointStorage(tmp_path, loose)


def test_checkpoint_load_rejects_id_mode_and_malformed_payload(tmp_path: Path) -> None:
    storage = SecureCheckpointStorage(tmp_path)
    with pytest.raises(WorkflowCheckpointException, match="ID"):
        asyncio.run(storage.load("../../escape"))
    checkpoint = _checkpoint()
    checkpoint_id = asyncio.run(storage.save(checkpoint))
    path = storage.storage_path / f"{checkpoint_id}.json"
    path.chmod(0o644)
    with pytest.raises(WorkflowCheckpointException, match="0600"):
        asyncio.run(storage.load(checkpoint_id))
    path.chmod(0o600)
    path.write_text(json.dumps({"not": "a checkpoint"}), encoding="utf-8")
    os.chmod(path, 0o600)
    with pytest.raises(WorkflowCheckpointException):
        asyncio.run(storage.load(checkpoint_id))


def test_checkpoint_save_is_create_only(tmp_path: Path) -> None:
    storage = SecureCheckpointStorage(tmp_path)
    checkpoint = _checkpoint()
    asyncio.run(storage.save(checkpoint))

    with pytest.raises(WorkflowCheckpointException, match="already exists"):
        asyncio.run(storage.save(checkpoint))


def test_reader_never_sees_checkpoint_before_owner_only_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    storage = SecureCheckpointStorage(tmp_path)
    checkpoint = _checkpoint()
    original = FileCheckpointStorage.save
    observed = []

    async def inspect_before_publication(delegate, value):
        checkpoint_id = await original(delegate, value)
        observed.append(await storage.list_checkpoint_ids(workflow_name="unit-workflow"))
        assert not (storage.storage_path / f"{checkpoint_id}.json").exists()
        return checkpoint_id

    monkeypatch.setattr(FileCheckpointStorage, "save", inspect_before_publication)
    checkpoint_id = asyncio.run(storage.save(checkpoint))
    assert observed == [[]]
    assert (storage.storage_path / f"{checkpoint_id}.json").stat().st_mode & 0o777 == 0o600
    listed = asyncio.run(storage.list_checkpoint_ids(workflow_name="unit-workflow"))
    assert listed == [checkpoint_id]
    assert not list(storage.storage_path.glob(".pending-*"))
