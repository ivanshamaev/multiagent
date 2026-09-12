from pathlib import Path

import pytest

from orchestrator import Stage, verify_event_chain
from runtime.qa_mutations import (
    install_qa_mutation,
    load_qa_mutations,
    seed_mutation_candidate,
)
from runtime.scenario_harness import load_manifest, reset_workspace

ROOT = Path(__file__).resolve().parents[2]


def test_mutation_corpus_has_required_independent_defects() -> None:
    manifest = load_qa_mutations()

    assert {item.id for item in manifest.mutations} == {
        "refund-date",
        "attribution",
        "split-payments",
        "duplicate-attribution",
        "weakened-test",
    }
    assert all(item.expected_defect for item in manifest.mutations)


def test_mutation_installer_changes_exactly_one_target_and_rejects_unknown() -> None:
    scenario = load_manifest(ROOT, "net-revenue")
    canonical = install_qa_mutation(ROOT, "net-revenue", "canonical")
    try:
        mutated = install_qa_mutation(ROOT, "net-revenue", "refund-date")

        assert mutated.model_sha256 != canonical.model_sha256
        assert mutated.test_sha256 == canonical.test_sha256
        assert mutated.expected_defect is not None
        with pytest.raises(ValueError, match="unknown QA mutation"):
            install_qa_mutation(ROOT, "net-revenue", "unknown")
    finally:
        reset_workspace(ROOT, scenario)


def test_mutation_candidate_enters_implemented_through_normal_event_gates() -> None:
    scenario = load_manifest(ROOT, "net-revenue")
    try:
        candidate = seed_mutation_candidate(
            ROOT,
            "net-revenue",
            "attribution",
            workflow_id="qa-mutation-attribution",
        )

        assert candidate.state.stage is Stage.IMPLEMENTED
        assert candidate.state.implementation_author_id == "mutation-harness"
        assert candidate.state.budgets.used.model_tokens == 0
        verify_event_chain(candidate.events, expected_state=candidate.state)
    finally:
        reset_workspace(ROOT, scenario)


@pytest.mark.parametrize(
    "mutation_id",
    [
        "canonical",
        "refund-date",
        "attribution",
        "split-payments",
        "duplicate-attribution",
        "weakened-test",
    ],
)
def test_mutation_installer_changes_only_disposable_candidate(
    mutation_id: str,
) -> None:
    scenario = load_manifest(ROOT, "net-revenue")
    try:
        installed = install_qa_mutation(ROOT, "net-revenue", mutation_id)
        assert installed.workspace.is_relative_to(ROOT / ".scenario-state/workspaces")
        assert (installed.workspace / "platform/dbt/models/marts/fct_net_revenue.sql").is_file()
        assert (
            installed.workspace / "platform/dbt/tests/assert_fct_net_revenue_contract.sql"
        ).is_file()
        assert len(installed.model_sha256) == 64
        assert len(installed.test_sha256) == 64
    finally:
        reset_workspace(ROOT, scenario)


def test_unknown_mutation_fails_closed() -> None:
    with pytest.raises(ValueError, match="unknown QA mutation"):
        install_qa_mutation(ROOT, "net-revenue", "not-a-mutation")
