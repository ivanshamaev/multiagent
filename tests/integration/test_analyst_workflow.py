import asyncio
from datetime import UTC, datetime
from pathlib import Path

import pytest

from contracts import AnalysisFactKind
from orchestrator import Stage, verify_event_chain
from policies import load_capability_profile
from runtime.analyst import (
    AnalystPhaseDraft,
    AnalystSynthesisDraft,
    ObservedFactDraft,
    prepare_analyst_request,
)
from runtime.analyst_workflow import AutonomousAnalystError, build_analyst_workflow
from runtime.model_provider import ModelInvocation, ModelUsage
from runtime.scenario_harness import load_manifest, reset_workspace
from runtime.tools import (
    ConnectedDataEngineerMCPTools,
    DataEngineerMCPTools,
    MCPToolGateway,
    ToolEvidenceStore,
)

ROOT = Path(__file__).resolve().parents[2]


class _MCP:
    async def call_tool(self, tool_name: str, **kwargs):
        if tool_name == "list":
            return "source.agentic_data_platform.raw.orders\nmodel.agentic_data_platform.fct_orders"
        if tool_name == "get_lineage_dev":
            return (
                "source.agentic_data_platform.raw.orders -> model.agentic_data_platform.fct_orders"
            )
        if tool_name == "run_query":
            return "order_count\tcurrency_count\tmissing_currency_count\n10\t2\t0"
        raise AssertionError(f"unexpected tool {tool_name}")


class _OfflineAnalyst:
    def __init__(self) -> None:
        self.phase = 0
        self.prompts: list[str] = []

    def _invocation(self, value):
        marker = str(self.phase)
        return ModelInvocation(
            value=value,
            model_id="fake/offline-analyst",
            usage=ModelUsage(input_tokens=10, output_tokens=5, total_tokens=15),
            latency_ms=10,
            finish_reason="stop",
            request_sha256=marker * 64,
            response_sha256=chr(96 + self.phase) * 64,
        )

    async def generate_with_tools(
        self,
        response_model,
        *,
        system_prompt: str,
        user_prompt: str,
        tools,
    ):
        self.phase += 1
        self.prompts.append(user_prompt)
        exposed = {item.name: item for item in tools}
        if self.phase == 1:
            await exposed["analyst_list_resources"].invoke(arguments={})
            facts = (
                ObservedFactDraft(
                    kind=AnalysisFactKind.SOURCE,
                    statement="source.agentic_data_platform.raw.orders",
                ),
                ObservedFactDraft(
                    kind=AnalysisFactKind.MODEL,
                    statement="model.agentic_data_platform.fct_orders",
                ),
            )
        elif self.phase == 2:
            await exposed["analyst_get_lineage"].invoke(arguments={})
            facts = (
                ObservedFactDraft(
                    kind=AnalysisFactKind.LINEAGE,
                    statement=(
                        "source.agentic_data_platform.raw.orders -> "
                        "model.agentic_data_platform.fct_orders"
                    ),
                ),
            )
        else:
            assert self.phase == 3
            await exposed["analyst_profile_orders"].invoke(arguments={})
            facts = (
                ObservedFactDraft(
                    kind=AnalysisFactKind.PROFILE,
                    statement="10\t2\t0",
                ),
            )
        return self._invocation(AnalystPhaseDraft(facts=facts))

    async def generate(self, response_model, *, system_prompt: str, user_prompt: str):
        self.phase += 1
        assert self.phase == 4
        self.prompts.append(user_prompt)
        return self._invocation(
            AnalystSynthesisDraft(
                assumptions=("Revenue should remain split by currency.",),
                open_questions=("Should late refunds restate order dates?",),
                risks=("No FX source was discovered.",),
                recommended_next_steps=("PM must resolve refund-date semantics.",),
            )
        )


class _ToolFreeAnalyst(_OfflineAnalyst):
    async def generate_with_tools(
        self,
        response_model,
        *,
        system_prompt: str,
        user_prompt: str,
        tools,
    ):
        self.phase += 1
        return self._invocation(
            AnalystPhaseDraft(
                facts=(
                    ObservedFactDraft(
                        kind=AnalysisFactKind.SOURCE,
                        statement="unsupported without a tool",
                    ),
                )
            )
        )


def test_offline_analyst_produces_evidence_backed_pm_handoff() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset_workspace(ROOT, manifest)
    profile = load_capability_profile(ROOT / "policies/profiles/analyst_v1.json")
    mcp = _MCP()
    gateway = MCPToolGateway(
        profile,
        mcp,
        mcp,
        ToolEvidenceStore(ROOT, ROOT / ".scenario-state"),
    )
    tools = DataEngineerMCPTools(
        gateway,
        task_id="scenario-net-revenue",
        actor_id="analyst-agent",
        role="analyst",
    )
    connected = ConnectedDataEngineerMCPTools(tools.tools, gateway)
    provider = _OfflineAnalyst()
    request = prepare_analyst_request(
        ROOT,
        "net-revenue",
        workflow_id="workflow-offline-analyst",
        correlation_id="correlation-offline-analyst",
        configuration_fingerprint="a" * 64,
        created_at=datetime(2026, 9, 13, 8, tzinfo=UTC),
    )

    output = asyncio.run(build_analyst_workflow(provider, connected).run(request)).get_outputs()[0]

    assert output.state.stage is Stage.ANALYSIS_READY
    assert len(output.report.facts) == 4
    assert len(output.tool_evidence) == 3
    assert len(output.model_calls) == 4
    assert output.handoff.unresolved_questions == output.report.open_questions
    assert len(provider.prompts) == 4
    verify_event_chain(output.events, expected_state=output.state)


def test_tool_free_phase_fails_closed_without_analysis_artifact() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    reset_workspace(ROOT, manifest)
    profile = load_capability_profile(ROOT / "policies/profiles/analyst_v1.json")
    mcp = _MCP()
    gateway = MCPToolGateway(
        profile,
        mcp,
        mcp,
        ToolEvidenceStore(ROOT, ROOT / ".scenario-state"),
    )
    facade = DataEngineerMCPTools(
        gateway,
        task_id="scenario-net-revenue",
        actor_id="analyst-agent",
        role="analyst",
    )
    request = prepare_analyst_request(
        ROOT,
        "net-revenue",
        workflow_id="workflow-tool-free-analyst",
        correlation_id="correlation-tool-free-analyst",
        configuration_fingerprint="f" * 64,
    )

    with pytest.raises(
        AutonomousAnalystError,
        match="analyst_phase_1_requires_exactly_one_tool",
    ) as raised:
        asyncio.run(
            build_analyst_workflow(
                _ToolFreeAnalyst(),
                ConnectedDataEngineerMCPTools(facade.tools, gateway),
            ).run(request)
        )

    assert raised.value.tool_evidence == ()
    assert len(raised.value.model_calls) == 1
