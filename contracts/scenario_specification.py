"""Frozen human-authored specification envelope for autonomous scenarios."""

from __future__ import annotations

from typing import Annotated, Self

from pydantic import StringConstraints, model_validator

from contracts.artifacts import SpecificationDecision, TaskSpecification
from contracts.common import Identifier, Sha256, VersionedModel

SemanticVersion = Annotated[
    str,
    StringConstraints(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", max_length=32),
]


class ScenarioSpecification(VersionedModel):
    """Bind a trusted task specification to an exact scenario input document."""

    scenario_id: Identifier
    scenario_version: SemanticVersion
    task_sha256: Sha256
    specification: TaskSpecification

    @model_validator(mode="after")
    def validate_control_plane_identity(self) -> Self:
        expected_task = f"scenario-{self.scenario_id}"
        expected_artifact = (
            f"specification-{self.scenario_id}-v{self.scenario_version.replace('.', '-')}"
        )
        if self.specification.task_id != expected_task:
            raise ValueError("specification task does not match its scenario")
        if self.specification.artifact_id != expected_artifact:
            raise ValueError("specification artifact identity is not canonical")
        if self.specification.producer_id != "human":
            raise ValueError("scenario specification must be human-authored")
        if self.specification.decision is not SpecificationDecision.READY:
            raise ValueError("autonomous scenario requires a ready specification")
        if self.specification.evidence:
            raise ValueError("human scenario specification must not contain runtime evidence")
        return self
