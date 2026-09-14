"""Checkpointable MAF graph with one executor per business role."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from contextlib import nullcontext
from dataclasses import dataclass
from hashlib import sha256
from typing import Never

from agent_framework import (
    Case,
    Default,
    Executor,
    Workflow,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowRunResult,
    handler,
)
from pydantic import model_validator

from contracts import (
    AnalysisReport,
    Artifact,
    ImplementationResult,
    ImplementationStatus,
    PMRequirementsHandoff,
    QADecision,
    QAReport,
    RequirementsAnalysisReport,
    ReviewDecision,
    ReviewReport,
    SpecificationDecision,
    TaskSpecification,
    ValidationDecision,
    ValidationResult,
)
from contracts.common import FrozenModel
from orchestrator import EventChainError, Stage, WorkflowEvent, WorkflowState, verify_event_chain
from runtime.analyst import AnalystRunRequest
from runtime.checkpoints import SecureCheckpointStorage
from runtime.role_receipts import RoleReceipt, SecureRoleReceiptStore, role_operation_id
from runtime.telemetry import AgenticTelemetry, SafeSpan, TraceCarrier

ROLE_PIPELINE_NAME = "agentic-data-role-pipeline-v3"
MAX_ROLE_MESSAGE_BYTES = 5_000_000
MAX_ROLE_PIPELINE_ITERATIONS = 32


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
    gate_history: tuple[Artifact, ...] = ()
    trace: TraceCarrier | None = None

    @model_validator(mode="after")
    def validate_accepted_tip(self):
        artifacts = (
            self.requirements,
            self.handoff,
            self.specification,
            self.analysis,
            self.implementation,
            self.validation,
            self.qa_report,
            self.review_report,
        )
        if self.state is None:
            if self.events or self.gate_history or any(item is not None for item in artifacts):
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
            raise ValueError("snapshot event chain is invalid") from error

        if any(
            not isinstance(item, (ImplementationResult, ValidationResult, QAReport, ReviewReport))
            for item in self.gate_history
        ):
            raise ValueError("gate history contains a non-attempt artifact")
        current_gate = tuple(
            item
            for item in (self.implementation, self.validation, self.qa_report, self.review_report)
            if item is not None
        )
        accepted = tuple(
            item
            for item in (self.requirements, self.specification, *self.gate_history, *current_gate)
            if item is not None
        )
        scoped = (*accepted, *((self.analysis,) if self.analysis else ()))
        if any(item.task_id != state.task_id for item in scoped):
            raise ValueError("snapshot contains an artifact from another task")
        if state.artifact_ids != (
            self.request.task.artifact_id,
            *(item.artifact_id for item in accepted),
        ):
            raise ValueError("snapshot artifact ledger does not match reducer history")
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
        stage = self.state.stage
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
        happy_counts = {
            Stage.ANALYSIS_READY: 2,
            Stage.SPEC_READY: 3,
            Stage.IMPLEMENTED: 5,
            Stage.VALIDATED: 6,
            Stage.QA_PASSED: 7,
            Stage.DONE: 8,
        }
        if stage in happy_counts:
            count = happy_counts[stage]
            if any(item is None for item in ordered[:count]) or any(
                item is not None for item in ordered[count:]
            ):
                raise ValueError(f"snapshot has out-of-order artifacts for {stage.value}")
            self._validate_success_decisions(stage)
            return
        if stage is Stage.REWORK:
            self._validate_rework_shape()
            return
        if stage in {Stage.BLOCKED, Stage.FAILED}:
            self._validate_terminal_shape(stage)
            return
        raise ValueError("role pipeline snapshot is not at a committed role boundary")

    def _validate_success_decisions(self, stage: Stage) -> None:
        if (
            stage is Stage.SPEC_READY
            and self.specification.decision is not SpecificationDecision.READY
        ):
            raise ValueError("spec_ready requires a ready specification")
        if (
            stage is Stage.IMPLEMENTED
            and self.implementation.status is not ImplementationStatus.COMPLETED
        ):
            raise ValueError("implemented requires a completed implementation")
        if stage in {Stage.VALIDATED, Stage.QA_PASSED, Stage.DONE}:
            if self.validation.decision is not ValidationDecision.PASS:
                raise ValueError("downstream role requires passing validation")
        if (
            stage in {Stage.QA_PASSED, Stage.DONE}
            and self.qa_report.decision is not QADecision.PASS
        ):
            raise ValueError("downstream review requires passing QA")
        if stage is Stage.DONE and self.review_report.decision is not ReviewDecision.APPROVE:
            raise ValueError("done requires reviewer approval")

    def _validate_rework_shape(self) -> None:
        if any(
            item is None
            for item in (
                self.requirements,
                self.handoff,
                self.specification,
                self.analysis,
                self.implementation,
            )
        ):
            raise ValueError("rework snapshot is missing upstream artifacts")
        validator_failed = (
            self.validation is not None
            and self.validation.decision is ValidationDecision.FAIL
            and self.qa_report is None
            and self.review_report is None
        )
        qa_failed = (
            self.validation is not None
            and self.validation.decision is ValidationDecision.PASS
            and self.qa_report is not None
            and self.qa_report.decision is QADecision.FAIL
            and self.review_report is None
        )
        reviewer_failed = (
            self.validation is not None
            and self.validation.decision is ValidationDecision.PASS
            and self.qa_report is not None
            and self.qa_report.decision is QADecision.PASS
            and self.review_report is not None
            and self.review_report.decision is ReviewDecision.REQUEST_CHANGES
        )
        if not (validator_failed or qa_failed or reviewer_failed):
            raise ValueError("rework snapshot does not contain one accepted failing gate")

    def _validate_terminal_shape(self, stage: Stage) -> None:
        if self.requirements is None or self.handoff is None:
            raise ValueError("terminal snapshot is missing requirements")
        if stage is Stage.BLOCKED:
            valid = (
                (
                    self.specification is not None
                    and self.specification.decision is SpecificationDecision.BLOCKED
                    and self.implementation is None
                )
                or (
                    self.implementation is not None
                    and self.implementation.status is ImplementationStatus.BLOCKED
                )
                or (self.qa_report is not None and self.qa_report.decision is QADecision.BLOCKED)
                or (
                    self.review_report is not None
                    and self.review_report.decision is ReviewDecision.BLOCKED
                )
            )
        else:
            valid = (
                (
                    self.implementation is not None
                    and self.implementation.status is ImplementationStatus.FAILED
                )
                or (
                    self.validation is not None
                    and self.validation.decision
                    in {ValidationDecision.FAIL, ValidationDecision.ERROR}
                )
                or (self.qa_report is not None and self.qa_report.decision is QADecision.FAIL)
                or (
                    self.review_report is not None
                    and self.review_report.decision is ReviewDecision.REQUEST_CHANGES
                )
            )
        if not valid:
            raise ValueError(f"snapshot does not explain terminal {stage.value}")


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
        incoming: frozenset[Stage | None],
        outgoing: frozenset[Stage],
        receipt_store: SecureRoleReceiptStore | None = None,
        after_receipt: Callable[[str, str], Awaitable[None]] | None = None,
        telemetry: AgenticTelemetry | None = None,
    ) -> None:
        super().__init__(id=executor_id)
        self.stage_handler = stage_handler
        self.incoming = incoming
        self.outgoing = outgoing
        self.receipt_store = receipt_store
        self.after_receipt = after_receipt
        self.telemetry = telemetry

    async def advance(self, payload: str) -> RolePipelineSnapshot:
        snapshot = decode_role_snapshot(payload)
        actual = snapshot.state.stage if snapshot.state is not None else None
        if actual not in self.incoming:
            expected = ",".join(
                "unstarted" if item is None else item.value
                for item in sorted(
                    self.incoming, key=lambda value: "" if value is None else value.value
                )
            )
            raise RoleBoundaryError(f"{self.id} requires {expected} input")
        revision = snapshot.state.revision if snapshot.state is not None else 0
        operation_id = role_operation_id(
            workflow_id=snapshot.request.workflow_id,
            executor_id=self.id,
            input_revision=revision,
            input_payload=payload,
        )
        trace_scope = (
            self.telemetry.role(
                snapshot.trace,
                workflow_id=snapshot.request.workflow_id,
                task_id=snapshot.request.task.task_id,
                role_name=self.id.removeprefix("role_"),
                input_stage="unstarted" if actual is None else actual.value,
                operation_id=operation_id,
            )
            if self.telemetry is not None and snapshot.trace is not None
            else nullcontext(None)
        )
        with trace_scope as role_span:
            receipt = self.receipt_store.get(operation_id) if self.receipt_store else None
            if receipt is None:
                result = await self.stage_handler(snapshot)
                if not isinstance(result, RolePipelineSnapshot):
                    raise RoleBoundaryError(f"{self.id} returned an invalid snapshot type")
                result = self._validate_result(snapshot, result)
                if self.receipt_store is not None:
                    output = encode_role_snapshot(result)
                    self.receipt_store.save(
                        RoleReceipt(
                            operation_id=operation_id,
                            workflow_id=snapshot.request.workflow_id,
                            executor_id=self.id,
                            input_revision=revision,
                            input_sha256=sha256(payload.encode("utf-8")).hexdigest(),
                            output_sha256=sha256(output.encode("utf-8")).hexdigest(),
                            output=output,
                        )
                    )
                    if self.after_receipt is not None:
                        await self.after_receipt(self.id, operation_id)
                self._complete_trace(snapshot, result, role_span, receipt_hit=False)
                return result
            if (
                receipt.workflow_id != snapshot.request.workflow_id
                or receipt.executor_id != self.id
                or receipt.input_revision != revision
                or receipt.input_sha256 != sha256(payload.encode("utf-8")).hexdigest()
            ):
                raise RoleBoundaryError(f"{self.id} receipt does not match role input")
            result = self._validate_result(snapshot, decode_role_snapshot(receipt.output))
            self._complete_trace(snapshot, result, role_span, receipt_hit=True)
            return result

    def _complete_trace(
        self,
        before: RolePipelineSnapshot,
        after: RolePipelineSnapshot,
        span: SafeSpan | None,
        *,
        receipt_hit: bool,
    ) -> None:
        if span is None or self.telemetry is None or after.state is None:
            return
        span.set("agentic.stage.output", after.state.stage.value)
        span.set("agentic.receipt.hit", receipt_hit)
        if receipt_hit:
            return
        artifacts = {
            item.artifact_id: item
            for item in (
                after.requirements,
                after.specification,
                *after.gate_history,
                after.implementation,
                after.validation,
                after.qa_report,
                after.review_report,
            )
            if item is not None
        }
        for event in after.events[len(before.events) :]:
            if event.artifact_id is not None:
                self.telemetry.artifact(
                    artifacts[event.artifact_id],
                    workflow_id=after.state.workflow_id,
                    event_hash=event.event_hash,
                )

    def _validate_result(
        self, snapshot: RolePipelineSnapshot, result: RolePipelineSnapshot
    ) -> RolePipelineSnapshot:
        # Round-trip at the trust boundary; do not trust model construction shortcuts.
        result = decode_role_snapshot(encode_role_snapshot(result))
        if result.state is None or result.state.stage not in self.outgoing:
            expected = ",".join(sorted(item.value for item in self.outgoing))
            raise RoleBoundaryError(f"{self.id} did not reach one of {expected}")
        if result.request != snapshot.request:
            raise RoleBoundaryError(f"{self.id} replaced the immutable pipeline request")
        if result.trace != snapshot.trace:
            raise RoleBoundaryError(f"{self.id} replaced trace identity")
        if snapshot.state is not None:
            if result.state.workflow_id != snapshot.state.workflow_id:
                raise RoleBoundaryError(f"{self.id} changed workflow identity")
            if result.events[: len(snapshot.events)] != snapshot.events:
                raise RoleBoundaryError(f"{self.id} rewrote accepted workflow history")
            if len(result.events) != len(snapshot.events) + 2:
                raise RoleBoundaryError(f"{self.id} did not make exactly one gated role step")
        elif len(result.events) != 2:
            raise RoleBoundaryError(f"{self.id} did not make exactly one gated role step")
        if snapshot.state is not None and snapshot.state.stage is Stage.REWORK:
            if self.id != "role_data_engineer":
                raise RoleBoundaryError("only Data Engineer may consume rework")
            rolled = tuple(
                item
                for item in (
                    snapshot.implementation,
                    snapshot.validation,
                    snapshot.qa_report,
                    snapshot.review_report,
                )
                if item is not None
            )
            if result.gate_history != (*snapshot.gate_history, *rolled):
                raise RoleBoundaryError("Data Engineer did not preserve the prior attempt ledger")
            if any(
                item is not None
                for item in (result.validation, result.qa_report, result.review_report)
            ):
                raise RoleBoundaryError("Data Engineer did not reset completed downstream gates")
        elif result.gate_history != snapshot.gate_history:
            raise RoleBoundaryError(f"{self.id} rewrote gate history")
        mutable = {
            "role_analyst": frozenset({"requirements", "handoff"}),
            "role_pm": frozenset({"specification"}),
            "role_data_engineer": frozenset({"implementation"}),
            "role_validator": frozenset({"validation"}),
            "role_qa": frozenset({"qa_report"}),
            "role_reviewer": frozenset({"review_report"}),
        }[self.id]
        if snapshot.state is not None and snapshot.state.stage is Stage.REWORK:
            mutable = mutable | {"validation", "qa_report", "review_report"}
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
            if before is not None and field not in mutable and getattr(result, field) != before:
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
    async def run(self, payload: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(encode_role_snapshot(await self.advance(payload)))


class TerminalExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="role_terminal")

    @handler
    async def run(self, payload: str, ctx: WorkflowContext[Never, str]) -> None:
        snapshot = decode_role_snapshot(payload)
        if snapshot.state is None or not snapshot.state.stage.terminal:
            raise RoleBoundaryError("terminal executor requires done, blocked, or failed")
        await ctx.yield_output(encode_role_snapshot(snapshot))


def _route_stage(payload: str, stage: Stage) -> bool:
    snapshot = decode_role_snapshot(payload)
    return snapshot.state is not None and snapshot.state.stage is stage


def route_spec_ready(payload: str) -> bool:
    return _route_stage(payload, Stage.SPEC_READY)


def route_implemented(payload: str) -> bool:
    return _route_stage(payload, Stage.IMPLEMENTED)


def route_validated(payload: str) -> bool:
    return _route_stage(payload, Stage.VALIDATED)


def route_qa_passed(payload: str) -> bool:
    return _route_stage(payload, Stage.QA_PASSED)


def route_rework(payload: str) -> bool:
    return _route_stage(payload, Stage.REWORK)


def build_role_pipeline(
    handlers: RolePipelineHandlers,
    checkpoint_storage: SecureCheckpointStorage,
    receipt_store: SecureRoleReceiptStore,
    *,
    after_receipt: Callable[[str, str], Awaitable[None]] | None = None,
    telemetry: AgenticTelemetry | None = None,
) -> Workflow:
    """Build the bounded branching graph; graph identity is part of the restore contract."""

    common = {
        "receipt_store": receipt_store,
        "after_receipt": after_receipt,
        "telemetry": telemetry,
    }
    analyst = AnalystExecutor(
        "role_analyst",
        handlers.analyst,
        frozenset({None}),
        frozenset({Stage.ANALYSIS_READY}),
        **common,
    )
    pm = PMExecutor(
        "role_pm",
        handlers.pm,
        frozenset({Stage.ANALYSIS_READY}),
        frozenset({Stage.SPEC_READY, Stage.BLOCKED}),
        **common,
    )
    data_engineer = DataEngineerExecutor(
        "role_data_engineer",
        handlers.data_engineer,
        frozenset({Stage.SPEC_READY, Stage.REWORK}),
        frozenset({Stage.IMPLEMENTED, Stage.BLOCKED, Stage.FAILED}),
        **common,
    )
    validator = ValidatorExecutor(
        "role_validator",
        handlers.validator,
        frozenset({Stage.IMPLEMENTED}),
        frozenset({Stage.VALIDATED, Stage.REWORK, Stage.FAILED}),
        **common,
    )
    qa = QAExecutor(
        "role_qa",
        handlers.qa,
        frozenset({Stage.VALIDATED}),
        frozenset({Stage.QA_PASSED, Stage.REWORK, Stage.BLOCKED, Stage.FAILED}),
        **common,
    )
    reviewer = ReviewerExecutor(
        "role_reviewer",
        handlers.reviewer,
        frozenset({Stage.QA_PASSED}),
        frozenset({Stage.DONE, Stage.REWORK, Stage.BLOCKED, Stage.FAILED}),
        **common,
    )
    terminal = TerminalExecutor()
    return (
        WorkflowBuilder(
            max_iterations=MAX_ROLE_PIPELINE_ITERATIONS,
            name=ROLE_PIPELINE_NAME,
            start_executor=analyst,
            checkpoint_storage=checkpoint_storage,
            output_from=[terminal],
        )
        .add_edge(analyst, pm)
        .add_switch_case_edge_group(
            pm, [Case(condition=route_spec_ready, target=data_engineer), Default(target=terminal)]
        )
        .add_switch_case_edge_group(
            data_engineer,
            [Case(condition=route_implemented, target=validator), Default(target=terminal)],
        )
        .add_switch_case_edge_group(
            validator,
            [
                Case(condition=route_validated, target=qa),
                Case(condition=route_rework, target=data_engineer),
                Default(target=terminal),
            ],
        )
        .add_switch_case_edge_group(
            qa,
            [
                Case(condition=route_qa_passed, target=reviewer),
                Case(condition=route_rework, target=data_engineer),
                Default(target=terminal),
            ],
        )
        .add_switch_case_edge_group(
            reviewer,
            [Case(condition=route_rework, target=data_engineer), Default(target=terminal)],
        )
        .build()
    )


def initial_role_message(
    request: AnalystRunRequest, *, trace_carrier: TraceCarrier | None = None
) -> str:
    return encode_role_snapshot(RolePipelineSnapshot(request=request, trace=trace_carrier))


async def run_traced_role_pipeline(
    workflow: Workflow,
    request: AnalystRunRequest,
    telemetry: AgenticTelemetry,
) -> WorkflowRunResult:
    """Run a fresh workflow under one root span and persist its trace carrier."""

    with telemetry.workflow(
        workflow_id=request.workflow_id,
        task_id=request.task.task_id,
        correlation_id=request.correlation_id,
    ) as (span, carrier):
        result = await workflow.run(initial_role_message(request, trace_carrier=carrier))
        outputs = result.get_outputs()
        if len(outputs) != 1:
            raise RoleBoundaryError("traced workflow must produce exactly one output")
        snapshot = decode_role_snapshot(outputs[0])
        if snapshot.state is None:
            raise RoleBoundaryError("traced workflow output has no state")
        span.set("agentic.workflow.stage", snapshot.state.stage.value)
        span.set("agentic.workflow.revision", snapshot.state.revision)
        return result
