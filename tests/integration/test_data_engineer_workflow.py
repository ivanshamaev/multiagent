import asyncio
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from contracts import ArtifactReference, Evidence, EvidenceKind, ValidationDecision
from orchestrator import Stage, verify_event_chain
from policies import load_capability_profile
from runtime.data_engineer import prepare_data_engineer_request
from runtime.data_engineer_workflow import (
    AutonomousExecutionError,
    _bounded_validator_excerpt,
    _repair_target,
    build_data_engineer_workflow,
    build_phased_data_engineer_workflow,
)
from runtime.model_provider import ModelInvocation, ModelUsage
from runtime.scenario_harness import load_manifest, reset_workspace
from runtime.tools import (
    ConnectedDataEngineerMCPTools,
    DataEngineerMCPTools,
    MCPToolGateway,
    ToolEvidenceStore,
    WorkspaceToolAdapter,
)
from runtime.validator import ValidationGate, ValidationGateOutcome, validation_plan

REPOSITORY = Path(__file__).resolve().parents[2]
PROFILE = REPOSITORY / "policies/profiles/data_engineer_v1.json"


def test_validator_feedback_preserves_failure_tail_and_selects_repair_target() -> None:
    feedback = _bounded_validator_excerpt(
        b"command start\n"
        + b"routine output\n" * 2_000
        + b"Database Error in test assert_fct_net_revenue_contract\nsyntax error\n"
    )

    assert feedback.startswith("command start")
    assert "VALIDATOR OUTPUT MIDDLE OMITTED" in feedback
    assert feedback.endswith("syntax error\n")
    assert _repair_target(feedback) == ("platform/dbt/tests/assert_fct_net_revenue_contract.sql")
    assert _repair_target("Failure in model fct_net_revenue") == (
        "platform/dbt/models/marts/fct_net_revenue.sql"
    )
    assert (
        _repair_target("Failure in test assert_fct_net_revenue_contract\nGot 2 results")
        == "platform/dbt/models/marts/fct_net_revenue.sql"
    )


class _UnusedMCP:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def call_tool(self, tool_name: str, **kwargs: object) -> str:
        self.calls.append(tool_name)
        return "unused"


class _OfflineDataEngineer:
    async def generate(self, response_model, *, system_prompt: str, user_prompt: str):
        raise AssertionError("tool-free generation must not be used")

    async def generate_with_tools(
        self,
        response_model,
        *,
        system_prompt: str,
        user_prompt: str,
        tools,
    ):
        exposed = {item.name: item for item in tools}
        assert "immutable specification" in system_prompt
        assert "<untrusted_workspace_context" in user_prompt
        await exposed["workspace_read_file"].invoke(arguments={"path": "TASK.md"})
        await exposed["workspace_write_file"].invoke(
            arguments={
                "path": "platform/dbt/models/marts/fct_net_revenue.sql",
                "content": "{{ config(materialized='table') }}\nselect 1 as net_revenue_cents\n",
            }
        )
        draft = response_model(
            relevant_sources=("raw.orders", "raw.payments", "raw.refunds"),
            findings=("event streams must be aggregated independently",),
            recommended_approach="aggregate events before joining to orders",
            status="completed",
            summary="offline candidate written",
        )
        return ModelInvocation(
            value=draft,
            model_id="fake/offline-data-engineer",
            usage=ModelUsage(input_tokens=20, output_tokens=10, total_tokens=30),
            latency_ms=10,
            finish_reason="stop",
            request_sha256="a" * 64,
            response_sha256="b" * 64,
        )


class _ToolFreeDataEngineer(_OfflineDataEngineer):
    async def generate_with_tools(
        self,
        response_model,
        *,
        system_prompt: str,
        user_prompt: str,
        tools,
    ):
        draft = response_model(
            relevant_sources=("raw.orders",),
            findings=("claimed inspection without evidence",),
            recommended_approach="write a model",
            status="completed",
            summary="unsupported completion",
        )
        return ModelInvocation(
            value=draft,
            model_id="fake/tool-free",
            usage=ModelUsage(input_tokens=12, output_tokens=8, total_tokens=20),
            latency_ms=5,
            finish_reason="stop",
            request_sha256="d" * 64,
            response_sha256="e" * 64,
        )


