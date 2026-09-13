"""Checkpointable MAF graph with one executor per business role."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Never

from agent_framework import Executor, Workflow, WorkflowBuilder, WorkflowContext, handler
from pydantic import model_validator

from contracts import (
    AnalysisReport,
    ImplementationResult,
    PMRequirementsHandoff,
    QAReport,
    RequirementsAnalysisReport,
    ReviewReport,
    TaskSpecification,
    ValidationResult,
)
from contracts.common import FrozenModel
from orchestrator import EventChainError, Stage, WorkflowEvent, WorkflowState, verify_event_chain
from runtime.analyst import AnalystRunRequest
from runtime.checkpoints import SecureCheckpointStorage

ROLE_PIPELINE_NAME = "agentic-data-role-pipeline-v1"
MAX_ROLE_MESSAGE_BYTES = 5_000_000


class RoleBoundaryError(RuntimeError):
    """A role handoff is malformed or does not match the accepted workflow tip."""


class RolePipelineSnapshot(FrozenModel):
    """Complete, immutable handoff reconstructed and validated at every role boundary."""

    request: AnalystRunRequest
    state: WorkflowState | None = None
    events: tuple[WorkflowEvent, ...] = ()
    requirements: RequirementsAnalysisReport | None = None
    handoff: PMRequirementsHandoff | None = None
    specification: TaskSpecification | None = None
    analysis: AnalysisReport | None = None
    implementation: ImplementationResult | None = None
    validation: ValidationResult | None = None
    qa_report: QAReport | None = None
    review_report: ReviewReport | None = None

    @model_validator(mode="after")
    def validate_accepted_tip(self):
        if self.state is None:
            if self.events or any(
                item is not None
                for item in (
                    self.requirements,
                    self.handoff,
                    self.specification,
                    self.analysis,
                    self.implementation,
                    self.validation,
                    self.qa_report,
                    self.review_report,
                )
            ):
                raise ValueError("an unstarted pipeline cannot contain accepted state or artifacts")
            return self

        state = self.state
        if state.workflow_id != self.request.workflow_id:
            raise ValueError("snapshot workflow does not match the original request")
        if state.task_id != self.request.task.task_id:
            raise ValueError("snapshot task does not match the original request")
        try:
            verify_event_chain(self.events, expected_state=state)
        except EventChainError as error:
            # Pydantic validators must expose one closed validation failure at this boundary.
            raise ValueError("snapshot event chain is invalid") from error

        # AnalysisReport is supporting DE reasoning. Unlike gate artifacts, the current reducer
        # deliberately does not append its ID; ImplementationResult is the accepted DE outcome.
        accepted_artifacts = tuple(
            item
            for item in (
                self.requirements,
                self.specification,
                self.implementation,
                self.validation,
                self.qa_report,
                self.review_report,
            )
            if item is not None
        )
        scoped_artifacts = (*accepted_artifacts, *((self.analysis,) if self.analysis else ()))
        if any(item.task_id != state.task_id for item in scoped_artifacts):
            raise ValueError("snapshot contains an artifact from another task")
        if any(item.artifact_id not in state.artifact_ids for item in accepted_artifacts):
            raise ValueError("snapshot contains an artifact not accepted by the reducer")
        if self.handoff is not None:
            if self.requirements is None or self.handoff.analysis != self.requirements:
                raise ValueError("PM handoff does not contain the accepted requirements report")
            if self.handoff.task != self.request.task:
                raise ValueError("PM handoff replaced the original task")
            if self.handoff.workflow_id != state.workflow_id:
                raise ValueError("PM handoff belongs to another workflow")
        self._validate_stage_shape()
        return self

    def _validate_stage_shape(self) -> None:
        assert self.state is not None
        required_by_stage = {
            Stage.ANALYSIS_READY: (self.requirements, self.handoff),
            Stage.SPEC_READY: (self.requirements, self.handoff, self.specification),
            Stage.IMPLEMENTED: (
                self.requirements,
                self.handoff,
                self.specification,
                self.analysis,
                self.implementation,
            ),
            Stage.VALIDATED: (
                self.requirements,
                self.handoff,
                self.specification,
                self.analysis,
                self.implementation,
                self.validation,
            ),
            Stage.QA_PASSED: (
                self.requirements,
                self.handoff,
                self.specification,
                self.analysis,
                self.implementation,
                self.validation,
                self.qa_report,
            ),
            Stage.DONE: (
                self.requirements,
                self.handoff,
                self.specification,
                self.analysis,
                self.implementation,
                self.validation,
                self.qa_report,
                self.review_report,
            ),
        }
        required = required_by_stage.get(self.state.stage)
        if required is None:
            raise ValueError("role pipeline snapshot is not at a committed happy-path boundary")
        if any(item is None for item in required):
            raise ValueError(f"snapshot is incomplete for {self.state.stage.value}")
        ordered = (
            self.requirements,
            self.handoff,
            self.specification,
            self.analysis,
            self.implementation,
            self.validation,
            self.qa_report,
            self.review_report,
        )
        expected_count = {
            Stage.ANALYSIS_READY: 2,
            Stage.SPEC_READY: 3,
            Stage.IMPLEMENTED: 5,
            Stage.VALIDATED: 6,
            Stage.QA_PASSED: 7,
            Stage.DONE: 8,
        }[self.state.stage]
        if any(item is None for item in ordered[:expected_count]) or any(
            item is not None for item in ordered[expected_count:]
        ):
            raise ValueError(f"snapshot has out-of-order artifacts for {self.state.stage.value}")


RoleStageHandler = Callable[[RolePipelineSnapshot], Awaitable[RolePipelineSnapshot]]


@dataclass(frozen=True)
class RolePipelineHandlers:
    analyst: RoleStageHandler
    pm: RoleStageHandler
    data_engineer: RoleStageHandler
    validator: RoleStageHandler
    qa: RoleStageHandler
    reviewer: RoleStageHandler


def encode_role_snapshot(snapshot: RolePipelineSnapshot) -> str:
    payload = json.dumps(
        snapshot.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    if len(payload.encode("utf-8")) > MAX_ROLE_MESSAGE_BYTES:
        raise RoleBoundaryError("role handoff exceeds the size limit")
    return payload


def decode_role_snapshot(payload: str) -> RolePipelineSnapshot:
    if not isinstance(payload, str):
        raise RoleBoundaryError("role handoff must be JSON text")
    if len(payload.encode("utf-8")) > MAX_ROLE_MESSAGE_BYTES:
        raise RoleBoundaryError("role handoff exceeds the size limit")
    try:
        return RolePipelineSnapshot.model_validate_json(payload, strict=True)
    except (TypeError, ValueError) as error:
        raise RoleBoundaryError("role handoff failed validation") from error


class _RoleExecutor(Executor):
    def __init__(
        self,
        executor_id: str,
        stage_handler: RoleStageHandler,
        incoming: Stage | None,
        outgoing: Stage,
    ) -> None:
        super().__init__(id=executor_id)
        self.stage_handler = stage_handler
        self.incoming = incoming
        self.outgoing = outgoing

    async def advance(self, payload: str) -> RolePipelineSnapshot:
        snapshot = decode_role_snapshot(payload)
        actual = snapshot.state.stage if snapshot.state is not None else None
        if actual is not self.incoming:
            expected = self.incoming.value if self.incoming is not None else "unstarted"
            raise RoleBoundaryError(f"{self.id} requires {expected} input")
        result = await self.stage_handler(snapshot)
        if not isinstance(result, RolePipelineSnapshot):
            raise RoleBoundaryError(f"{self.id} returned an invalid snapshot type")
        # Round-trip at the trust boundary; do not trust model construction shortcuts.
        result = decode_role_snapshot(encode_role_snapshot(result))
        if result.state is None or result.state.stage is not self.outgoing:
            raise RoleBoundaryError(f"{self.id} did not reach {self.outgoing.value}")
        if result.request != snapshot.request:
            raise RoleBoundaryError(f"{self.id} replaced the immutable pipeline request")
        if snapshot.state is not None:
            if result.state.workflow_id != snapshot.state.workflow_id:
                raise RoleBoundaryError(f"{self.id} changed workflow identity")
            if result.events[: len(snapshot.events)] != snapshot.events:
                raise RoleBoundaryError(f"{self.id} rewrote accepted workflow history")
            if len(result.events) != len(snapshot.events) + 2:
                raise RoleBoundaryError(f"{self.id} did not make exactly one gated role step")
        elif len(result.events) != 2:
            raise RoleBoundaryError(f"{self.id} did not make exactly one gated role step")
        for field in (
            "requirements",
            "handoff",
            "specification",
            "analysis",
            "implementation",
            "validation",
            "qa_report",
            "review_report",
        ):
            before = getattr(snapshot, field)
            if before is not None and getattr(result, field) != before:
                raise RoleBoundaryError(f"{self.id} replaced accepted {field}")
        return result


class AnalystExecutor(_RoleExecutor):
    @handler
    async def run(self, payload: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(encode_role_snapshot(await self.advance(payload)))


class PMExecutor(_RoleExecutor):
    @handler
    async def run(self, payload: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(encode_role_snapshot(await self.advance(payload)))


class DataEngineerExecutor(_RoleExecutor):
    @handler
    async def run(self, payload: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(encode_role_snapshot(await self.advance(payload)))


class ValidatorExecutor(_RoleExecutor):
    @handler
    async def run(self, payload: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(encode_role_snapshot(await self.advance(payload)))


class QAExecutor(_RoleExecutor):
    @handler
    async def run(self, payload: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(encode_role_snapshot(await self.advance(payload)))


class ReviewerExecutor(_RoleExecutor):
    @handler
    async def run(self, payload: str, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output(encode_role_snapshot(await self.advance(payload)))


def build_role_pipeline(
    handlers: RolePipelineHandlers,
    checkpoint_storage: SecureCheckpointStorage,
) -> Workflow:
    """Build a stable six-role graph; graph identity is part of the restore contract."""

    analyst = AnalystExecutor("role_analyst", handlers.analyst, None, Stage.ANALYSIS_READY)
    pm = PMExecutor("role_pm", handlers.pm, Stage.ANALYSIS_READY, Stage.SPEC_READY)
    data_engineer = DataEngineerExecutor(
        "role_data_engineer", handlers.data_engineer, Stage.SPEC_READY, Stage.IMPLEMENTED
    )
    validator = ValidatorExecutor(
        "role_validator", handlers.validator, Stage.IMPLEMENTED, Stage.VALIDATED
    )
    qa = QAExecutor("role_qa", handlers.qa, Stage.VALIDATED, Stage.QA_PASSED)
    reviewer = ReviewerExecutor("role_reviewer", handlers.reviewer, Stage.QA_PASSED, Stage.DONE)
    return (
        WorkflowBuilder(
            name=ROLE_PIPELINE_NAME,
            start_executor=analyst,
            checkpoint_storage=checkpoint_storage,
            output_from=[reviewer],
        )
        .add_edge(analyst, pm)
        .add_edge(pm, data_engineer)
        .add_edge(data_engineer, validator)
        .add_edge(validator, qa)
        .add_edge(qa, reviewer)
        .build()
    )


def initial_role_message(request: AnalystRunRequest) -> str:
    return encode_role_snapshot(RolePipelineSnapshot(request=request))
