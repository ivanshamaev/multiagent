import asyncio
from pathlib import Path

import pytest

from contracts import QADecision, ReviewDecision
from orchestrator import Stage, verify_event_chain
from policies import ToolUsage, load_capability_profile
from runtime.data_engineer import prepare_data_engineer_request
from runtime.data_engineer_workflow import (
    QAAssessmentResult,
    ReviewerAssessmentResult,
    build_phased_data_engineer_workflow,
)
from runtime.model_provider import (
    ModelCallRecord,
    ModelInvocation,
    ModelOutputValidationError,
    ModelUsage,
)
from runtime.qa import prepare_qa_request
from runtime.qa_workflow import QAWorkflowInput, build_qa_workflow
from runtime.reviewer import (
    ReviewerBoundaryError,
    ReviewerDraft,
    accept_reviewer_draft,
    prepare_reviewer_request,
)
from runtime.reviewer_workflow import (
    AutonomousReviewerError,
    ReviewerWorkflowInput,
    build_reviewer_workflow,
)
from runtime.scenario_harness import load_manifest, reset_workspace
from runtime.tools import (
    ConnectedDataEngineerMCPTools,
    DataEngineerMCPTools,
    MCPToolGateway,
    ToolEvidenceStore,
    WorkspaceToolAdapter,
)
from tests.integration.test_data_engineer_workflow import (
    _OfflinePhasedDataEngineer,
    _PassingValidator,
    _UnusedMCP,
)
from tests.integration.test_qa_workflow import (
    _OfflineQA,
    _run_qa,
    _validated_de_result,
)

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "policies/profiles/reviewer_v1.json"


class _OfflineReviewer:
    def __init__(self, criteria: tuple[str, ...], decision: ReviewDecision) -> None:
        self.criteria = criteria
        self.decision = decision
        self.phase = 0

    async def generate(self, response_model, *, system_prompt: str, user_prompt: str):
        raise AssertionError("Reviewer must use exact phase reads")

    async def generate_with_tools(
        self,
        response_model,
        *,
        system_prompt: str,
        user_prompt: str,
        tools,
    ):
        self.phase += 1
        read = {item.name: item for item in tools}["workspace_read_file"]
        if self.phase == 1:
            await read.invoke(arguments={"path": "platform/dbt/models/marts/fct_net_revenue.sql"})
            value = response_model(
                observations=(
                    "Physical table, explicit projections, signed integer arithmetic, and "
                    "deterministic tie-breaks are present.",
                ),
                findings=("The model uses explicit projections and deterministic tie-breaks.",),
                risks=(),
            )
        else:
            await read.invoke(
                arguments={"path": "platform/dbt/tests/assert_fct_net_revenue_contract.sql"}
            )
            criteria = [
                {
                    "criterion": item,
                    "status": "fail"
                    if self.decision is ReviewDecision.REQUEST_CHANGES and index == 0
                    else "pass",
                    "rationale": "Candidate and test evidence cover this criterion.",
                }
                for index, item in enumerate(self.criteria)
            ]
            findings = []
            if self.decision is ReviewDecision.REQUEST_CHANGES:
                findings = [
                    {
                        "severity": "high",
                        "description": (
                            "The physical relation is hard-coded instead of using dbt source."
                        ),
                        "acceptance_criterion": self.criteria[0],
                    }
                ]
            value = response_model(
                decision=self.decision,
                acceptance_criteria=criteria,
                findings=findings,
                risks=(),
                summary="Review completed from both candidate artifacts.",
            )
        marker = str(self.phase)
        return ModelInvocation(
            value=value,
            model_id="fake/offline-reviewer",
            usage=ModelUsage(input_tokens=10, output_tokens=5, total_tokens=15),
            latency_ms=10,
            finish_reason="stop",
            request_sha256=marker * 64,
            response_sha256=("c" if self.phase == 1 else "d") * 64,
        )


class _InvalidReviewer(_OfflineReviewer):
    async def generate_with_tools(
        self,
        response_model,
        *,
        system_prompt: str,
        user_prompt: str,
        tools,
    ):
        if self.phase == 0:
            return await super().generate_with_tools(
                response_model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                tools=tools,
            )
        read = {item.name: item for item in tools}["workspace_read_file"]
        await read.invoke(
            arguments={"path": "platform/dbt/tests/assert_fct_net_revenue_contract.sql"}
        )
        raise ModelOutputValidationError(
            ("json_invalid",),
            ModelCallRecord(
                model_id="fake/invalid-reviewer",
                usage=ModelUsage(input_tokens=7, output_tokens=3, total_tokens=10),
                latency_ms=11,
                finish_reason="stop",
                request_sha256="a" * 64,
                response_sha256="b" * 64,
            ),
        )