class _OfflinePhasedDataEngineer(_OfflineDataEngineer):
    def __init__(self) -> None:
        self.phase = 0

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
        if self.phase == 1:
            assert set(exposed) == {"workspace_read_file"}
            await exposed["workspace_read_file"].invoke(arguments={"path": "TASK.md"})
            summary = "offline investigation complete"
        elif self.phase == 2:
            assert set(exposed) == {"workspace_write_file"}
            await exposed["workspace_write_file"].invoke(
                arguments={
                    "path": "platform/dbt/models/marts/fct_net_revenue.sql",
                    "content": (
                        "{{ config(materialized='table') }}\nselect 1 as net_revenue_cents\n"
                    ),
                }
            )
            summary = "offline SQL written"
        else:
            assert set(exposed) == {"workspace_write_file"}
            if self.phase == 3:
                await exposed["workspace_write_file"].invoke(
                    arguments={
                        "path": "platform/dbt/tests/assert_fct_net_revenue_contract.sql",
                        "content": "select * from {{ ref('fct_net_revenue') }} where 1 = 0\n",
                    }
                )
                summary = "offline test written"
            else:
                assert self.phase in {4, 5}
                assert "untrusted_public_validation" in user_prompt
                await exposed["workspace_write_file"].invoke(
                    arguments={
                        "path": "platform/dbt/models/marts/fct_net_revenue.sql",
                        "content": (
                            "{{ config(materialized='table') }}\n"
                            f"select {self.phase} as net_revenue_cents\n"
                        ),
                    }
                )
                summary = "offline SQL repaired"
        if "relevant_sources" in response_model.model_fields:
            draft = response_model(
                relevant_sources=("raw.orders", "raw.payments", "raw.refunds"),
                findings=("event streams must be aggregated independently",),
                recommended_approach="aggregate before joining",
            )
        else:
            draft = response_model(status="completed", summary=summary)
        marker = str(self.phase)
        return ModelInvocation(
            value=draft,
            model_id="fake/offline-phased",
            usage=ModelUsage(input_tokens=10, output_tokens=5, total_tokens=15),
            latency_ms=10,
            finish_reason="stop",
            request_sha256=marker * 64,
            response_sha256=chr(96 + self.phase) * 64,
        )


class _PassingValidator:
    def __init__(self) -> None:
        self.calls = []

    def run(self, command, *, task_id: str) -> ValidationGateOutcome:
        self.calls.append(command.gate)
        now = datetime.now(UTC)
        return ValidationGateOutcome(
            evidence=Evidence(
                evidence_id=f"offline-{command.gate.value}",
                task_id=task_id,
                producer_id="validator",
                kind=EvidenceKind.TEST,
                source=command.gate.value,
                invocation="offline deterministic gate",
                exit_code=0,
                artifact=ArtifactReference(
                    path=f"evidence/offline-{command.gate.value}.txt",
                    sha256="c" * 64,
                    media_type="text/plain",
                    size_bytes=2,
                ),
                occurred_at=now,
            ),
            duration_ms=1,
        )


class _FailingValidator:
    def __init__(self, failures: int) -> None:
        self.failures_remaining = failures
        self.calls = 0

    def run(self, command, *, task_id: str) -> ValidationGateOutcome:
        self.calls += 1
        should_fail = command.gate is ValidationGate.PUBLIC_BUILD and self.failures_remaining > 0
        if should_fail:
            self.failures_remaining -= 1
        contents = b"public dbt compile failure\n" if should_fail else b"ok\n"
        digest = sha256(contents).hexdigest()
        target = REPOSITORY / f".scenario-state/evidence/validator/{digest}.txt"
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        target.write_bytes(contents)
        target.chmod(0o600)
        return ValidationGateOutcome(
            evidence=Evidence(
                evidence_id=f"rework-{command.gate.value}-{self.calls}",
                task_id=task_id,
                producer_id="validator",
                kind=EvidenceKind.TEST,
                source=command.gate.value,
                invocation="offline deterministic gate",
                exit_code=1 if should_fail else 0,
                artifact=ArtifactReference(
                    path=target.relative_to(REPOSITORY).as_posix(),
                    sha256=digest,
                    media_type="text/plain",
                    size_bytes=len(contents),
                ),
                occurred_at=datetime.now(UTC),
            ),
            duration_ms=1,
        )


