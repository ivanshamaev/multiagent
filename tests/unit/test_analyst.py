from datetime import UTC, datetime, timedelta
from hashlib import sha256

import pytest
from pydantic import ValidationError

from contracts import (
    AnalysisFact,
    AnalysisFactKind,
    ArtifactReference,
    Evidence,
    EvidenceKind,
    RequirementsAnalysisReport,
    ToolCallEvidence,
    ToolCallStatus,
    ToolName,
)
from orchestrator import BudgetLimits, Stage
from policies import ToolUsage
from runtime.analyst import (
    AnalystBoundaryError,
    AnalystPhaseDraft,
    AnalystRunRequest,
    AnalystSynthesisDraft,
    ObservedFactDraft,
    accept_analyst_drafts,
    build_pm_requirements_handoff,
    seed_analyst_state,
)
from runtime.context import ContextBundle, ContextDocument
from runtime.model_provider import ModelUsage
from tests.workflow.factories import task_request

NOW = datetime(2026, 9, 13, 8, tzinfo=UTC)


def _request() -> AnalystRunRequest:
    content = "# task\n"
    return AnalystRunRequest(
        task=task_request(),
        context=ContextBundle(
            workspace_fingerprint="a" * 64,
            documents=(
                ContextDocument(
                    path="TASK.md",
                    content=content,
                    size_bytes=len(content.encode()),
                    sha256=sha256(content.encode()).hexdigest(),
                ),
            ),
            total_bytes=len(content.encode()),
        ),
        workflow_id="workflow-analyst",
        correlation_id="correlation-analyst",
        configuration_fingerprint="b" * 64,
        budget_limits=BudgetLimits(
            tool_calls=6,
            model_tokens=10_000,
            wall_time_seconds=300,
            rework_attempts=1,
        ),
    )


def _tool_evidence(evidence_id: str, tool: ToolName, *, task_id: str = "TASK-001"):
    return ToolCallEvidence(
        evidence_id=evidence_id,
        request_id=f"request-{evidence_id}",
        task_id=task_id,
        producer_id="tool-gateway",
        tool=tool,
        arguments_sha256="c" * 64,
        started_at=NOW,
        completed_at=NOW,
        status=ToolCallStatus.SUCCESS,
        exit_code=0,
        duration_ms=3,
        output_bytes=2,
        output=ArtifactReference(
            path=f"evidence/{evidence_id}.txt",
            sha256="d" * 64,
            media_type="text/plain",
            size_bytes=2,
        ),
    )


def _accepted():
    request = _request()
    state, events = seed_analyst_state(request, occurred_at=NOW)
    report, state, events = accept_analyst_drafts(
        request,
        state,
        events,
        (
            AnalystPhaseDraft(
                facts=(
                    ObservedFactDraft(
                        kind=AnalysisFactKind.SOURCE,
                        statement="raw.orders exists",
                    ),
                )
            ),
            AnalystPhaseDraft(
                facts=(
                    ObservedFactDraft(
                        kind=AnalysisFactKind.LINEAGE,
                        statement="raw.orders feeds analytics.fct_orders",
                    ),
                )
            ),
            AnalystPhaseDraft(
                facts=(
                    ObservedFactDraft(
                        kind=AnalysisFactKind.PROFILE,
                        statement="raw.orders contains four currencies",
                    ),
                )
            ),
        ),
        AnalystSynthesisDraft(
            assumptions=("Revenue remains separated by currency.",),
            open_questions=("Should late refunds restate prior dates?",),
            risks=("No FX source was observed.",),
            recommended_next_steps=("PM must resolve refund timing semantics.",),
        ),
        phase_evidence=(
            _tool_evidence("metadata", ToolName.DBT_LIST),
            _tool_evidence("lineage", ToolName.DBT_GET_LINEAGE_DEV),
            _tool_evidence("profile", ToolName.CLICKHOUSE_RUN_QUERY),
        ),
        phase_outputs=(
            "raw.orders exists and analytics.fct_orders exists",
            "raw.orders feeds analytics.fct_orders",
            "raw.orders contains four currencies",
        ),
        tool_usage=ToolUsage(completed_calls=3, elapsed_ms=100, output_bytes=6),
        model_usage=ModelUsage(total_tokens=40),
        model_latency_ms=1200,
        completed_at=NOW + timedelta(seconds=2),
    )
    return request, report, state, events


