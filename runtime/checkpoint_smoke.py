"""Real process-kill and MAF checkpoint-resume proof."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Never

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler

from runtime.checkpoints import SecureCheckpointStorage
from runtime.scenario_harness import REPOSITORY_ROOT

WORKFLOW_NAME = "checkpoint-crash-proof-v1"


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


def _increment(path: Path) -> int:
    value = int(path.read_text(encoding="utf-8")) + 1 if path.exists() else 1
    _atomic_text(path, str(value))
    return value


class StartStage(Executor):
    def __init__(self, run_dir: Path) -> None:
        super().__init__(id="start_stage")
        self.run_dir = run_dir

    @handler
    async def run(self, message: str, ctx: WorkflowContext[str]) -> None:
        _increment(self.run_dir / "start.count")
        await ctx.send_message(f"{message}:committed")


class FinishStage(Executor):
    def __init__(self, run_dir: Path) -> None:
        super().__init__(id="finish_stage")
        self.run_dir = run_dir

    @handler
    async def run(self, message: str, ctx: WorkflowContext[Never, str]) -> None:
        _atomic_text(self.run_dir / "finish.entered", "ready")
        while not (self.run_dir / "finish.release").exists():
            await asyncio.sleep(0.05)
        _increment(self.run_dir / "finish.count")
        await ctx.yield_output(f"{message}:finished")


def _build(run_dir: Path, storage: SecureCheckpointStorage):
    start = StartStage(run_dir)
    finish = FinishStage(run_dir)
    return (
        WorkflowBuilder(
            name=WORKFLOW_NAME,
            start_executor=start,
            checkpoint_storage=storage,
            output_from=[finish],
        )
        .add_edge(start, finish)
        .build()
    )


def _safe_run_dir(repository_root: Path, run_dir: Path) -> Path:
    root = repository_root.resolve(strict=True)
    if run_dir.is_symlink():
        raise RuntimeError("checkpoint smoke directory must not be a symlink")
    resolved = run_dir.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise RuntimeError("checkpoint smoke directory escaped the repository")
    resolved.mkdir(parents=True, exist_ok=True, mode=0o700)
    resolved.chmod(0o700)
    return resolved


async def _worker(
    repository_root: Path, run_dir: Path, checkpoint_id: str | None
) -> dict[str, object]:
    run_dir = _safe_run_dir(repository_root, run_dir)
    storage = SecureCheckpointStorage(repository_root, run_dir / "checkpoints")
    workflow = _build(run_dir, storage)
    result = (
        await workflow.run(checkpoint_id=checkpoint_id)
        if checkpoint_id
        else await workflow.run("task")
    )
    return {"outputs": result.get_outputs(), "status": "PASS"}


async def run_crash_recovery(
    repository_root: Path = REPOSITORY_ROOT,
    state_root: Path | None = None,
    *,
    timeout_seconds: float = 15.0,
) -> dict[str, object]:
    base = state_root or repository_root / ".scenario-state/checkpoint-smoke"
    run_dir = _safe_run_dir(repository_root, base / f"run-{uuid.uuid4().hex[:12]}")
    storage = SecureCheckpointStorage(repository_root, run_dir / "checkpoints")
    command = [
        sys.executable,
        "-m",
        "runtime.checkpoint_smoke",
        "--worker",
        "--repository-root",
        str(repository_root),
        "--run-dir",
        str(run_dir),
    ]
    environment = {"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0"}
    child = subprocess.Popen(
        command,
        cwd=REPOSITORY_ROOT,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + timeout_seconds
    checkpoint_id: str | None = None
    try:
        while time.monotonic() < deadline:
            checkpoints = await storage.list_checkpoints(workflow_name=WORKFLOW_NAME)
            committed = [item for item in checkpoints if item.iteration_count == 1]
            if committed and (run_dir / "finish.entered").exists():
                checkpoint_id = committed[0].checkpoint_id
                break
            if child.poll() is not None:
                raise RuntimeError("checkpoint worker exited before the crash boundary")
            await asyncio.sleep(0.05)
        if checkpoint_id is None:
            raise RuntimeError("checkpoint worker did not reach the crash boundary")
    finally:
        child.kill()
        child.wait(timeout=3)
    _atomic_text(run_dir / "finish.release", "resume")
    resumed = subprocess.run(
        [*command, "--checkpoint-id", checkpoint_id],
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    if resumed.returncode != 0:
        raise RuntimeError("checkpoint resume worker failed")
    payload = json.loads(resumed.stdout.strip().splitlines()[-1])
    start_count = int((run_dir / "start.count").read_text(encoding="utf-8"))
    finish_count = int((run_dir / "finish.count").read_text(encoding="utf-8"))
    if payload.get("outputs") != ["task:committed:finished"]:
        raise RuntimeError("checkpoint resume output is invalid")
    if start_count != 1 or finish_count != 1:
        raise RuntimeError("checkpoint resume repeated a committed stage")
    return {
        "checkpoint_iteration": 1,
        "finish_stage_calls": finish_count,
        "resumed": True,
        "start_stage_calls": start_count,
        "status": "PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--checkpoint-id")
    args = parser.parse_args(argv)
    try:
        if args.worker:
            if args.run_dir is None:
                raise RuntimeError("worker run directory is required")
            result = asyncio.run(_worker(args.repository_root, args.run_dir, args.checkpoint_id))
        else:
            result = asyncio.run(run_crash_recovery(args.repository_root))
    except Exception as error:
        print(json.dumps({"error_type": type(error).__name__, "status": "FAIL"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
