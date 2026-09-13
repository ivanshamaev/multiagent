import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from runtime.checkpoints import SecureCheckpointStorage
from runtime.role_pipeline import ROLE_PIPELINE_NAME

ROLES = ("analyst", "pm", "data_engineer", "validator", "qa", "reviewer")


def test_new_process_resumes_after_data_engineer_without_repeating_completed_roles(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "role-recovery"
    run_dir.mkdir(mode=0o700)
    storage = SecureCheckpointStorage(tmp_path, run_dir / "checkpoints")
    base_command = [
        sys.executable,
        "-m",
        "tests.workflow.role_pipeline_worker",
        "--repository-root",
        str(tmp_path),
        "--run-dir",
        str(run_dir),
        "--pause-role",
        "validator",
    ]
    environment = {"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0"}
    child = subprocess.Popen(
        base_command,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    checkpoint_id = None
    deadline = time.monotonic() + 15
    try:
        while time.monotonic() < deadline:
            checkpoints = asyncio.run(storage.list_checkpoints(workflow_name=ROLE_PIPELINE_NAME))
            committed = [item for item in checkpoints if item.iteration_count == 3]
            if committed and (run_dir / "validator.entered").exists():
                checkpoint_id = committed[0].checkpoint_id
                break
            if child.poll() is not None:
                raise RuntimeError("role worker exited before the crash boundary")
            time.sleep(0.05)
    finally:
        child.kill()
        child.wait(timeout=3)
    assert checkpoint_id is not None

    (run_dir / "validator.release").write_text("resume", encoding="utf-8")
    resumed = subprocess.run(
        [*base_command, "--checkpoint-id", checkpoint_id],
        env=environment,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert resumed.returncode == 0, resumed.stderr
    assert json.loads(resumed.stdout.strip().splitlines()[-1]) == {
        "stage": "done",
        "status": "PASS",
    }
    assert {
        role: int((run_dir / f"{role}.count").read_text(encoding="utf-8")) for role in ROLES
    } == {role: 1 for role in ROLES}
