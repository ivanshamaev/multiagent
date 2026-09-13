"""Deterministic mutation corpus installer for QA evaluation only."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from pydantic import Field, model_validator

from contracts import (
    ArtifactReference,
    Evidence,
    EvidenceKind,
    ImplementationResult,
    ImplementationStatus,
)
from contracts.common import FrozenModel, Identifier, NonEmptyText
from orchestrator import (
    BudgetLimits,
    Stage,
    TransitionCommand,
    WorkflowEvent,
    WorkflowState,
    append_transition,
)
from runtime.data_engineer import prepare_data_engineer_request, seed_data_engineer_state
from runtime.scenario_harness import load_manifest, reset_workspace

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "tests/fixtures/qa_mutants"
MODEL_TARGET = "platform/dbt/models/marts/fct_net_revenue.sql"
TEST_TARGET = "platform/dbt/tests/assert_fct_net_revenue_contract.sql"


class QAMutation(FrozenModel):
    id: Identifier
    target: str = Field(pattern="^(model|test)$")
    old: NonEmptyText
    new: NonEmptyText
    expected_defect: NonEmptyText


class QAMutationManifest(FrozenModel):
    schema_version: int = Field(ge=1, le=1)
    mutations: tuple[QAMutation, ...] = Field(min_length=5, max_length=32)

    @model_validator(mode="after")
    def unique_ids(self):
        ids = [item.id for item in self.mutations]
        if len(ids) != len(set(ids)):
            raise ValueError("QA mutation IDs must be unique")
        return self


class InstalledMutation(FrozenModel):
    mutation_id: Identifier
    expected_defect: NonEmptyText | None = None
    workspace: Path
    model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    test_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class MutationCandidateWorkflow(FrozenModel):
    installed: InstalledMutation
    state: WorkflowState
    events: tuple[WorkflowEvent, ...]


def load_qa_mutations() -> QAMutationManifest:
    path = FIXTURE_ROOT / "manifest.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 100_000:
        raise RuntimeError("QA mutation manifest is not a bounded regular file")
    return QAMutationManifest.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _read_fixture(name: str) -> str:
    path = FIXTURE_ROOT / name
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 100_000:
        raise RuntimeError("QA mutation fixture is not a bounded regular file")
    return path.read_text(encoding="utf-8")


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_text = tempfile.mkstemp(prefix=".qa-mutation-", dir=path.parent)
    temporary = Path(temporary_text)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o600)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def install_qa_mutation(
    repository_root: Path,
    scenario_id: str,
    mutation_id: str = "canonical",
) -> InstalledMutation:
    """Reset the disposable workspace and install exactly one immutable evaluation mutation."""

    manifest = load_manifest(repository_root, scenario_id)
    status = reset_workspace(repository_root, manifest)
    workspace = Path(str(status["workspace"])).resolve(strict=True)
    model = _read_fixture("fct_net_revenue.sql")
    test = _read_fixture("assert_fct_net_revenue_contract.sql")
    expected_defect = None
    if mutation_id != "canonical":
        candidates = {item.id: item for item in load_qa_mutations().mutations}
        if mutation_id not in candidates:
            raise ValueError("unknown QA mutation")
        mutation = candidates[mutation_id]
        selected = model if mutation.target == "model" else test
        if selected.count(mutation.old) != 1:
            raise RuntimeError("QA mutation source marker is not unique")
        selected = (
            mutation.new
            if mutation.target == "test"
            else selected.replace(mutation.old, mutation.new, 1)
        )
        if mutation.target == "model":
            model = selected
        else:
            test = selected
        expected_defect = mutation.expected_defect
    _atomic_write(workspace / MODEL_TARGET, model)
    _atomic_write(workspace / TEST_TARGET, test)
    return InstalledMutation(
        mutation_id=mutation_id,
        expected_defect=expected_defect,
        workspace=workspace,
        model_sha256=sha256(model.encode()).hexdigest(),
        test_sha256=sha256(test.encode()).hexdigest(),
    )


def seed_mutation_candidate(
    repository_root: Path,
    scenario_id: str,
    mutation_id: str,
    *,
    workflow_id: str,
    budget_limits: BudgetLimits | None = None,
) -> MutationCandidateWorkflow:
    """Install a fixture and enter IMPLEMENTED through ordinary artifact gates."""

    installed = install_qa_mutation(repository_root, scenario_id, mutation_id)
    return seed_installed_candidate(
        repository_root,
        scenario_id,
        installed,
        workflow_id=workflow_id,
        budget_limits=budget_limits,
    )


def seed_installed_candidate(
    repository_root: Path,
    scenario_id: str,
    installed: InstalledMutation,
    *,
    workflow_id: str,
    budget_limits: BudgetLimits | None = None,
) -> MutationCandidateWorkflow:
    """Enter IMPLEMENTED for an already installed content-addressed candidate."""

    mutation_id = installed.mutation_id
    now = datetime.now(UTC)
    request = prepare_data_engineer_request(
        repository_root,
        scenario_id,
        workflow_id=workflow_id,
        correlation_id=workflow_id,
        started_at=now,
    )
    if budget_limits is not None:
        request = request.model_copy(update={"budget_limits": budget_limits})
    state, events = seed_data_engineer_state(request)
    artifact_evidence = tuple(
        Evidence(
            evidence_id=f"mutation-{mutation_id}-{kind}-evidence",
            task_id=state.task_id,
            producer_id="mutation-harness",
            kind=EvidenceKind.ARTIFACT,
            source="qa-mutation-fixture",
            invocation=f"fixture={mutation_id};target={relative}",
            exit_code=0,
            artifact=ArtifactReference(
                path=(installed.workspace / relative).relative_to(repository_root).as_posix(),
                sha256=digest,
                media_type="text/plain; charset=utf-8",
                size_bytes=(installed.workspace / relative).stat().st_size,
            ),
            occurred_at=now,
        )
        for kind, relative, digest in (
            ("model", MODEL_TARGET, installed.model_sha256),
            ("test", TEST_TARGET, installed.test_sha256),
        )
    )
    implementation = ImplementationResult(
        artifact_id=f"mutation-{mutation_id}-implementation",
        task_id=state.task_id,
        producer_id="mutation-harness",
        created_at=now,
        status=ImplementationStatus.COMPLETED,
        changed_files=(MODEL_TARGET, TEST_TARGET),
        summary="Installed one content-addressed QA evaluation candidate.",
        evidence=artifact_evidence,
    )
    for command in (
        TransitionCommand(
            command_id=f"mutation-{mutation_id}-implemented",
            task_id=state.task_id,
            actor_id="mutation-harness",
            target_stage=Stage.IMPLEMENTED,
            occurred_at=now,
            artifact=implementation,
        ),
    ):
        state, events = append_transition(state, command, events)
    return MutationCandidateWorkflow(installed=installed, state=state, events=events)
