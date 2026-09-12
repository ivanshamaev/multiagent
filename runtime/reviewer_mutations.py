"""Independent maintainability mutations for Reviewer false-approval evaluation."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from pydantic import Field, model_validator

from contracts.common import FrozenModel, Identifier, NonEmptyText
from orchestrator import BudgetLimits
from runtime.qa_mutations import (
    MODEL_TARGET,
    TEST_TARGET,
    InstalledMutation,
    MutationCandidateWorkflow,
    _atomic_write,
    install_qa_mutation,
    seed_installed_candidate,
)

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "tests/fixtures/reviewer_mutants"


class ReviewerMutation(FrozenModel):
    id: Identifier
    target: str = Field(pattern="^(model|test)$")
    old: NonEmptyText
    new: NonEmptyText
    expected_finding: NonEmptyText


class ReviewerMutationManifest(FrozenModel):
    schema_version: int = Field(ge=1, le=1)
    mutations: tuple[ReviewerMutation, ...] = Field(min_length=4, max_length=32)

    @model_validator(mode="after")
    def unique_ids(self):
        ids = [item.id for item in self.mutations]
        if len(ids) != len(set(ids)):
            raise ValueError("Reviewer mutation IDs must be unique")
        return self


def load_reviewer_mutations() -> ReviewerMutationManifest:
    path = FIXTURE_ROOT / "manifest.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 100_000:
        raise RuntimeError("Reviewer mutation manifest is not a bounded regular file")
    return ReviewerMutationManifest.model_validate(json.loads(path.read_text(encoding="utf-8")))


def install_reviewer_mutation(
    repository_root: Path,
    scenario_id: str,
    mutation_id: str = "canonical",
) -> InstalledMutation:
    """Install exactly one review mutation over the independently fixed canonical fixture."""

    canonical = install_qa_mutation(repository_root, scenario_id, "canonical")
    if mutation_id == "canonical":
        return canonical.model_copy(update={"mutation_id": "canonical"})
    candidates = {item.id: item for item in load_reviewer_mutations().mutations}
    if mutation_id not in candidates:
        raise ValueError("unknown Reviewer mutation")
    mutation = candidates[mutation_id]
    target_relative = MODEL_TARGET if mutation.target == "model" else TEST_TARGET
    target = canonical.workspace / target_relative
    original = target.read_text(encoding="utf-8")
    if original.count(mutation.old) != 1:
        raise RuntimeError("Reviewer mutation source marker is not unique")
    changed = original.replace(mutation.old, mutation.new, 1)
    _atomic_write(target, changed)
    model = (canonical.workspace / MODEL_TARGET).read_bytes()
    test = (canonical.workspace / TEST_TARGET).read_bytes()
    return InstalledMutation(
        mutation_id=mutation.id,
        expected_defect=mutation.expected_finding,
        workspace=canonical.workspace,
        model_sha256=sha256(model).hexdigest(),
        test_sha256=sha256(test).hexdigest(),
    )


def seed_reviewer_mutation_candidate(
    repository_root: Path,
    scenario_id: str,
    mutation_id: str,
    *,
    workflow_id: str,
    budget_limits: BudgetLimits | None = None,
) -> MutationCandidateWorkflow:
    installed = install_reviewer_mutation(repository_root, scenario_id, mutation_id)
    return seed_installed_candidate(
        repository_root,
        scenario_id,
        installed,
        workflow_id=workflow_id,
        budget_limits=budget_limits,
    )
