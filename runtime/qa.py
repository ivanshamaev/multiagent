"""Trusted boundary for the independent read-only QA role."""

from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from math import ceil
from pathlib import Path
from typing import Self

from pydantic import model_validator

from contracts import (
    CheckResult,
    CheckStatus,
    Defect,
    Evidence,
    EvidenceKind,
    QADecision,
    QAReport,
    ScenarioSpecification,
    Severity,
    ToolCallEvidence,
    ToolCallStatus,
    ToolName,
)
from contracts.artifacts import RequiredTextTuple
from contracts.common import FrozenModel, Identifier, NonEmptyText, ShortText, UtcDateTime
from orchestrator import (
    BudgetCharge,
    Stage,
    TransitionCommand,
    WorkflowEvent,
    WorkflowState,
    append_transition,
    verify_event_chain,
)
from policies import ToolUsage
from runtime.context import ContextBundle, build_scenario_context
from runtime.model_provider import ModelUsage
from runtime.specification import load_scenario_specification

QA_INSTRUCTIONS_PATH = Path(__file__).resolve().parents[1] / "agents/qa/instructions.md"
QA_CONTEXT_PATHS = (
    "TASK.md",
    "platform/dbt/models/marts/fct_orders.sql",
    "platform/dbt/models/marts/fct_net_revenue.sql",
    "platform/dbt/models/staging/sources.yml",
    "platform/dbt/tests/assert_fct_net_revenue_contract.sql",
)
QA_READ_ONLY_TOOLS = frozenset(
    {
        ToolName.WORKSPACE_READ_FILE,
        ToolName.CLICKHOUSE_LIST_TABLES,
        ToolName.CLICKHOUSE_RUN_QUERY,
        ToolName.DBT_SHOW,
        ToolName.DBT_LIST,
        ToolName.DBT_GET_LINEAGE_DEV,
        ToolName.DBT_GET_NODE_DETAILS_DEV,
    }
)
QA_SEMANTIC_PROBE_SQL = """WITH
deduplicated_attribution AS (
    SELECT
        attribution_event_id,
        any(order_id) AS attributed_order_id,
        argMax(ifNull(acquisition_channel, 'unknown'), attributed_at) AS attributed_channel,
        max(attributed_at) AS latest_attributed_at
    FROM raw.marketing_attribution
    GROUP BY attribution_event_id
),
attribution_by_order AS (
    SELECT
        attributed_order_id AS order_id,
        argMax(
            ifNull(attributed_channel, 'unknown'),
            tuple(latest_attributed_at, attribution_event_id)
        ) AS acquisition_channel
    FROM deduplicated_attribution
    GROUP BY attributed_order_id
),
expected_components AS (
    SELECT
        orders.order_date AS order_date,
        orders.country AS country,
        ifNull(attribution.acquisition_channel, 'unknown') AS acquisition_channel,
        orders.currency AS currency,
        sum(toInt64(orders.successful_payment_amount_cents)) AS expected_gross,
        sum(toInt64(orders.successful_refund_amount_cents)) AS expected_refunds
    FROM analytics.fct_orders AS orders
    LEFT JOIN attribution_by_order AS attribution USING (order_id)
    GROUP BY order_date, country, acquisition_channel, currency
),
expected AS (
    SELECT
        order_date,
        country,
        acquisition_channel,
        currency,
        expected_gross AS gross_payment_amount_cents,
        expected_refunds AS successful_refund_amount_cents,
        expected_gross - expected_refunds AS net_revenue_cents
    FROM expected_components
),
missing AS (
    SELECT * FROM expected
    EXCEPT DISTINCT
    SELECT * FROM analytics.fct_net_revenue
),
unexpected AS (
    SELECT * FROM analytics.fct_net_revenue
    EXCEPT DISTINCT
    SELECT * FROM expected
)
SELECT *
FROM (
    SELECT 'missing' AS issue, * FROM missing
    UNION ALL
    SELECT 'unexpected' AS issue, * FROM unexpected
) AS differences
LIMIT 100"""


class QABoundaryError(RuntimeError):
    """Untrusted QA output or evidence crossed the role boundary."""