def _run_reviewer(
    qa_result,
    decision: ReviewDecision,
    *,
    agent_id: str = "reviewer-agent",
    provider=None,
):
    manifest = load_manifest(ROOT, "net-revenue")
    profile = load_capability_profile(PROFILE)
    gateway = MCPToolGateway(
        profile,
        _UnusedMCP(),
        _UnusedMCP(),
        ToolEvidenceStore(ROOT, ROOT / ".scenario-state"),
        WorkspaceToolAdapter(ROOT, manifest, profile),
    )
    connected = ConnectedDataEngineerMCPTools(
        DataEngineerMCPTools(
            gateway,
            task_id=qa_result.state.task_id,
            actor_id=agent_id,
            role="reviewer",
        ).tools,
        gateway,
    )
    request = prepare_reviewer_request(
        ROOT,
        "net-revenue",
        workflow_id=qa_result.state.workflow_id,
        qa_report=qa_result.report,
    ).model_copy(update={"agent_id": agent_id})
    criteria = tuple(request.specification.specification.acceptance_criteria)
    active_provider = provider or _OfflineReviewer(criteria, decision)
    output = asyncio.run(
        build_reviewer_workflow(
            active_provider,  # type: ignore[arg-type]
            connected,
        ).run(
            ReviewerWorkflowInput(
                request=request,
                state=qa_result.state,
                events=qa_result.events,
            )
        )
    )
    return output.get_outputs()[0]


def test_qa_passed_candidate_reaches_done_through_independent_reviewer() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset_workspace(ROOT, manifest)
    try:
        de_result = _validated_de_result(manifest)
        _, _, qa_result = _run_qa(de_result, QADecision.PASS)
        result = _run_reviewer(qa_result, ReviewDecision.APPROVE)

        assert result.state.stage is Stage.DONE
        assert result.report.decision is ReviewDecision.APPROVE
        assert result.report.producer_id == "reviewer-agent"
        assert result.report.implementation_author_id == "data-engineer-agent"
        assert len(result.report.acceptance_criteria) == 8
        assert [item.tool.value for item in result.tool_evidence] == [
            "workspace.read_file",
            "workspace.read_file",
        ]
        verify_event_chain(result.events, expected_state=result.state)
    finally:
        reset_workspace(ROOT, manifest)


def test_reviewer_request_changes_consumes_rework_and_cannot_write() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset_workspace(ROOT, manifest)
    try:
        de_result = _validated_de_result(manifest)
        _, _, qa_result = _run_qa(de_result, QADecision.PASS)
        result = _run_reviewer(qa_result, ReviewDecision.REQUEST_CHANGES)

        assert result.state.stage is Stage.REWORK
        assert result.state.budgets.used.rework_attempts == 1
        assert result.report.findings[0].severity.value == "high"
        assert all(item.tool.value == "workspace.read_file" for item in result.tool_evidence)
    finally:
        reset_workspace(ROOT, manifest)


def test_reviewer_rejects_qa_identity_and_missing_criterion() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset_workspace(ROOT, manifest)
    try:
        de_result = _validated_de_result(manifest)
        _, _, qa_result = _run_qa(de_result, QADecision.PASS)
        with pytest.raises(ReviewerBoundaryError, match="independent"):
            _run_reviewer(qa_result, ReviewDecision.APPROVE, agent_id="qa-agent")

        request = prepare_reviewer_request(
            ROOT,
            "net-revenue",
            workflow_id=qa_result.state.workflow_id,
            qa_report=qa_result.report,
        )
        criteria = tuple(request.specification.specification.acceptance_criteria)
        draft = ReviewerDraft(
            decision="approve",
            acceptance_criteria=tuple(
                {
                    "criterion": item,
                    "status": "pass",
                    "rationale": "Covered.",
                }
                for item in criteria[:-1]
            ),
            summary="Incomplete criterion set.",
        )
        with pytest.raises(ReviewerBoundaryError, match="every immutable criterion"):
            accept_reviewer_draft(
                request,
                qa_result.state,
                qa_result.events,
                draft,
                tool_evidence=qa_result.tool_evidence[:1],
                tool_usage=ToolUsage(),
                model_usage=ModelUsage(input_tokens=1, output_tokens=1, total_tokens=2),
                model_latency_ms=1,
            )
    finally:
        reset_workspace(ROOT, manifest)


def test_invalid_reviewer_output_fails_closed_with_safe_telemetry() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset_workspace(ROOT, manifest)
    try:
        de_result = _validated_de_result(manifest)
        _, _, qa_result = _run_qa(de_result, QADecision.PASS)
        request = prepare_reviewer_request(
            ROOT,
            "net-revenue",
            workflow_id=qa_result.state.workflow_id,
            qa_report=qa_result.report,
        )
        criteria = tuple(request.specification.specification.acceptance_criteria)
        with pytest.raises(AutonomousReviewerError) as captured:
            _run_reviewer(
                qa_result,
                ReviewDecision.APPROVE,
                provider=_InvalidReviewer(criteria, ReviewDecision.APPROVE),
            )

        assert captured.value.code == "reviewer_test_decision_failure"
        assert len(captured.value.model_calls) == 2
        assert captured.value.model_calls[-1].usage.total_tokens == 10
        assert len(captured.value.tool_evidence) == 2
        assert qa_result.state.stage is Stage.QA_PASSED
    finally:
        reset_workspace(ROOT, manifest)


