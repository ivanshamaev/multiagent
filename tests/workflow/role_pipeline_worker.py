"""Subprocess worker used by the real role-pipeline crash/recovery test."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import uuid
from pathlib import Path

from runtime.checkpoints import SecureCheckpointStorage
from runtime.role_pipeline import (
    RolePipelineHandlers,
    build_role_pipeline,
    decode_role_snapshot,
    initial_role_message,
)
from runtime.role_receipts import SecureRoleReceiptStore
from tests.workflow.test_role_pipeline import _handlers, _request


def _atomic_text(path: Path, value: str) -> None:
    temporary = path.with_suffix(f".{uuid.uuid4().hex}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        path.chmod(0o600)
    finally:
        temporary.unlink(missing_ok=True)


def _increment(path: Path) -> None:
    current = int(path.read_text(encoding="utf-8")) if path.exists() else 0
    _atomic_text(path, str(current + 1))


def _instrument(run_dir: Path, pause_role: str) -> RolePipelineHandlers:
    base = _handlers([])

    def wrap(name, stage_handler):
        async def measured(snapshot):
            if name == pause_role:
                _atomic_text(run_dir / f"{name}.entered", "ready")
                while not (run_dir / f"{name}.release").exists():
                    await asyncio.sleep(0.05)
            _increment(run_dir / f"{name}.count")
            return await stage_handler(snapshot)

        return measured

    return RolePipelineHandlers(
        analyst=wrap("analyst", base.analyst),
        pm=wrap("pm", base.pm),
        data_engineer=wrap("data_engineer", base.data_engineer),
        validator=wrap("validator", base.validator),
        qa=wrap("qa", base.qa),
        reviewer=wrap("reviewer", base.reviewer),
    )


def _after_receipt(run_dir: Path, pause_role: str):
    async def hook(executor_id: str, operation_id: str) -> None:
        role = executor_id.removeprefix("role_")
        if role != pause_role:
            return
        _atomic_text(run_dir / f"{role}.receipt-entered", operation_id)
        while not (run_dir / f"{role}.receipt-release").exists():
            await asyncio.sleep(0.05)

    return hook


async def _run(args) -> dict[str, object]:
    storage = SecureCheckpointStorage(args.repository_root, args.run_dir / "checkpoints")
    receipts = SecureRoleReceiptStore(args.repository_root, args.run_dir / "receipts")
    workflow = build_role_pipeline(
        _instrument(args.run_dir, args.pause_role),
        storage,
        receipts,
        after_receipt=_after_receipt(args.run_dir, args.pause_after_receipt),
    )
    result = (
        await workflow.run(checkpoint_id=args.checkpoint_id)
        if args.checkpoint_id
        else await workflow.run(initial_role_message(_request()))
    )
    snapshot = decode_role_snapshot(result.get_outputs()[0])
    return {"stage": snapshot.state.stage.value if snapshot.state else None, "status": "PASS"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--pause-role", default="validator")
    parser.add_argument("--pause-after-receipt", default="")
    parser.add_argument("--checkpoint-id")
    args = parser.parse_args()
    try:
        result = asyncio.run(_run(args))
    except Exception as error:
        print(json.dumps({"error_type": type(error).__name__, "status": "FAIL"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