def test_analysis_is_accepted_before_pm_and_preserves_unknowns() -> None:
    request, report, state, events = _accepted()

    assert state.stage is Stage.ANALYSIS_READY
    assert [event.to_stage for event in events] == [Stage.ANALYZING, Stage.ANALYSIS_READY]
    assert state.budgets.used.tool_calls == 3
    assert all(fact.evidence_ids for fact in report.facts)
    handoff = build_pm_requirements_handoff(request, report, state)
    assert handoff.unresolved_questions == report.open_questions
    assert handoff.configuration_fingerprint == "b" * 64


def test_analysis_fact_must_reference_successful_attached_evidence() -> None:
    item = Evidence(
        evidence_id="evidence-failed",
        task_id="TASK-001",
        producer_id="tool-gateway",
        kind=EvidenceKind.QUERY,
        source="clickhouse.run_query",
        invocation="arguments_sha256=" + "e" * 64,
        exit_code=1,
        artifact=ArtifactReference(
            path="evidence/failed.txt",
            sha256="f" * 64,
            media_type="text/plain",
            size_bytes=0,
        ),
        occurred_at=NOW,
    )
    with pytest.raises(ValidationError, match="successful evidence"):
        RequirementsAnalysisReport(
            artifact_id="analysis-failed",
            task_id="TASK-001",
            producer_id="analyst-agent",
            created_at=NOW,
            facts=(
                AnalysisFact(
                    fact_id="fact-1",
                    kind=AnalysisFactKind.PROFILE,
                    statement="unsupported claim",
                    evidence_ids=("evidence-failed",),
                ),
            ),
            recommended_next_steps=("Ask PM.",),
            evidence=(item,),
        )


def test_cross_task_or_write_evidence_fails_closed() -> None:
    request = _request()
    state, events = seed_analyst_state(request, occurred_at=NOW)
    phase = AnalystPhaseDraft(
        facts=(ObservedFactDraft(kind=AnalysisFactKind.SOURCE, statement="observed"),)
    )
    synthesis = AnalystSynthesisDraft(recommended_next_steps=("continue",))
    with pytest.raises(AnalystBoundaryError, match="another task"):
        accept_analyst_drafts(
            request,
            state,
            events,
            (phase,),
            synthesis,
            phase_evidence=(_tool_evidence("wrong-task", ToolName.DBT_LIST, task_id="TASK-OTHER"),),
            phase_outputs=("observed",),
            tool_usage=ToolUsage(completed_calls=1),
            model_usage=ModelUsage(),
            model_latency_ms=0,
            completed_at=NOW + timedelta(seconds=1),
        )

    with pytest.raises(AnalystBoundaryError, match="non-read-only"):
        accept_analyst_drafts(
            request,
            state,
            events,
            (phase,),
            synthesis,
            phase_evidence=(_tool_evidence("write", ToolName.WORKSPACE_WRITE_FILE),),
            phase_outputs=("observed",),
            tool_usage=ToolUsage(completed_calls=1),
            model_usage=ModelUsage(),
            model_latency_ms=0,
            completed_at=NOW + timedelta(seconds=1),
        )


def test_identity_collision_and_unaccepted_report_handoff_fail_closed() -> None:
    request, report, state, _ = _accepted()
    with pytest.raises(AnalystBoundaryError, match="accepted analysis"):
        build_pm_requirements_handoff(
            request,
            report.model_copy(update={"artifact_id": "foreign-report"}),
            state,
        )
    collision = request.model_copy(update={"agent_id": "pm-agent"})
    with pytest.raises(AnalystBoundaryError, match="identity"):
        seed_analyst_state(collision, occurred_at=NOW)