def test_offline_workflow_connects_tools_artifacts_reducer_and_validator() -> None:
    manifest = load_manifest(REPOSITORY, "net-revenue")
    reset = reset_workspace(REPOSITORY, manifest)
    profile = load_capability_profile(PROFILE)
    clickhouse = _UnusedMCP()
    dbt = _UnusedMCP()
    workspace = WorkspaceToolAdapter(REPOSITORY, manifest, profile)
    gateway = MCPToolGateway(
        profile,
        clickhouse,
        dbt,
        ToolEvidenceStore(REPOSITORY, REPOSITORY / ".scenario-state"),
        workspace,
    )
    facade = DataEngineerMCPTools(
        gateway,
        task_id="scenario-net-revenue",
        actor_id="data-engineer-agent",
    )
    connected = ConnectedDataEngineerMCPTools(facade.tools, gateway)
    validator = _PassingValidator()

    try:
        request = prepare_data_engineer_request(
            REPOSITORY,
            "net-revenue",
            workflow_id="workflow-offline-de",
            correlation_id="correlation-offline-de",
        )
        workflow = build_data_engineer_workflow(
            _OfflineDataEngineer(),  # type: ignore[arg-type]
            connected,
            repository_root=REPOSITORY,
            scenario_id="net-revenue",
            validator_runner=validator,
        )
        run = asyncio.run(workflow.run(request))
        outputs = run.get_outputs()
        assert len(outputs) == 1
        result = outputs[0]

        assert result.state.stage is Stage.VALIDATED
        assert result.validation.decision is ValidationDecision.PASS
        assert result.implementation.changed_files == (
            "platform/dbt/models/marts/fct_net_revenue.sql",
        )
        assert result.state.budgets.used.tool_calls == 2
        assert len(result.tool_evidence) == 2
        assert validator.calls == [item.gate for item in validation_plan("net-revenue")]
        assert clickhouse.calls == []
        assert dbt.calls == []
        verify_event_chain(result.events, expected_state=result.state)
    finally:
        reset_workspace(REPOSITORY, manifest)
        assert Path(str(reset["workspace"])).is_dir()


def test_tool_free_model_completion_is_a_typed_run_failure() -> None:
    manifest = load_manifest(REPOSITORY, "net-revenue")
    reset_workspace(REPOSITORY, manifest)
    profile = load_capability_profile(PROFILE)
    gateway = MCPToolGateway(
        profile,
        _UnusedMCP(),
        _UnusedMCP(),
        ToolEvidenceStore(REPOSITORY, REPOSITORY / ".scenario-state"),
        WorkspaceToolAdapter(REPOSITORY, manifest, profile),
    )
    connected = ConnectedDataEngineerMCPTools(
        DataEngineerMCPTools(
            gateway,
            task_id="scenario-net-revenue",
            actor_id="data-engineer-agent",
        ).tools,
        gateway,
    )
    try:
        request = prepare_data_engineer_request(
            REPOSITORY,
            "net-revenue",
            workflow_id="workflow-tool-free-de",
            correlation_id="correlation-tool-free-de",
        )
        workflow = build_data_engineer_workflow(
            _ToolFreeDataEngineer(),  # type: ignore[arg-type]
            connected,
            repository_root=REPOSITORY,
            scenario_id="net-revenue",
            validator_runner=_PassingValidator(),
        )
        try:
            asyncio.run(workflow.run(request))
        except AutonomousExecutionError as error:
            assert error.code == "model_completed_without_tool_evidence"
            assert error.model_call.usage.total_tokens == 20
            assert error.tool_evidence == ()
        else:
            raise AssertionError("tool-free completion was accepted")
    finally:
        reset_workspace(REPOSITORY, manifest)


def test_phased_workflow_uses_fresh_scoped_tool_rounds_and_cumulative_evidence() -> None:
    manifest = load_manifest(REPOSITORY, "net-revenue")
    reset_workspace(REPOSITORY, manifest)
    profile = load_capability_profile(PROFILE)
    gateway = MCPToolGateway(
        profile,
        _UnusedMCP(),
        _UnusedMCP(),
        ToolEvidenceStore(REPOSITORY, REPOSITORY / ".scenario-state"),
        WorkspaceToolAdapter(REPOSITORY, manifest, profile),
    )
    connected = ConnectedDataEngineerMCPTools(
        DataEngineerMCPTools(
            gateway,
            task_id="scenario-net-revenue",
            actor_id="data-engineer-agent",
        ).tools,
        gateway,
    )
    provider = _OfflinePhasedDataEngineer()
    try:
        request = prepare_data_engineer_request(
            REPOSITORY,
            "net-revenue",
            workflow_id="workflow-phased-de",
            correlation_id="correlation-phased-de",
        )
        workflow = build_phased_data_engineer_workflow(
            provider,  # type: ignore[arg-type]
            connected,
            repository_root=REPOSITORY,
            scenario_id="net-revenue",
            validator_runner=_PassingValidator(),
        )
        outputs = asyncio.run(workflow.run(request)).get_outputs()
        result = outputs[0]

        assert provider.phase == 3
        assert result.state.stage is Stage.VALIDATED
        assert result.state.budgets.used.tool_calls == 3
        assert len(result.tool_evidence) == 3
        assert len(result.all_model_calls) == 3
        assert sum(item.usage.total_tokens for item in result.all_model_calls) == 45
        assert result.implementation.changed_files == (
            "platform/dbt/models/marts/fct_net_revenue.sql",
            "platform/dbt/tests/assert_fct_net_revenue_contract.sql",
        )
    finally:
        reset_workspace(REPOSITORY, manifest)


