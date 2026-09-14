from pathlib import Path

import pytest

from runtime.runner_isolation import (
    IsolatedRunner,
    RunnerIsolationError,
    load_all_runner_profiles,
    load_runner_profile,
)

ROOT = Path(__file__).resolve().parents[2]


def test_runner_profiles_have_distinct_identity_and_matching_capabilities() -> None:
    profiles = load_all_runner_profiles(ROOT)

    assert [item.runner.role for item in profiles] == [
        "analyst",
        "pm",
        "data-engineer",
        "qa",
        "reviewer",
    ]
    assert len({item.runner.runner_id for item in profiles}) == 5
    assert len({item.runner.actor_id for item in profiles}) == 5
    assert len({item.runner.namespace_uid for item in profiles}) == 5
    assert profiles[1].capability is None
    assert all(
        item.capability is None or item.capability.role == item.runner.role for item in profiles
    )


def test_pm_runner_has_no_workspace_and_command_is_fail_closed() -> None:
    profile = load_runner_profile(ROOT, "pm_v1.json")
    runner = IsolatedRunner(ROOT, profile, None)
    command = runner.command(("/usr/bin/python3", "-I", "-c", "print('{}')"))

    assert "--unshare-all" in command
    assert "--clearenv" in command
    assert "--cap-drop" in command
    assert "--no-new-privs" in command
    assert "/workspace" not in command
    assert str(ROOT) not in command
    with pytest.raises(RunnerIsolationError, match="isolated system Python"):
        runner.command(("/bin/sh", "-c", "id"))
    with pytest.raises(RunnerIsolationError, match="must not receive"):
        IsolatedRunner(ROOT, profile, ROOT)


def test_runner_rejects_unknown_profile_name() -> None:
    with pytest.raises(RunnerIsolationError, match="not allowlisted"):
        load_runner_profile(ROOT, "../data_engineer_v1.json")
