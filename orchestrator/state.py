"""Immutable workflow state and fail-closed resource budgets."""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import Field, model_validator

from contracts import TaskRequest
from contracts.common import FrozenModel, Identifier, NonNegativeInt, VersionedModel, ensure_unique
from orchestrator.errors import BudgetExceededError


class Stage(StrEnum):
    CREATED = "created"
    SPECIFYING = "specifying"
    SPEC_READY = "spec_ready"
    ANALYZING = "analyzing"
    ANALYSIS_READY = "analysis_ready"
    IMPLEMENTING = "implementing"
    IMPLEMENTED = "implemented"
    VALIDATING = "validating"
    VALIDATED = "validated"
    QA = "qa"
    QA_PASSED = "qa_passed"
    REVIEW = "review"
    REWORK = "rework"
    DONE = "done"
    BLOCKED = "blocked"
    FAILED = "failed"

    @property
    def terminal(self) -> bool:
        return self in {Stage.DONE, Stage.BLOCKED, Stage.FAILED}


class BudgetLimits(FrozenModel):
    tool_calls: NonNegativeInt
    model_tokens: NonNegativeInt
    wall_time_seconds: NonNegativeInt
    rework_attempts: NonNegativeInt


class BudgetUsage(FrozenModel):
    tool_calls: NonNegativeInt = 0
    model_tokens: NonNegativeInt = 0
    wall_time_seconds: NonNegativeInt = 0
    rework_attempts: NonNegativeInt = 0


class BudgetCharge(BudgetUsage):
    """Resources measured by code for one accepted transition."""


class BudgetState(FrozenModel):
    limits: BudgetLimits
    used: BudgetUsage = Field(default_factory=BudgetUsage)

    @model_validator(mode="after")
    def validate_within_limits(self) -> Self:
        for field in BudgetUsage.model_fields:
            if getattr(self.used, field) > getattr(self.limits, field):
                raise ValueError(f"used {field} exceeds configured limit")
        return self

    @property
    def remaining(self) -> BudgetUsage:
        return BudgetUsage(
            **{
                field: getattr(self.limits, field) - getattr(self.used, field)
                for field in BudgetUsage.model_fields
            }
        )

    def charge(self, charge: BudgetCharge) -> BudgetState:
        values: dict[str, int] = {}
        for field in BudgetUsage.model_fields:
            value = getattr(self.used, field) + getattr(charge, field)
            if value > getattr(self.limits, field):
                raise BudgetExceededError(f"{field} budget exceeded")
            values[field] = value
        return BudgetState(limits=self.limits, used=BudgetUsage(**values))


class WorkflowState(VersionedModel):
    workflow_id: Identifier
    correlation_id: Identifier
    task_id: Identifier
    stage: Stage
    revision: NonNegativeInt
    budgets: BudgetState
    artifact_ids: tuple[Identifier, ...]
    implementation_author_id: Identifier | None = None
    terminal_reason: str | None = None

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        ensure_unique(self.artifact_ids, "artifact_ids")
        if self.stage in {Stage.BLOCKED, Stage.FAILED} and not self.terminal_reason:
            raise ValueError("blocked and failed states require terminal_reason")
        if not self.stage.terminal and self.terminal_reason is not None:
            raise ValueError("active states cannot contain terminal_reason")
        return self


def initial_state(
    task: TaskRequest,
    *,
    workflow_id: str,
    correlation_id: str,
    limits: BudgetLimits,
) -> WorkflowState:
    """Create the only valid revision-zero state from a TaskRequest."""

    return WorkflowState(
        workflow_id=workflow_id,
        correlation_id=correlation_id,
        task_id=task.task_id,
        stage=Stage.CREATED,
        revision=0,
        budgets=BudgetState(limits=limits),
        artifact_ids=(task.artifact_id,),
    )
