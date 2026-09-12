import asyncio
from pathlib import Path

import pytest

from contracts import QADecision
from orchestrator import Stage, verify_event_chain
from policies import load_capability_profile
from runtime.data_engineer import prepare_data_engineer_request
from runtime.data_engineer_workflow import QAAssessmentResult, build_phased_data_engineer_workflow
from runtime.model_provider import (
    ModelCallRecord,
    ModelInvocation,
    ModelOutputValidationError,
    ModelUsage,
)
from runtime.qa import prepare_qa_request
from runtime.qa_workflow import AutonomousQAError, QAWorkflowInput, build_qa_workflow
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

ROOT = Path(__file__).resolve().parents[2]
DE_PROFILE = ROOT / "policies/profiles/data_engineer_v1.json"
QA_PROFILE = ROOT / "policies/profiles/qa_v1.json"


class _OfflineQA:
    def __init__(self, decision: QADecision) -> None:
        self.phase = 0
        self.decision = decision

    async def generate(self, response_model, *, system_prompt: str, user_prompt: str):
        raise AssertionError("QA must use its phase tool")

    async def generate_with_tools(
        self,
        response_model,
        *,
        system_prompt: str,
        user_prompt: str,
        tools,
    ):
        self.phase += 1
        exposed = {item.name: item for item in tools}
        assert "immutable_specification" in user_prompt
        if self.phase == 1:
            assert set(exposed) == {"workspace_read_file"}
            await exposed["workspace_read_file"].invoke(
                arguments={"path": "platform/dbt/models/marts/fct_net_revenue.sql"}
            )
            value = response_model(
                findings=("Candidate aggregates revenue at the requested grain.",),
                probe_strategy="Search for semantic counterexample rows.",
            )
        else:
            assert self.phase == 2
            assert set(exposed) == {"qa_run_public_probe"}
            await exposed["qa_run_public_probe"].invoke(arguments={})
            payload = {
                "decision": self.decision,
                "check_name": "semantic counterexample probe",
                "summary": (
                    "QA found a refund-date counterexample."
                    if self.decision is QADecision.FAIL
                    else "QA probe found no counterexample."
                ),
            }
            if self.decision is QADecision.FAIL:
                payload.update(
                    {
                        "defect_description": (
                            "A late refund is attributed to the refund date instead of order date."
                        ),
                        "acceptance_criterion": "refunds inherit the original order date",
                        "severity": "high",
                    }
                )
            value = response_model(**payload)
        marker = str(self.phase)
        return ModelInvocation(
            value=value,
            model_id="fake/offline-qa",
            usage=ModelUsage(input_tokens=10, output_tokens=5, total_tokens=15),
            latency_ms=10,
            finish_reason="stop",
            request_sha256=marker * 64,
            response_sha256=("e" if self.phase == 1 else "f") * 64,
        )


class _InvalidProbeQA(_OfflineQA):
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
        exposed = {item.name: item for item in tools}
        await exposed["qa_run_public_probe"].invoke(arguments={})
        raise ModelOutputValidationError(
            ("json_invalid",),
            ModelCallRecord(
                model_id="fake/invalid-qa",
                usage=ModelUsage(input_tokens=7, output_tokens=3, total_tokens=10),
                latency_ms=11,
                finish_reason="stop",
                request_sha256="a" * 64,
                response_sha256="b" * 64,
            ),
        )


def _validated_de_result(manifest):
    de_profile = load_capability_profile(DE_PROFILE)
    gateway = MCPToolGateway(
        de_profile,
        _UnusedMCP(),
        _UnusedMCP(),
        ToolEvidenceStore(ROOT, ROOT / ".scenario-state"),
        WorkspaceToolAdapter(ROOT, manifest, de_profile),
    )
    connected = ConnectedDataEngineerMCPTools(
        DataEngineerMCPTools(
            gateway,
            task_id="scenario-net-revenue",
            actor_id="data-engineer-agent",
        ).tools,
        gateway,
    )
    request = prepare_data_engineer_request(
        ROOT,
        "net-revenue",
        workflow_id="workflow-offline-quality",
        correlation_id="correlation-offline-quality",
    )
    workflow = build_phased_data_engineer_workflow(
        _OfflinePhasedDataEngineer(),  # type: ignore[arg-type]
        connected,
        repository_root=ROOT,
        scenario_id="net-revenue",
        validator_runner=_PassingValidator(),
    )
    return asyncio.run(workflow.run(request)).get_outputs()[0]


def _run_qa(de_result, decision: QADecision):
    profile = load_capability_profile(QA_PROFILE)
    clickhouse = _UnusedMCP()
    gateway = MCPToolGateway(
        profile,
        clickhouse,
        _UnusedMCP(),
        ToolEvidenceStore(ROOT, ROOT / ".scenario-state"),
        WorkspaceToolAdapter(ROOT, load_manifest(ROOT, "net-revenue"), profile),
    )
    connected = ConnectedDataEngineerMCPTools(
        DataEngineerMCPTools(
            gateway,
            task_id="scenario-net-revenue",
            actor_id="qa-agent",
            role="qa",
        ).tools,
        gateway,
    )
    request = prepare_qa_request(
        ROOT,
        "net-revenue",
        workflow_id=de_result.state.workflow_id,
    )
    provider = _OfflineQA(decision)
    workflow = build_qa_workflow(provider, connected)  # type: ignore[arg-type]
    result = asyncio.run(
        workflow.run(
            QAWorkflowInput(
                request=request,
                state=de_result.state,
                events=de_result.events,
            )
        )
    ).get_outputs()[0]
    return provider, clickhouse, result