def test_review_changes_repeat_validator_qa_and_reviewer_before_done() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset_workspace(ROOT, manifest)
    de_profile = load_capability_profile(ROOT / "policies/profiles/data_engineer_v1.json")
    de_gateway = MCPToolGateway(
        de_profile,
        _UnusedMCP(),
        _UnusedMCP(),
        ToolEvidenceStore(ROOT, ROOT / ".scenario-state"),
        WorkspaceToolAdapter(ROOT, manifest, de_profile),
    )
    de_connected = ConnectedDataEngineerMCPTools(
        DataEngineerMCPTools(
            de_gateway,
            task_id="scenario-net-revenue",
            actor_id="data-engineer-agent",
        ).tools,
        de_gateway,
    )
    de_provider = _OfflinePhasedDataEngineer()
    validator = _PassingValidator()
    review_decisions = iter((ReviewDecision.REQUEST_CHANGES, ReviewDecision.APPROVE))

    async def assess_qa(state, events):
        qa_profile = load_capability_profile(ROOT / "policies/profiles/qa_v1.json")
        qa_gateway = MCPToolGateway(
            qa_profile,
            _UnusedMCP(),
            _UnusedMCP(),
            ToolEvidenceStore(ROOT, ROOT / ".scenario-state"),
            WorkspaceToolAdapter(ROOT, manifest, qa_profile),
        )
        connected = ConnectedDataEngineerMCPTools(
            DataEngineerMCPTools(
                qa_gateway,
                task_id=state.task_id,
                actor_id="qa-agent",
                role="qa",
            ).tools,
            qa_gateway,
        )
        request = prepare_qa_request(
            ROOT,
            "net-revenue",
            workflow_id=state.workflow_id,
        )
        output = await build_qa_workflow(
            _OfflineQA(QADecision.PASS),  # type: ignore[arg-type]
            connected,
        ).run(QAWorkflowInput(request=request, state=state, events=events))
        result = output.get_outputs()[0]
        return QAAssessmentResult(
            report=result.report,
            state=result.state,
            events=result.events,
        )

    async def assess_reviewer(state, events, qa_report):
        profile = load_capability_profile(PROFILE)
        gateway = MCPToolGateway(
            profile,
            _UnusedMCP(),
            _UnusedMCP(),
            ToolEvidenceStore(ROOT, ROOT / ".scenario-state"),
            WorkspaceToolAdapter(ROOT, manifest, profile),
        )
        connected = ConnectedDataEngineerMCPTools(
            DataEngineerMCPTools(
                gateway,
                task_id=state.task_id,
                actor_id="reviewer-agent",
                role="reviewer",
            ).tools,
            gateway,
        )
        request = prepare_reviewer_request(
            ROOT,
            "net-revenue",
            workflow_id=state.workflow_id,
            qa_report=qa_report,
        )
        criteria = tuple(request.specification.specification.acceptance_criteria)
        output = await build_reviewer_workflow(
            _OfflineReviewer(criteria, next(review_decisions)),  # type: ignore[arg-type]
            connected,
        ).run(ReviewerWorkflowInput(request=request, state=state, events=events))
        result = output.get_outputs()[0]
        return ReviewerAssessmentResult(
            report=result.report,
            state=result.state,
            events=result.events,
        )

    try:
        request = prepare_data_engineer_request(
            ROOT,
            "net-revenue",
            workflow_id="workflow-offline-review-rework",
            correlation_id="correlation-offline-review-rework",
        )
        workflow = build_phased_data_engineer_workflow(
            de_provider,  # type: ignore[arg-type]
            de_connected,
            repository_root=ROOT,
            scenario_id="net-revenue",
            validator_runner=validator,
            qa_assessor=assess_qa,
            reviewer_assessor=assess_reviewer,
        )
        result = asyncio.run(workflow.run(request)).get_outputs()[0]

        assert result.state.stage is Stage.DONE
        assert result.review_report is not None
        assert result.review_report.decision is ReviewDecision.APPROVE
        assert de_provider.phase == 4
        assert len(validator.calls) == 8
        stages = [event.requested_stage for event in result.events]
        first_review = stages.index(Stage.REVIEW)
        assert stages[first_review : first_review + 10] == [
            Stage.REVIEW,
            Stage.REWORK,
            Stage.IMPLEMENTING,
            Stage.IMPLEMENTED,
            Stage.VALIDATING,
            Stage.VALIDATED,
            Stage.QA,
            Stage.QA_PASSED,
            Stage.REVIEW,
            Stage.DONE,
        ]
        verify_event_chain(result.events, expected_state=result.state)
    finally:
        reset_workspace(ROOT, manifest)
