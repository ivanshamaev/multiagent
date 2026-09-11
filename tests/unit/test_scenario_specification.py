import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts import ScenarioSpecification
from runtime.scenario_harness import load_manifest, reset_workspace
from runtime.specification import SpecificationBoundaryError, load_scenario_specification

ROOT = Path(__file__).resolve().parents[2]


def test_net_revenue_specification_is_frozen_human_authored_and_complete() -> None:
    envelope = ScenarioSpecification.model_validate_json(
        (ROOT / "scenarios/net-revenue/specification.json").read_bytes()
    )

    assert envelope.specification.producer_id == "human"
    assert envelope.specification.decision.value == "ready"
    assert envelope.specification.dimensions == (
        "order_date",
        "country",
        "acquisition_channel",
        "currency",
    )
    assert len(envelope.specification.acceptance_criteria) == 8
    with pytest.raises(ValidationError, match="frozen"):
        envelope.scenario_id = "other"  # type: ignore[misc]


def test_specification_identity_and_authorship_are_not_model_controlled() -> None:
    payload = json.loads(
        (ROOT / "scenarios/net-revenue/specification.json").read_text(encoding="utf-8")
    )

    for field, value, message in (
        ("producer_id", "data-engineer", "human-authored"),
        ("artifact_id", "model-selected-id", "canonical"),
        ("task_id", "other-task", "scenario"),
    ):
        changed = json.loads(json.dumps(payload))
        changed["specification"][field] = value
        with pytest.raises(ValidationError, match=message):
            ScenarioSpecification.model_validate(changed)


def test_loader_binds_verified_workspace_specification_to_task() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset_workspace(ROOT, manifest)

    loaded = load_scenario_specification(ROOT, "net-revenue")

    assert loaded.scenario_id == "net-revenue"
    assert loaded.task_sha256 == (
        "96e0032a580675be21ef64a798dc7c5a2daa92c9fbf38802e9f51976fa59b924"
    )


def test_loader_rejects_protected_specification_tampering() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset = reset_workspace(ROOT, manifest)
    workspace = Path(str(reset["workspace"]))
    specification = workspace / "scenarios/net-revenue/specification.json"
    specification.write_text("{}\n", encoding="utf-8")

    try:
        with pytest.raises(SpecificationBoundaryError, match="protected workspace paths changed"):
            load_scenario_specification(ROOT, "net-revenue")
    finally:
        reset_workspace(ROOT, manifest)
