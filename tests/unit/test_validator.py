from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path

import pytest

from contracts import (
    ArtifactReference,
    Evidence,
    EvidenceKind,
    ImplementationResult,
    ImplementationStatus,
    ScenarioSpecification,
    ToolCallEvidence,
    ToolCallStatus,
    ToolName,
    ValidationDecision,
)
from orchestrator import Stage, TransitionCommand, append_transition, verify_event_chain
from policies import ToolUsage
from runtime.context import ContextBundle, ContextDocument
from runtime.data_engineer import (
    DataEngineerDraft,
    DataEngineerRunRequest,
    accept_data_engineer_draft,
    seed_data_engineer_state,
)
from runtime.model_provider import ModelUsage
from runtime.validator import (
    ValidationBoundaryError,
    ValidationCommand,
    ValidationCommandRunner,
    ValidationGate,
    ValidationGateOutcome,
    validate_candidate,
    validation_environment,
    validation_plan,
)

REPOSITORY = Path(__file__).resolve().parents[2]
BASE_TIME = datetime(2026, 9, 11, 2, tzinfo=UTC)


def _tool_evidence(evidence_id: str, tool_name: ToolName) -> ToolCallEvidence:
    return ToolCallEvidence(
        evidence_id=evidence_id,
        request_id=f"request-{evidence_id}",
        task_id="scenario-net-revenue",
        producer_id="tool-gateway",
        tool=tool_name,
        arguments_sha256="a" * 64,
        started_at=BASE_TIME,
        completed_at=BASE_TIME,
        status=ToolCallStatus.SUCCESS,
        exit_code=0,
        duration_ms=1,
        output_bytes=2,
        output=ArtifactReference(
            path=f"evidence/{evidence_id}.txt",
            sha256="b" * 64,
            media_type="text/plain",
            size_bytes=2,
        ),
    )


def _implemented_state(*, rework_attempts: int = 1):
    task_content = "# bounded task\n"
    encoded = task_content.encode()
    specification = ScenarioSpecification.model_validate_json(
        (REPOSITORY / "scenarios/net-revenue/specification.json").read_bytes()
    )
    request = DataEngineerRunRequest(
        specification=specification,
        context=ContextBundle(
            workspace_fingerprint="c" * 64,
            documents=(
                ContextDocument(
                    path="TASK.md",
                    content=task_content,
                    size_bytes=len(encoded),
                    sha256=sha256(encoded).hexdigest(),
                ),
            ),
            total_bytes=len(encoded),
        ),
        workflow_id="workflow-validator",
        correlation_id="correlation-validator",
        started_at=BASE_TIME,
        budget_limits={
            "tool_calls": 80,
            "model_tokens": 30_000,
            "wall_time_seconds": 1_200,
            "rework_attempts": rework_attempts,
        },
    )
    state, events = seed_data_engineer_state(request)
    _, _, state, events = accept_data_engineer_draft(
        request,
        state,
        events,
        DataEngineerDraft(
            relevant_sources=("raw.orders",),
            findings=("grain inspected",),
            recommended_approach="aggregate before joining",
            status=ImplementationStatus.COMPLETED,
            summary="candidate implemented",
        ),
        tool_evidence=(
            _tool_evidence("tool-read", ToolName.WORKSPACE_READ_FILE),
            _tool_evidence("tool-write", ToolName.WORKSPACE_WRITE_FILE),
        ),
        tool_usage=ToolUsage(completed_calls=2, elapsed_ms=2, output_bytes=4),
        model_usage=ModelUsage(total_tokens=10),
        model_latency_ms=10,
        changed_files=("platform/dbt/models/marts/fct_net_revenue.sql",),
        completed_at=BASE_TIME,
    )
    return state, events


class _FakeRunner:
    def __init__(self, *, failing_gate: ValidationGate | None = None, run_number: int = 1) -> None:
        self.failing_gate = failing_gate
        self.run_number = run_number
        self.calls: list[ValidationGate] = []

    def run(self, command: ValidationCommand, *, task_id: str) -> ValidationGateOutcome:
        self.calls.append(command.gate)
        failed = command.gate is self.failing_gate
        evidence_id = f"validation-{self.run_number}-{command.gate.value}"
        return ValidationGateOutcome(
            evidence=Evidence(
                evidence_id=evidence_id,
                task_id=task_id,
                producer_id="validator",
                kind=EvidenceKind.TEST,
                source=command.gate.value,
                invocation="fixed fake command",
                exit_code=1 if failed else 0,
                artifact=ArtifactReference(
                    path=f"evidence/{evidence_id}.txt",
                    sha256="d" * 64,
                    media_type="text/plain",
                    size_bytes=2,
                ),
                occurred_at=BASE_TIME + timedelta(seconds=self.run_number),
            ),
            duration_ms=100,
        )


def test_validation_plan_is_closed_and_contains_independent_sql() -> None:
    plan = validation_plan("net-revenue")

    assert [command.gate for command in plan] == list(ValidationGate)
    assert all("shell" not in command.argv for command in plan)
    assert "scenario-contract-test" in plan[2].argv


