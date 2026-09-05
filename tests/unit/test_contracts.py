from datetime import datetime

import pytest
from pydantic import TypeAdapter, ValidationError

from contracts import (
    Artifact,
    ArtifactReference,
    Evidence,
    EvidenceKind,
    ImplementationResult,
    SpecificationDecision,
    TaskSpecification,
)
from tests.workflow.factories import TASK_ID, at, evidence, implementation_result, specification


def test_artifact_union_round_trips_discriminator_json() -> None:
    artifact = implementation_result()
    adapter = TypeAdapter(Artifact)

    restored = adapter.validate_json(adapter.dump_json(artifact))

    assert restored == artifact
    assert isinstance(restored, ImplementationResult)


def test_models_are_frozen_and_reject_extra_fields() -> None:
    item = implementation_result()

    with pytest.raises(ValidationError, match="frozen"):
        item.summary = "tampered"  # type: ignore[misc]
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ImplementationResult.model_validate({**item.model_dump(), "unexpected": True})


def test_naive_timestamp_is_rejected() -> None:
    item = evidence("evidence-naive", 1).model_dump()
    item["occurred_at"] = datetime(2026, 9, 5, 18, 0)

    with pytest.raises(ValidationError, match="timezone-aware UTC"):
        Evidence.model_validate(item)


def test_evidence_requires_source_invocation_exit_code_and_artifact() -> None:
    payload = {
        "evidence_id": "evidence-incomplete",
        "task_id": TASK_ID,
        "producer_id": "validator",
        "kind": EvidenceKind.TEST,
        "occurred_at": at(1),
    }

    with pytest.raises(ValidationError) as captured:
        Evidence.model_validate(payload)

    missing = {error["loc"][0] for error in captured.value.errors()}
    assert {"source", "invocation", "exit_code", "artifact"}.issubset(missing)


@pytest.mark.parametrize("path", ["../secret", "/etc/passwd", "a/../../b", "a\\b", "a//b"])
def test_artifact_reference_rejects_unsafe_path(path: str) -> None:
    with pytest.raises(ValidationError, match="path"):
        ArtifactReference(
            path=path,
            sha256="a" * 64,
            media_type="application/json",
            size_bytes=1,
        )


def test_ready_specification_requires_complete_semantics() -> None:
    payload = specification().model_dump()
    payload["metric_definition"] = None

    with pytest.raises(ValidationError, match="requires metric_definition"):
        TaskSpecification.model_validate(payload)


def test_blocked_specification_requires_open_question() -> None:
    payload = specification(decision=SpecificationDecision.BLOCKED).model_dump()
    payload["open_questions"] = ()

    with pytest.raises(ValidationError, match="requires open questions"):
        TaskSpecification.model_validate(payload)


def test_evidence_must_match_task_and_precede_artifact() -> None:
    payload = implementation_result().model_dump()
    wrong_task = evidence("evidence-wrong-task", 5, task_id="TASK-OTHER")
    payload["evidence"] = (wrong_task,)
    payload["tests_executed"] = (wrong_task.evidence_id,)

    with pytest.raises(ValidationError, match="artifact task"):
        ImplementationResult.model_validate(payload)

    future = evidence("evidence-future", 100)
    payload["evidence"] = (future,)
    payload["tests_executed"] = (future.evidence_id,)
    with pytest.raises(ValidationError, match="after artifact creation"):
        ImplementationResult.model_validate(payload)


def test_unknown_contract_status_is_rejected() -> None:
    payload = specification().model_dump()
    payload["decision"] = "invented"

    with pytest.raises(ValidationError, match=r"ready|blocked"):
        TaskSpecification.model_validate(payload)