class QAInspectionDraft(FrozenModel):
    """Minimal output from the candidate-inspection phase."""

    findings: RequiredTextTuple
    probe_strategy: NonEmptyText


class QADraft(FrozenModel):
    """Untrusted QA decision without identity or evidence references."""

    decision: QADecision
    check_name: ShortText
    summary: NonEmptyText
    defect_description: NonEmptyText | None = None
    acceptance_criterion: ShortText | None = None
    severity: Severity | None = None

    @model_validator(mode="after")
    def validate_decision_fields(self) -> Self:
        defect_fields = (
            self.defect_description,
            self.acceptance_criterion,
            self.severity,
        )
        if self.decision is QADecision.FAIL and any(item is None for item in defect_fields):
            raise ValueError("failing QA draft requires a complete defect")
        if self.decision is not QADecision.FAIL and any(item is not None for item in defect_fields):
            raise ValueError("only failing QA draft may contain a defect")
        return self


class QARunRequest(FrozenModel):
    specification: ScenarioSpecification
    context: ContextBundle
    workflow_id: Identifier
    agent_id: Identifier = "qa-agent"


def _identifier(prefix: str, *parts: str) -> str:
    digest = sha256("\x00".join(parts).encode()).hexdigest()[:24]
    return f"{prefix}-{digest}"


def qa_system_prompt() -> str:
    """Load bounded trusted role instructions without following a symlink."""

    path = QA_INSTRUCTIONS_PATH
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("QA instructions must be a regular repository file")
    contents = path.read_bytes()
    if not 1 <= len(contents) <= 12_000:
        raise RuntimeError("QA instructions exceed the trusted size boundary")
    try:
        instructions = contents.decode("utf-8").strip()
    except UnicodeDecodeError:
        raise RuntimeError("QA instructions must be UTF-8") from None
    if not instructions:
        raise RuntimeError("QA instructions must not be empty")
    return instructions


def qa_user_prompt(request: QARunRequest) -> str:
    """Separate the immutable specification from untrusted candidate context."""

    specification = request.specification.specification.model_dump_json(exclude={"evidence"})
    return (
        "Independently assess this validated candidate. Return only the requested structured "
        "draft after using the phase tool.\n"
        f"<immutable_specification>{specification}</immutable_specification>\n"
        f'<untrusted_candidate_context fingerprint="{request.context.workspace_fingerprint}">\n'
        f"{request.context.as_prompt()}\n"
        "</untrusted_candidate_context>"
    )


def prepare_qa_request(
    repository_root: Path,
    scenario_id: str,
    *,
    workflow_id: str,
    requested_state_root: Path | None = None,
) -> QARunRequest:
    """Build QA input from the verified candidate and frozen human specification."""

    specification = load_scenario_specification(
        repository_root,
        scenario_id,
        requested_state_root=requested_state_root,
    )
    context = build_scenario_context(
        repository_root,
        scenario_id,
        relative_paths=QA_CONTEXT_PATHS,
        requested_state_root=requested_state_root,
    )
    return QARunRequest(
        specification=specification,
        context=context,
        workflow_id=workflow_id,
    )


def _domain_evidence(item: ToolCallEvidence) -> Evidence:
    if item.status is not ToolCallStatus.SUCCESS or item.output is None:
        raise QABoundaryError("QA evidence contains a non-success tool outcome")
    if item.tool not in QA_READ_ONLY_TOOLS:
        raise QABoundaryError("QA evidence contains a non-read-only tool")
    kind = (
        EvidenceKind.QUERY
        if item.tool in {ToolName.CLICKHOUSE_RUN_QUERY, ToolName.DBT_SHOW}
        else EvidenceKind.ARTIFACT
        if item.tool is ToolName.WORKSPACE_READ_FILE
        else EvidenceKind.COMMAND
    )
    return Evidence(
        evidence_id=item.evidence_id,
        task_id=item.task_id,
        producer_id=item.producer_id,
        kind=kind,
        source=item.tool.value,
        invocation=f"arguments_sha256={item.arguments_sha256}",
        exit_code=0,
        artifact=item.output,
        occurred_at=item.completed_at,
    )