def test_validation_environment_drops_secrets_and_python_make_injection() -> None:
    environment = validation_environment(
        {
            "PATH": "/usr/bin",
            "HOME": "/tmp/home",
            "DOCKER_HOST": "unix:///socket",
            "API_TOKEN": "secret",
            "LLM_DEFAULT_MODEL": "expensive",
            "PYTHONPATH": "/tmp/inject",
            "PYTHONHOME": "/tmp/inject",
            "MAKEFLAGS": "--eval=bad",
        }
    )

    assert environment == {
        "PATH": "/usr/bin",
        "HOME": "/tmp/home",
        "DOCKER_HOST": "unix:///socket",
    }


def test_command_runner_rejects_forged_argv_before_execution(tmp_path: Path) -> None:
    runner = ValidationCommandRunner(tmp_path, "net-revenue")
    forged = ValidationCommand(ValidationGate.POLICY, ("sh", "-c", "true"), 1)

    with pytest.raises(ValidationBoundaryError, match="allowlist"):
        runner.run(forged, task_id="scenario-net-revenue")


def test_all_independent_gates_open_validated_transition() -> None:
    state, events = _implemented_state()
    runner = _FakeRunner()

    result = validate_candidate(
        REPOSITORY,
        "net-revenue",
        state,
        events,
        runner=runner,  # type: ignore[arg-type]
        clock=lambda: BASE_TIME + timedelta(seconds=2),
    )

    assert result.artifact.decision is ValidationDecision.PASS
    assert result.state.stage is Stage.VALIDATED
    assert runner.calls == list(ValidationGate)
    verify_event_chain(result.events, expected_state=result.state)


def test_failure_stops_early_then_exhausted_rework_becomes_terminal() -> None:
    state, events = _implemented_state(rework_attempts=1)
    first_runner = _FakeRunner(failing_gate=ValidationGate.INDEPENDENT_SQL)
    first = validate_candidate(
        REPOSITORY,
        "net-revenue",
        state,
        events,
        runner=first_runner,  # type: ignore[arg-type]
        clock=lambda: BASE_TIME + timedelta(seconds=2),
    )

    assert first.artifact.decision is ValidationDecision.FAIL
    assert first.state.stage is Stage.REWORK
    assert first_runner.calls == [
        ValidationGate.WORKSPACE_INTEGRITY,
        ValidationGate.PUBLIC_BUILD,
        ValidationGate.INDEPENDENT_SQL,
    ]

    state, events = append_transition(
        first.state,
        TransitionCommand(
            command_id="rework-implementing",
            task_id=first.state.task_id,
            actor_id="data-engineer-agent",
            target_stage=Stage.IMPLEMENTING,
            occurred_at=BASE_TIME + timedelta(seconds=3),
        ),
        first.events,
    )
    repaired = ImplementationResult(
        artifact_id="implementation-rework-1",
        task_id=state.task_id,
        producer_id="data-engineer-agent",
        created_at=BASE_TIME + timedelta(seconds=3),
        status=ImplementationStatus.COMPLETED,
        changed_files=("platform/dbt/models/marts/fct_net_revenue.sql",),
        summary="reworked candidate",
        evidence=(first.artifact.evidence[0],),
    )
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id="rework-implemented",
            task_id=state.task_id,
            actor_id="data-engineer-agent",
            target_stage=Stage.IMPLEMENTED,
            occurred_at=BASE_TIME + timedelta(seconds=3),
            artifact=repaired,
        ),
        events,
    )
    second = validate_candidate(
        REPOSITORY,
        "net-revenue",
        state,
        events,
        runner=_FakeRunner(failing_gate=ValidationGate.PUBLIC_BUILD, run_number=2),  # type: ignore[arg-type]
        clock=lambda: BASE_TIME + timedelta(seconds=4),
    )

    assert second.state.stage is Stage.FAILED
    assert second.state.budgets.used.rework_attempts == 1
    assert "rework budget exhausted" in second.state.terminal_reason


def test_validator_infrastructure_error_fails_without_rework() -> None:
    state, events = _implemented_state(rework_attempts=2)
    runner = _FakeRunner(failing_gate=ValidationGate.WORKSPACE_INTEGRITY)
    original_run = runner.run

    def infrastructure_failure(command: ValidationCommand, *, task_id: str):
        outcome = original_run(command, task_id=task_id)
        return ValidationGateOutcome(
            evidence=outcome.evidence,
            duration_ms=outcome.duration_ms,
            infrastructure_error=True,
        )

    runner.run = infrastructure_failure  # type: ignore[method-assign]
    result = validate_candidate(
        REPOSITORY,
        "net-revenue",
        state,
        events,
        runner=runner,
        clock=lambda: BASE_TIME + timedelta(seconds=2),
    )

    assert result.artifact.decision is ValidationDecision.ERROR
    assert result.state.stage is Stage.FAILED
    assert result.state.budgets.used.rework_attempts == 0
