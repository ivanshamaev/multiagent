"""Minimal MAF code workflow joined to the deterministic domain reducer."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from hashlib import sha256
from math import ceil
from pathlib import Path
from typing import Never

from agent_framework import Executor, Workflow, WorkflowBuilder, WorkflowContext, handler

from contracts import (
    AnalysisFact,
    AnalysisFactKind,
    ArtifactReference,
    Evidence,
    EvidenceKind,
    RequirementsAnalysisReport,
    SpecificationDecision,
    TaskRequest,
    TaskSpecification,
)
from contracts.artifacts import TextTuple
from contracts.common import FrozenModel, Identifier, NonEmptyText, UtcDateTime
from orchestrator import (
    BudgetCharge,
    BudgetLimits,
    Stage,
    TransitionCommand,
    WorkflowEvent,
    WorkflowState,
    append_transition,
    initial_state,
    verify_event_chain,
)
from runtime.context import ContextBundle, build_scenario_context
from runtime.model_provider import (
    ModelCallRecord,
    StructuredModelProvider,
    model_call_record,
)
from runtime.scenario_harness import load_manifest

PM_INSTRUCTIONS_PATH = Path(__file__).resolve().parents[1] / "agents/pm/instructions.md"


class SpecificationDraft(FrozenModel):
    """Untrusted PM role content; workflow-controlled identity fields are intentionally absent."""

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
    task: TaskRequest
    context: ContextBundle
    workflow_id: Identifier
    correlation_id: Identifier
    agent_id: Identifier = "pm-agent"
    budget_limits: BudgetLimits


class SpecificationRunResult(FrozenModel):
    artifact: TaskSpecification
    state: WorkflowState
    events: tuple[WorkflowEvent, ...]
    model_call: ModelCallRecord


def _identifier(prefix: str, *parts: str) -> str:
    digest = sha256("\x00".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def _system_prompt() -> str:
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


def _user_prompt(task: TaskRequest, context: ContextBundle) -> str:
    return (
        "Convert this immutable task request into a testable specification. "
        "The workflow owns IDs, actor identity, timestamps and evidence.\n"
        f"Task request:\n{task.model_dump_json(exclude={'evidence'})}\n\n"
        f"Verified workspace context ({context.workspace_fingerprint}):\n{context.as_prompt()}"
    )


def prepare_scenario_specification_request(
    repository_root: Path,
    scenario_id: str,
    *,
    workflow_id: str,
    correlation_id: str,
    created_at: UtcDateTime | None = None,
    requested_state_root: Path | None = None,
) -> SpecificationRunRequest:
    """Create the production request only from a verified disposable scenario workspace."""

    manifest = load_manifest(repository_root, scenario_id)
    context = build_scenario_context(
        repository_root,
        scenario_id,
        requested_state_root=requested_state_root,
    )
    timestamp = created_at or datetime.now(UTC)
    task_id = f"scenario-{manifest.scenario_id}"
    return SpecificationRunRequest(
        task=TaskRequest(
            artifact_id=_identifier("request", workflow_id, task_id),
            task_id=task_id,
            producer_id="user",
            created_at=timestamp,
            title=f"Scenario {manifest.scenario_id}",
            description="Create a testable specification from the verified scenario context.",
        ),
        context=context,
        workflow_id=workflow_id,
        correlation_id=correlation_id,
        budget_limits=BudgetLimits(**manifest.budgets),
    )


class SpecificationExecutor(Executor):
    """MAF message adapter; all transition decisions remain in domain code."""

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
        state = initial_state(
            request.task,
            workflow_id=request.workflow_id,
            correlation_id=request.correlation_id,
            limits=request.budget_limits,
        )
        first_document = request.context.documents[0]
        discovery_evidence = Evidence(
            evidence_id=_identifier("evidence", request.workflow_id, "verified-context"),
            task_id=request.task.task_id,
            producer_id="context-builder",
            kind=EvidenceKind.ARTIFACT,
            source="verified-workspace-context",
            invocation=f"workspace_fingerprint={request.context.workspace_fingerprint}",
            exit_code=0,
            artifact=ArtifactReference(
                path=first_document.path,
                sha256=first_document.sha256,
                media_type="text/plain",
                size_bytes=first_document.size_bytes,
            ),
            occurred_at=request.task.created_at,
        )
        discovery = RequirementsAnalysisReport(
            artifact_id=_identifier("requirements-analysis", request.workflow_id, "compatibility"),
            task_id=request.task.task_id,
            producer_id="analyst-compatibility",
            created_at=request.task.created_at,
            facts=(
                AnalysisFact(
                    fact_id=_identifier("fact", request.workflow_id, "verified-context"),
                    kind=AnalysisFactKind.SOURCE,
                    statement="Verified scenario context is available for PM specification.",
                    evidence_ids=(discovery_evidence.evidence_id,),
                ),
            ),
            assumptions=(),
            open_questions=(),
            risks=("Compatibility input has not run autonomous data profiling.",),
            recommended_next_steps=("PM must validate semantics against the supplied context.",),
            evidence=(discovery_evidence,),
        )
        started_at = self.now()
        state, events = append_transition(
            state,
            TransitionCommand(
                command_id=_identifier("cmd", request.workflow_id, "analyzing"),
                task_id=request.task.task_id,
                actor_id="workflow",
                target_stage=Stage.ANALYZING,
                occurred_at=started_at,
            ),
            (),
        )
        state, events = append_transition(
            state,
            TransitionCommand(
                command_id=_identifier("cmd", request.workflow_id, "analysis-ready"),
                task_id=request.task.task_id,
                actor_id="analyst-compatibility",
                target_stage=Stage.ANALYSIS_READY,
                occurred_at=started_at,
                artifact=discovery,
            ),
            events,
        )
        state, events = append_transition(
            state,
            TransitionCommand(
                command_id=_identifier("cmd", request.workflow_id, "specifying"),
                task_id=request.task.task_id,
                actor_id="workflow",
                target_stage=Stage.SPECIFYING,
                occurred_at=started_at,
            ),
            events,
        )

        invocation = await self.provider.generate(
            SpecificationDraft,
            system_prompt=_system_prompt(),
            user_prompt=_user_prompt(request.task, request.context),
        )
        completed_at = self.now()
        draft = invocation.value
        artifact = TaskSpecification(
            artifact_id=_identifier("spec", request.workflow_id, request.task.task_id),
            task_id=request.task.task_id,
            producer_id=request.agent_id,
            created_at=completed_at,
            **draft.model_dump(),
        )
        target = (
            Stage.SPEC_READY if artifact.decision is SpecificationDecision.READY else Stage.BLOCKED
        )
        reason = "specification requires user input" if target is Stage.BLOCKED else None
        state, events = append_transition(
            state,
            TransitionCommand(
                command_id=_identifier("cmd", request.workflow_id, "specification-result"),
                task_id=request.task.task_id,
                actor_id=request.agent_id,
                target_stage=target,
                occurred_at=completed_at,
                artifact=artifact,
                charge=BudgetCharge(
                    model_tokens=invocation.usage.total_tokens,
                    wall_time_seconds=ceil(invocation.latency_ms / 1_000),
                ),
                reason=reason,
            ),
            events,
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
    """Build a caller-scoped graph workflow for one specification artifact."""

    executor = SpecificationExecutor(provider, clock=clock)
    return WorkflowBuilder(start_executor=executor, output_from=[executor]).build()