def test_validated_candidate_reaches_qa_passed_with_read_only_evidence() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset_workspace(ROOT, manifest)
    try:
        de_result = _validated_de_result(manifest)
        provider, clickhouse, result = _run_qa(de_result, QADecision.PASS)

        assert provider.phase == 2
        assert result.state.stage is Stage.QA_PASSED
        assert result.report.decision is QADecision.PASS
        assert result.report.implementation_author_id == "data-engineer-agent"
        assert result.report.producer_id == "qa-agent"
        assert result.state.budgets.used.tool_calls == 5
        assert result.state.budgets.used.model_tokens == 75
        assert [item.tool.value for item in result.tool_evidence] == [
            "workspace.read_file",
            "clickhouse.run_query",
        ]
        assert clickhouse.calls == ["run_query"]
        verify_event_chain(result.events, expected_state=result.state)
    finally:
        reset_workspace(ROOT, manifest)


def test_qa_defect_enters_shared_bounded_rework_without_write_access() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset_workspace(ROOT, manifest)
    try:
        de_result = _validated_de_result(manifest)
        _, _, result = _run_qa(de_result, QADecision.FAIL)

        assert result.state.stage is Stage.REWORK
        assert result.state.budgets.used.rework_attempts == 1
        assert result.report.defects[0].evidence_ids == tuple(
            item.evidence_id for item in result.report.evidence
        )
        assert result.report.defects[0].acceptance_criterion == (
            "refunds inherit the original order date"
        )
        assert all(item.tool.value != "workspace.write_file" for item in result.tool_evidence)
    finally:
        reset_workspace(ROOT, manifest)


def test_invalid_qa_probe_output_is_retained_safely_and_fails_closed() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset_workspace(ROOT, manifest)
    try:
        de_result = _validated_de_result(manifest)
        profile = load_capability_profile(QA_PROFILE)
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
                task_id="scenario-net-revenue",
                actor_id="qa-agent",
                role="qa",
            ).tools,
            gateway,
        )
        request = prepare_qa_request(
            ROOT,
            "net-revenue",
            workflow_id=de_result.state.workflow_id,
        )

        with pytest.raises(AutonomousQAError) as captured:
            asyncio.run(
                build_qa_workflow(_InvalidProbeQA(QADecision.PASS), connected).run(  # type: ignore[arg-type]
                    QAWorkflowInput(
                        request=request,
                        state=de_result.state,
                        events=de_result.events,
                    )
                )
            )

        assert captured.value.code == "qa_probe_model_failure"
        assert len(captured.value.model_calls) == 2
        assert captured.value.model_calls[-1].usage.total_tokens == 10
        assert len(captured.value.tool_evidence) == 2
        assert de_result.state.stage is Stage.VALIDATED
    finally:
        reset_workspace(ROOT, manifest)


def test_qa_failure_drives_de_repair_full_validation_and_qa_pass() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset_workspace(ROOT, manifest)
    de_profile = load_capability_profile(DE_PROFILE)
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
    qa_decisions = iter((QADecision.FAIL, QADecision.PASS))
    qa_results = []

    async def assess(state, events):
        qa_profile = load_capability_profile(QA_PROFILE)
        qa_gateway = MCPToolGateway(
            qa_profile,
            _UnusedMCP(),
            _UnusedMCP(),
            ToolEvidenceStore(ROOT, ROOT / ".scenario-state"),
            WorkspaceToolAdapter(ROOT, manifest, qa_profile),
        )
        qa_connected = ConnectedDataEngineerMCPTools(
            DataEngineerMCPTools(
                qa_gateway,
                task_id=state.task_id,
                actor_id="qa-agent",
                role="qa",
            ).tools,
            qa_gateway,
        )
        qa_request = prepare_qa_request(
            ROOT,
            "net-revenue",
            workflow_id=state.workflow_id,
        )
        qa_workflow = build_qa_workflow(_OfflineQA(next(qa_decisions)), qa_connected)  # type: ignore[arg-type]
        qa_result = (
            await qa_workflow.run(QAWorkflowInput(request=qa_request, state=state, events=events))
        ).get_outputs()[0]
        qa_results.append(qa_result)
        return QAAssessmentResult(
            report=qa_result.report,
            state=qa_result.state,
            events=qa_result.events,
        )

    try:
        request = prepare_data_engineer_request(
            ROOT,
            "net-revenue",
            workflow_id="workflow-offline-full-quality-loop",
            correlation_id="correlation-offline-full-quality-loop",
        )
        workflow = build_phased_data_engineer_workflow(
            de_provider,  # type: ignore[arg-type]
            de_connected,
            repository_root=ROOT,
            scenario_id="net-revenue",
            validator_runner=validator,
            qa_assessor=assess,
        )
        result = asyncio.run(workflow.run(request)).get_outputs()[0]

        assert result.state.stage is Stage.QA_PASSED
        assert result.qa_report is not None
        assert result.qa_report.decision is QADecision.PASS
        assert de_provider.phase == 4
        assert len(qa_results) == 2
        assert [item.report.decision for item in qa_results] == [
            QADecision.FAIL,
            QADecision.PASS,
        ]
        assert len(validator.calls) == 8
        assert result.state.budgets.used.rework_attempts == 1
        assert result.state.budgets.used.tool_calls == 8
        assert result.state.budgets.used.model_tokens == 120
        stages = [event.requested_stage for event in result.events]
        first_qa = stages.index(Stage.QA)
        assert stages[first_qa : first_qa + 9] == [
            Stage.QA,
            Stage.REWORK,
            Stage.IMPLEMENTING,
            Stage.IMPLEMENTED,
            Stage.VALIDATING,
            Stage.VALIDATED,
            Stage.QA,
            Stage.QA_PASSED,
        ]
        verify_event_chain(result.events, expected_state=result.state)
    finally:
        reset_workspace(ROOT, manifest)
