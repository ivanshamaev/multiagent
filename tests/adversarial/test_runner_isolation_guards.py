from pathlib import Path

import pytest

from runtime.mcp_auth import MCPAuthenticationError, MCPKeyStore
from runtime.runner_isolation import IsolatedRunner, RunnerIsolationError, load_runner_profile

ROOT = Path(__file__).resolve().parents[2]


def test_runner_rejects_workspace_escape_and_symlink(tmp_path: Path) -> None:
    profile = load_runner_profile(ROOT, "analyst_v1.json")
    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(RunnerIsolationError, match="escaped"):
        IsolatedRunner(ROOT, profile, outside)

    managed = ROOT / ".scenario-state" / "workspaces"
    managed.mkdir(parents=True, exist_ok=True)
    link = managed / "step22-hostile-link"
    if link.exists() or link.is_symlink():
        pytest.fail("hostile runner test path already exists")
    link.symlink_to(outside, target_is_directory=True)
    try:
        with pytest.raises(RunnerIsolationError, match="symlink"):
            IsolatedRunner(ROOT, profile, link)
    finally:
        link.unlink()


def test_runner_rejects_symlink_inside_readable_workspace_path(tmp_path: Path) -> None:
    profile = load_runner_profile(ROOT, "analyst_v1.json")
    managed = ROOT / ".scenario-state" / "workspaces"
    workspace = managed / "step22-hostile-readable"
    target = tmp_path / "models"
    target.mkdir()
    workspace.mkdir(parents=True)
    (workspace / "TASK.md").write_text("task", encoding="utf-8")
    platform = workspace / "platform/dbt"
    platform.mkdir(parents=True)
    (platform / "models").symlink_to(target, target_is_directory=True)
    try:
        runner = IsolatedRunner(ROOT, profile, workspace)
        with pytest.raises(RunnerIsolationError, match="symlink"):
            runner.command(("/usr/bin/python3", "-I", "-c", "print('{}')"))
    finally:
        (platform / "models").unlink()
        platform.rmdir()
        (workspace / "platform").rmdir()
        (workspace / "TASK.md").unlink()
        workspace.rmdir()


def test_key_store_rejects_escape_symlink_and_loose_mode(tmp_path: Path) -> None:
    with pytest.raises(MCPAuthenticationError, match="escaped"):
        MCPKeyStore(tmp_path, tmp_path.parent / "outside-keyring.json")

    private = tmp_path / "private"
    private.mkdir(mode=0o700)
    target = private / "target.json"
    target.touch(mode=0o600)
    link = private / "link.json"
    link.symlink_to(target)
    with pytest.raises(MCPAuthenticationError, match="symlink"):
        MCPKeyStore(tmp_path, link)

    shared = tmp_path / "shared"
    shared.mkdir(mode=0o755)
    shared.chmod(0o755)
    with pytest.raises(MCPAuthenticationError, match="0700"):
        MCPKeyStore(tmp_path, shared / "keyring.json")
