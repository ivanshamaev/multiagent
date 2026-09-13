import json
from hashlib import sha256
from pathlib import Path

import pytest

from runtime.role_receipts import (
    RoleReceipt,
    RoleReceiptError,
    SecureRoleReceiptStore,
    role_operation_id,
)


def _receipt(output: str = '{"stage":"done"}') -> RoleReceipt:
    operation_id = role_operation_id(
        workflow_id="workflow-receipt",
        executor_id="role_data_engineer",
        input_revision=4,
        input_payload="input",
    )
    return RoleReceipt(
        operation_id=operation_id,
        workflow_id="workflow-receipt",
        executor_id="role_data_engineer",
        input_revision=4,
        input_sha256=sha256(b"input").hexdigest(),
        output_sha256=sha256(output.encode()).hexdigest(),
        output=output,
    )


def test_receipt_round_trip_is_owner_only_and_same_value_is_idempotent(tmp_path: Path) -> None:
    store = SecureRoleReceiptStore(tmp_path, tmp_path / "receipts")
    receipt = _receipt()
    store.save(receipt)
    store.save(receipt)

    assert store.get(receipt.operation_id) == receipt
    assert store.storage_path.stat().st_mode & 0o777 == 0o700
    assert (store.storage_path / f"{receipt.operation_id}.json").stat().st_mode & 0o777 == 0o600


def test_receipt_store_rejects_escape_symlink_and_loose_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir(mode=0o700)
    with pytest.raises(RoleReceiptError, match="escaped"):
        SecureRoleReceiptStore(tmp_path, outside / "receipts")

    linked = tmp_path / "linked"
    linked.symlink_to(outside, target_is_directory=True)
    with pytest.raises(RoleReceiptError, match="symlink"):
        SecureRoleReceiptStore(tmp_path, linked / "receipts")

    loose = tmp_path / "loose"
    loose.mkdir(mode=0o755)
    with pytest.raises(RoleReceiptError, match="0700"):
        SecureRoleReceiptStore(tmp_path, loose)


def test_receipt_load_rejects_corruption_mode_and_collision(tmp_path: Path) -> None:
    store = SecureRoleReceiptStore(tmp_path, tmp_path / "receipts")
    receipt = _receipt()
    store.save(receipt)
    path = store.storage_path / f"{receipt.operation_id}.json"

    alternate = _receipt('{"stage":"blocked"}')
    with pytest.raises(RoleReceiptError, match="collision"):
        store.save(alternate)

    path.chmod(0o644)
    with pytest.raises(RoleReceiptError, match="0600"):
        store.get(receipt.operation_id)
    path.chmod(0o600)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["output"] = '{"stage":"tampered"}'
    path.write_text(json.dumps(payload), encoding="utf-8")
    path.chmod(0o600)
    with pytest.raises(RoleReceiptError, match="hash"):
        store.get(receipt.operation_id)
