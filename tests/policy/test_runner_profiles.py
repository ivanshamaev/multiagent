import json
from pathlib import Path

from policies import load_capability_profile
from runtime.runner_isolation import RUNNER_PROFILE_NAMES, load_all_runner_profiles

ROOT = Path(__file__).resolve().parents[2]


def test_runner_profiles_cover_exact_business_roles_and_no_network_setting() -> None:
    profiles = load_all_runner_profiles(ROOT)

    assert set(RUNNER_PROFILE_NAMES) == {
        "analyst_v1.json",
        "pm_v1.json",
        "data_engineer_v1.json",
        "qa_v1.json",
        "reviewer_v1.json",
    }
    assert {item.runner.role for item in profiles} == {
        "analyst",
        "pm",
        "data-engineer",
        "qa",
        "reviewer",
    }
    for name in RUNNER_PROFILE_NAMES:
        payload = json.loads((ROOT / "policies/runner_profiles" / name).read_text())
        assert set(payload) == {
            "schema_version",
            "runner_id",
            "actor_id",
            "role",
            "namespace_uid",
            "capability_profile",
            "max_input_bytes",
            "max_output_bytes",
            "timeout_seconds",
        }


def test_runner_write_mounts_derive_only_from_existing_capability_policy() -> None:
    profiles = load_all_runner_profiles(ROOT)
    by_role = {item.runner.role: item for item in profiles}

    assert by_role["pm"].capability is None
    for role in ("analyst", "qa", "reviewer"):
        assert by_role[role].capability.writable_paths == ()  # type: ignore[union-attr]
    de = load_capability_profile(ROOT / "policies/profiles/data_engineer_v1.json")
    assert by_role["data-engineer"].capability == de
    assert de.writable_paths == ("platform/dbt/models/**", "platform/dbt/tests/**")