def test_failed_validation_triggers_one_measured_rework_then_revalidation() -> None:
    manifest = load_manifest(REPOSITORY, "net-revenue")
    reset_workspace(REPOSITORY, manifest)
    profile = load_capability_profile(PROFILE)
    gateway = MCPToolGateway(
        profile,
        _UnusedMCP(),
        _UnusedMCP(),
        ToolEvidenceStore(REPOSITORY, REPOSITORY / ".scenario-state"),
        WorkspaceToolAdapter(REPOSITORY, manifest, profile),
    )
    connected = ConnectedDataEngineerMCPTools(
        DataEngineerMCPTools(
            gateway,
            task_id="scenario-net-revenue",
            actor_id="data-engineer-agent",
        ).tools,
        gateway,
    )
    provider = _OfflinePhasedDataEngineer()
    try:
        request = prepare_data_engineer_request(
            REPOSITORY,
            "net-revenue",
            workflow_id="workflow-phased-rework",
            correlation_id="correlation-phased-rework",
        )
        workflow = build_phased_data_engineer_workflow(
            provider,  # type: ignore[arg-type]
            connected,
            repository_root=REPOSITORY,
            scenario_id="net-revenue",
            validator_runner=_FailingValidator(1),
        )
        result = asyncio.run(workflow.run(request)).get_outputs()[0]

        assert provider.phase == 4
        assert result.state.stage is Stage.VALIDATED
        assert result.state.budgets.used.rework_attempts == 1
        assert result.state.budgets.used.tool_calls == 4
        assert result.state.budgets.used.model_tokens == 60
        assert len(result.tool_evidence) == 4
        assert len(result.all_model_calls) == 4
        assert result.validation.decision is ValidationDecision.PASS
        assert sum(event.requested_stage is Stage.REWORK for event in result.events) == 1
    finally:
        reset_workspace(REPOSITORY, manifest)


def test_rework_exhaustion_finishes_failed_without_unbounded_model_loop() -> None:
    manifest = load_manifest(REPOSITORY, "net-revenue")
    reset_workspace(REPOSITORY, manifest)
    profile = load_capability_profile(PROFILE)
    gateway = MCPToolGateway(
        profile,
        _UnusedMCP(),
        _UnusedMCP(),
        ToolEvidenceStore(REPOSITORY, REPOSITORY / ".scenario-state"),
        WorkspaceToolAdapter(REPOSITORY, manifest, profile),
    )
    connected = ConnectedDataEngineerMCPTools(
        DataEngineerMCPTools(
            gateway,
            task_id="scenario-net-revenue",
            actor_id="data-engineer-agent",
        ).tools,
        gateway,
    )
    provider = _OfflinePhasedDataEngineer()
    try:
        request = prepare_data_engineer_request(
            REPOSITORY,
            "net-revenue",
            workflow_id="workflow-rework-exhaustion",
            correlation_id="correlation-rework-exhaustion",
        )
        workflow = build_phased_data_engineer_workflow(
            provider,  # type: ignore[arg-type]
            connected,
            repository_root=REPOSITORY,
            scenario_id="net-revenue",
            validator_runner=_FailingValidator(3),
        )
        result = asyncio.run(workflow.run(request)).get_outputs()[0]

        assert provider.phase == 5
        assert result.state.stage is Stage.FAILED
        assert result.state.budgets.used.rework_attempts == 2
        assert result.state.budgets.used.tool_calls == 5
        assert result.state.budgets.used.model_tokens == 75
        assert result.validation.decision is ValidationDecision.FAIL
        assert "rework budget exhausted" in result.state.terminal_reason
    finally:
        reset_workspace(REPOSITORY, manifest)
