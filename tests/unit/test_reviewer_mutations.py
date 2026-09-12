from pathlib import Path

import pytest

from orchestrator import Stage, verify_event_chain
from runtime.reviewer_mutations import (
    install_reviewer_mutation,
    load_reviewer_mutations,
    seed_reviewer_mutation_candidate,
)
from runtime.scenario_harness import load_manifest, reset_workspace

ROOT = Path(__file__).resolve().parents[2]


def test_reviewer_mutation_corpus_has_required_defects() -> None:
    manifest = load_reviewer_mutations()
    assert {item.id for item in manifest.mutations} == {
        "hardcoded-relation",
        "wildcard-dead-code",
        "nondeterministic-attribution",
        "misleading-test-intent",
    }
    assert all(item.expected_finding for item in manifest.mutations)


@pytest.mark.parametrize(
    "mutation_id",
    [
        "hardcoded-relation",
        "wildcard-dead-code",
        "nondeterministic-attribution",
        "misleading-test-intent",
    ],
)
def test_reviewer_mutation_changes_exactly_one_candidate_artifact(
    mutation_id: str,
) -> None:
    scenario = load_manifest(ROOT, "net-revenue")
    canonical = install_reviewer_mutation(ROOT, "net-revenue", "canonical")
    try:
        mutated = install_reviewer_mutation(ROOT, "net-revenue", mutation_id)
        changed = (
            mutated.model_sha256 != canonical.model_sha256,
            mutated.test_sha256 != canonical.test_sha256,
        )
        assert sum(changed) == 1
        assert mutated.expected_defect is not None
    finally:
        reset_workspace(ROOT, scenario)


def test_seeded_reviewer_mutation_uses_normal_implemented_gates() -> None:
    scenario = load_manifest(ROOT, "net-revenue")
    try:
        candidate = seed_reviewer_mutation_candidate(
            ROOT,
            "net-revenue",
            "hardcoded-relation",
            workflow_id="reviewer-mutation-hardcoded-relation",
        )
        assert candidate.state.stage is Stage.IMPLEMENTED
        verify_event_chain(candidate.events, expected_state=candidate.state)
    finally:
        reset_workspace(ROOT, scenario)


def test_unknown_reviewer_mutation_fails_closed() -> None:
    with pytest.raises(ValueError, match="unknown Reviewer mutation"):
        install_reviewer_mutation(ROOT, "net-revenue", "unknown")
