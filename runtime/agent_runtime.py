"""Tool-free PM specification gate over an accepted Analyst handoff."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from hashlib import sha256
from math import ceil
from pathlib import Path
from typing import Never

from agent_framework import Executor, Workflow, WorkflowBuilder, WorkflowContext, handler

from contracts import (
    PMRequirementsHandoff,
    SpecificationBlockReason,
    SpecificationDecision,
    TaskSpecification,
)
from contracts.artifacts import TextTuple
from contracts.common import FrozenModel, Identifier, NonEmptyText, UtcDateTime
from orchestrator import (
    BudgetCharge,
    Stage,
    TransitionCommand,
    WorkflowEvent,
    WorkflowState,
    append_transition,
    verify_event_chain,
)
from runtime.model_provider import ModelCallRecord, StructuredModelProvider, model_call_record

PM_INSTRUCTIONS_PATH = Path(__file__).resolve().parents[1] / "agents/pm/instructions.md"


class PMBoundaryError(RuntimeError):
    """The PM input or output violated the requirements trust boundary."""


class SpecificationDraft(FrozenModel):
    """Untrusted PM content; all control-plane fields are intentionally absent."""

    decision: SpecificationDecision
    business_goal: NonEmptyText
    metric_definition: NonEmptyText | None = None
    grain: TextTuple = ()
    dimensions: TextTuple = ()
    source_requirements: TextTuple = ()
    acceptance_criteria: TextTuple = ()
    non_functional_requirements: TextTuple = ()
    assumptions: TextTuple = ()
    open_questions: TextTuple = ()
    risks: TextTuple = ()


class SpecificationRunRequest(FrozenModel):
    handoff: PMRequirementsHandoff
    state: WorkflowState
    events: tuple[WorkflowEvent, ...]
    agent_id: Identifier = "pm-agent"


class SpecificationRunResult(FrozenModel):
    artifact: TaskSpecification
    state: WorkflowState
    events: tuple[WorkflowEvent, ...]
    model_call: ModelCallRecord


def _identifier(prefix: str, *parts: str) -> str:
    digest = sha256("\x00".join(parts).encode()).hexdigest()[:24]
    return f"{prefix}-{digest}"


def pm_system_prompt() -> str:
    if PM_INSTRUCTIONS_PATH.is_symlink() or not PM_INSTRUCTIONS_PATH.is_file():
        raise RuntimeError("PM instructions must be a regular repository file")
    contents = PM_INSTRUCTIONS_PATH.read_bytes()
    if not 1 <= len(contents) <= 10_000:
        raise RuntimeError("PM instructions exceed the trusted size boundary")
    try:
        instructions = contents.decode("utf-8").strip()
    except UnicodeDecodeError:
        raise RuntimeError("PM instructions must be UTF-8") from None
    if not instructions:
        raise RuntimeError("PM instructions must not be empty")
    return instructions


def _user_prompt(handoff: PMRequirementsHandoff) -> str:
    analysis = handoff.analysis
    accepted = {
        "facts": [item.model_dump(mode="json") for item in analysis.facts],
        "assumptions": analysis.assumptions,
        "open_questions": analysis.open_questions,
        "risks": analysis.risks,
        "recommended_next_steps": analysis.recommended_next_steps,
    }
    return (
        "Create the PM decision from this immutable, reducer-accepted handoff. "
        "The workflow owns IDs, identity, time, evidence, budgets, and transitions.\n"
        f"<immutable_task>{handoff.task.model_dump_json(exclude={'evidence'})}</immutable_task>\n"
        "<untrusted_accepted_analysis>"
        f"{json.dumps(accepted, ensure_ascii=False, separators=(',', ':'), sort_keys=True)}"
        "</untrusted_accepted_analysis>"
    )


def validate_pm_request(request: SpecificationRunRequest) -> None:
    """Fail before the paid call unless the handoff is the accepted chain tip."""

    state = request.state
    handoff = request.handoff
    verify_event_chain(request.events, expected_state=state)
    if state.stage is not Stage.ANALYSIS_READY:
        raise PMBoundaryError("PM requires analysis_ready state")
    if handoff.workflow_id != state.workflow_id or handoff.task.task_id != state.task_id:
        raise PMBoundaryError("PM handoff belongs to another workflow or task")
    if handoff.task.artifact_id not in state.artifact_ids:
        raise PMBoundaryError("PM handoff task was not accepted by the workflow")
    if handoff.analysis.artifact_id not in state.artifact_ids:
        raise PMBoundaryError("PM handoff analysis was not accepted by the workflow")
    if not request.events or request.events[-1].artifact_id != handoff.analysis.artifact_id:
        raise PMBoundaryError("PM handoff analysis is not the accepted chain tip")
    reserved = {"workflow", handoff.task.producer_id, handoff.analysis.producer_id}
    if request.agent_id in reserved:
        raise PMBoundaryError("PM identity must be separate from workflow, user, and Analyst")


def accept_specification_draft(
    request: SpecificationRunRequest,
    state: WorkflowState,
    events: tuple[WorkflowEvent, ...],
    draft: SpecificationDraft,
    *,
    charge: BudgetCharge,
    completed_at: UtcDateTime,
) -> tuple[TaskSpecification, WorkflowState, tuple[WorkflowEvent, ...]]:
    """Turn untrusted model content into a code-owned artifact and reducer decision."""

    unresolved = request.handoff.unresolved_questions
    if unresolved and draft.decision is SpecificationDecision.READY:
        raise PMBoundaryError("PM cannot mark unresolved Analyst questions ready")
    if unresolved and draft.open_questions != unresolved:
        raise PMBoundaryError("PM must preserve unresolved Analyst questions exactly")
    blocked = draft.decision is SpecificationDecision.BLOCKED
    artifact = TaskSpecification(
        artifact_id=_identifier("spec", state.workflow_id, state.task_id),
        task_id=state.task_id,
        producer_id=request.agent_id,
        created_at=completed_at,
        blocked_reason=SpecificationBlockReason.NEEDS_USER if blocked else None,
        **draft.model_dump(),
    )
    target = Stage.BLOCKED if blocked else Stage.SPEC_READY
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id=_identifier("cmd", state.workflow_id, "specification-result"),
            task_id=state.task_id,
            actor_id=request.agent_id,
            target_stage=target,
            occurred_at=completed_at,
            artifact=artifact,
            charge=charge,
            reason=SpecificationBlockReason.NEEDS_USER.value if blocked else None,
        ),
        events,
    )
    return artifact, state, events


class SpecificationExecutor(Executor):
    """One tool-free structured PM call joined to deterministic domain transitions."""

    def __init__(
        self,
        provider: StructuredModelProvider,
        *,
        clock: Callable[[], UtcDateTime] | None = None,
    ) -> None:
        super().__init__(id="controlled_specification")
        self.provider = provider
        self.now = clock or (lambda: datetime.now(UTC))

    @handler
    async def specify(
        self,
        request: SpecificationRunRequest,
        ctx: WorkflowContext[Never, SpecificationRunResult],
    ) -> None:
        validate_pm_request(request)
        started_at = self.now()
        state, events = append_transition(
            request.state,
            TransitionCommand(
                command_id=_identifier("cmd", request.state.workflow_id, "specifying"),
                task_id=request.state.task_id,
                actor_id="workflow",
                target_stage=Stage.SPECIFYING,
                occurred_at=started_at,
            ),
            request.events,
        )
        invocation = await self.provider.generate(
            SpecificationDraft,
            system_prompt=pm_system_prompt(),
            user_prompt=_user_prompt(request.handoff),
        )
        completed_at = self.now()
        artifact, state, events = accept_specification_draft(
            request,
            state,
            events,
            invocation.value,
            charge=BudgetCharge(
                model_tokens=invocation.usage.total_tokens,
                wall_time_seconds=ceil(invocation.latency_ms / 1_000),
            ),
            completed_at=completed_at,
        )
        verify_event_chain(events, expected_state=state)
        await ctx.yield_output(
            SpecificationRunResult(
                artifact=artifact,
                state=state,
                events=events,
                model_call=model_call_record(invocation),
            )
        )


def build_specification_workflow(
    provider: StructuredModelProvider,
    *,
    clock: Callable[[], UtcDateTime] | None = None,
) -> Workflow:
    executor = SpecificationExecutor(provider, clock=clock)
    return WorkflowBuilder(start_executor=executor, output_from=[executor]).build()