def accept_qa_draft(
    request: QARunRequest,
    state: WorkflowState,
    events: tuple[WorkflowEvent, ...],
    draft: QADraft,
    *,
    tool_evidence: tuple[ToolCallEvidence, ...],
    tool_usage: ToolUsage,
    model_usage: ModelUsage,
    model_latency_ms: int,
    completed_at: UtcDateTime | None = None,
) -> tuple[QAReport, WorkflowState, tuple[WorkflowEvent, ...]]:
    """Create an evidence-backed QA report and let the reducer choose the branch."""

    if state.stage is not Stage.VALIDATED:
        raise QABoundaryError("QA requires a validated workflow state")
    if state.implementation_author_id is None:
        raise QABoundaryError("QA requires an implementation author")
    if request.specification.specification.task_id != state.task_id:
        raise QABoundaryError("QA request belongs to another task")
    if request.workflow_id != state.workflow_id:
        raise QABoundaryError("QA request belongs to another workflow")
    if request.agent_id == state.implementation_author_id:
        raise QABoundaryError("implementation author cannot execute independent QA")
    if not tool_evidence or any(item.task_id != state.task_id for item in tool_evidence):
        raise QABoundaryError("QA requires same-task measured tool evidence")

    measured = tuple(_domain_evidence(item) for item in tool_evidence)
    finished_at = completed_at or datetime.now(UTC)
    if any(item.occurred_at > finished_at for item in measured):
        raise QABoundaryError("QA report predates its evidence")
    evidence_ids = tuple(item.evidence_id for item in measured)
    status = {
        QADecision.PASS: CheckStatus.PASS,
        QADecision.FAIL: CheckStatus.FAIL,
        QADecision.BLOCKED: CheckStatus.BLOCKED,
    }[draft.decision]
    defects: tuple[Defect, ...] = ()
    if draft.decision is QADecision.FAIL:
        if (
            draft.severity is None
            or draft.defect_description is None
            or draft.acceptance_criterion is None
        ):
            raise QABoundaryError("QA FAIL requires a complete defect")
        defects = (
            Defect(
                defect_id=_identifier("defect", request.workflow_id, str(state.revision)),
                severity=draft.severity,
                description=draft.defect_description,
                acceptance_criterion=draft.acceptance_criterion,
                evidence_ids=evidence_ids,
            ),
        )
    report = QAReport(
        artifact_id=_identifier("qa-report", request.workflow_id, str(state.revision)),
        task_id=state.task_id,
        producer_id=request.agent_id,
        created_at=finished_at,
        implementation_author_id=state.implementation_author_id,
        decision=draft.decision,
        checks=(
            CheckResult(
                check_id=_identifier("qa-check", request.workflow_id, str(state.revision)),
                name=draft.check_name,
                status=status,
                evidence_ids=evidence_ids,
            ),
        ),
        defects=defects,
        summary=draft.summary,
        evidence=measured,
    )
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id=_identifier("cmd", request.workflow_id, str(state.revision), "qa-start"),
            task_id=state.task_id,
            actor_id=request.agent_id,
            target_stage=Stage.QA,
            occurred_at=finished_at,
        ),
        events,
    )
    target = {
        QADecision.PASS: Stage.QA_PASSED,
        QADecision.FAIL: Stage.REWORK,
        QADecision.BLOCKED: Stage.BLOCKED,
    }[draft.decision]
    reason = draft.summary if target in {Stage.REWORK, Stage.BLOCKED} else None
    tool_duration_ms = max(tool_usage.elapsed_ms, sum(item.duration_ms for item in tool_evidence))
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id=_identifier("cmd", request.workflow_id, str(state.revision), "qa-result"),
            task_id=state.task_id,
            actor_id=request.agent_id,
            target_stage=target,
            occurred_at=finished_at,
            artifact=report,
            charge=BudgetCharge(
                tool_calls=tool_usage.completed_calls,
                model_tokens=model_usage.total_tokens,
                wall_time_seconds=ceil(max(model_latency_ms, tool_duration_ms) / 1_000),
                rework_attempts=1 if target is Stage.REWORK else 0,
            ),
            reason=reason,
        ),
        events,
    )
    verify_event_chain(events, expected_state=state)
    return report, state, events
