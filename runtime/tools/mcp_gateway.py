"""Deny-by-default execution gateway for allowlisted official MCP tools."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Protocol

from contracts import (
    ToolCallEvidence,
    ToolCallStatus,
    ToolName,
    ToolRequest,
    ToolResult,
    WorkspaceReadCall,
    WorkspaceWriteCall,
)
from policies import (
    CapabilityProfile,
    PolicyCode,
    ToolPolicyDecision,
    ToolUsage,
    authorize_tool_call,
)
from runtime.tools.evidence_store import ToolEvidenceStore
from runtime.tools.workspace import (
    WorkspaceAuthorizationError,
    WorkspaceBoundaryError,
    WorkspaceToolAdapter,
)

_CLICKHOUSE_TOOLS = {
    ToolName.CLICKHOUSE_LIST_DATABASES,
    ToolName.CLICKHOUSE_LIST_TABLES,
    ToolName.CLICKHOUSE_RUN_QUERY,
}
_DBT_TOOLS = {
    ToolName.DBT_PARSE,
    ToolName.DBT_COMPILE,
    ToolName.DBT_BUILD,
    ToolName.DBT_TEST,
    ToolName.DBT_SHOW,
    ToolName.DBT_LIST,
    ToolName.DBT_GET_LINEAGE_DEV,
    ToolName.DBT_GET_NODE_DETAILS_DEV,
}
_DBT_FAILURE_PREFIXES = ("Timeout:", "Command failed", "--- stdout ---", "--- stderr ---")


class MCPCaller(Protocol):
    async def call_tool(self, tool_name: str, **kwargs: Any) -> str | Sequence[Any]: ...


class MCPGatewayError(RuntimeError):
    """An MCP request failed closed with typed retained evidence."""

    def __init__(self, message: str, evidence: ToolCallEvidence) -> None:
        super().__init__(message)
        self.evidence = evidence


class MCPAuthorizationError(MCPGatewayError):
    """The deterministic policy denied a request before MCP execution."""

    def __init__(self, decision: ToolPolicyDecision, evidence: ToolCallEvidence) -> None:
        super().__init__(f"{decision.code.value}: {decision.reason}", evidence)
        self.decision = decision


class MCPToolGateway:
    """Serialize, re-authorize, bound, and retain all MCP calls for one task."""

    def __init__(
        self,
        profile: CapabilityProfile,
        clickhouse: MCPCaller,
        dbt: MCPCaller,
        evidence_store: ToolEvidenceStore,
        workspace: WorkspaceToolAdapter | None = None,
    ) -> None:
        self._profile = profile
        self._clickhouse = clickhouse
        self._dbt = dbt
        self._evidence_store = evidence_store
        self._workspace = workspace
        self._usage = ToolUsage()
        self._evidence: list[ToolCallEvidence] = []
        self._execution_lock = asyncio.Lock()

    @property
    def usage(self) -> ToolUsage:
        """Return the immutable accumulated usage snapshot."""

        return self._usage

    @property
    def evidence(self) -> tuple[ToolCallEvidence, ...]:
        """Return every outcome, including pre-execution denials, in call order."""

        return tuple(self._evidence)

    @property
    def allowed_tools(self) -> frozenset[ToolName]:
        """Expose the immutable profile allowlist for facade construction."""

        allowed = set(self._profile.allowed_tools)
        if self._workspace is None:
            allowed -= {ToolName.WORKSPACE_READ_FILE, ToolName.WORKSPACE_WRITE_FILE}
        return frozenset(allowed)

    async def execute(self, request: ToolRequest) -> ToolResult:
        """Execute one validated MCP request after a fresh policy decision."""

        async with self._execution_lock:
            started_at = datetime.now(UTC)
            started_timer = time.monotonic()
            decision = authorize_tool_call(self._profile, request, self._usage)
            if not decision.allowed:
                evidence = self._evidence_store.outcome(
                    request,
                    status=ToolCallStatus.DENIED,
                    producer_id="mcp-gateway",
                    started_at=started_at,
                    completed_at=datetime.now(UTC),
                    duration_ms=0,
                    error_type=decision.code.value,
                )
                self._evidence.append(evidence)
                raise MCPAuthorizationError(decision, evidence)

            if isinstance(request.call, (WorkspaceReadCall, WorkspaceWriteCall)):
                return self._execute_workspace(request, started_at, started_timer)

            try:
                caller, remote_name = self._route(request.call.tool)
            except ValueError:
                adapter_decision = ToolPolicyDecision(
                    allowed=False,
                    code=PolicyCode.TOOL_DENIED,
                    reason="workspace tools must use the workspace adapter",
                )
                evidence = self._evidence_store.outcome(
                    request,
                    status=ToolCallStatus.DENIED,
                    producer_id="mcp-gateway",
                    started_at=started_at,
                    completed_at=datetime.now(UTC),
                    duration_ms=0,
                    error_type="wrong_adapter",
                )
                self._evidence.append(evidence)
                raise MCPAuthorizationError(adapter_decision, evidence) from None
            arguments = request.call.model_dump(
                mode="json",
                exclude={"tool"},
                exclude_none=True,
            )
            if arguments.get("resource_type") == []:
                arguments.pop("resource_type")
            remaining_seconds = self._profile.max_wall_time_seconds - self._usage.elapsed_ms / 1_000
            invoked = False
            try:
                invoked = True
                async with asyncio.timeout(remaining_seconds):
                    raw_result = await caller.call_tool(remote_name, **arguments)
                content = self._text_result(raw_result)
                output = content.encode("utf-8")
                duration_ms = self._duration_ms(started_timer)
                if self._usage.output_bytes + len(output) > self._profile.max_output_bytes:
                    self._record_usage(duration_ms, self._profile.max_output_bytes)
                    evidence = self._error_evidence(
                        request,
                        started_at,
                        duration_ms,
                        "output_budget_exceeded",
                    )
                    self._evidence.append(evidence)
                    raise MCPGatewayError("MCP output exceeded the remaining byte budget", evidence)
                if request.call.tool in _DBT_TOOLS and content.startswith(_DBT_FAILURE_PREFIXES):
                    self._record_usage(duration_ms, len(output))
                    evidence = self._evidence_store.error_with_output(
                        request,
                        output,
                        "text/plain; charset=utf-8",
                        producer_id="mcp-gateway",
                        started_at=started_at,
                        completed_at=datetime.now(UTC),
                        duration_ms=duration_ms,
                        error_type="dbt_command_failed",
                    )
                    self._evidence.append(evidence)
                    raise MCPGatewayError("dbt MCP command reported failure", evidence)
                result = self._evidence_store.success_result(
                    request,
                    output,
                    "text/plain; charset=utf-8",
                    producer_id="mcp-gateway",
                    started_at=started_at,
                    completed_at=datetime.now(UTC),
                    duration_ms=duration_ms,
                )
                self._record_usage(duration_ms, len(output))
                self._evidence.append(result.evidence)
                return result
            except TimeoutError:
                duration_ms = self._duration_ms(started_timer)
                if invoked:
                    self._record_usage(duration_ms, 0)
                evidence = self._evidence_store.outcome(
                    request,
                    status=ToolCallStatus.TIMEOUT,
                    producer_id="mcp-gateway",
                    started_at=started_at,
                    completed_at=datetime.now(UTC),
                    duration_ms=duration_ms,
                    error_type="mcp_timeout",
                )
                self._evidence.append(evidence)
                raise MCPGatewayError(
                    "MCP call exceeded the remaining wall-time budget",
                    evidence,
                ) from None
            except MCPGatewayError:
                raise
            except Exception as error:
                duration_ms = self._duration_ms(started_timer)
                if invoked:
                    self._record_usage(duration_ms, 0)
                evidence = self._error_evidence(
                    request,
                    started_at,
                    duration_ms,
                    type(error).__name__,
                )
                self._evidence.append(evidence)
                raise MCPGatewayError("MCP call failed", evidence) from error

    def _route(self, tool: ToolName) -> tuple[MCPCaller, str]:
        if tool in _CLICKHOUSE_TOOLS:
            return self._clickhouse, tool.value.removeprefix("clickhouse.")
        if tool in _DBT_TOOLS:
            return self._dbt, tool.value.removeprefix("dbt.")
        raise ValueError("MCP gateway received a non-MCP tool")

    def _execute_workspace(
        self,
        request: ToolRequest,
        started_at: datetime,
        started_timer: float,
    ) -> ToolResult:
        if self._workspace is None:
            decision = ToolPolicyDecision(
                allowed=False,
                code=PolicyCode.TOOL_DENIED,
                reason="workspace adapter is not configured",
            )
            evidence = self._evidence_store.outcome(
                request,
                status=ToolCallStatus.DENIED,
                producer_id="tool-gateway",
                started_at=started_at,
                completed_at=datetime.now(UTC),
                duration_ms=0,
                error_type="wrong_adapter",
            )
            self._evidence.append(evidence)
            raise MCPAuthorizationError(decision, evidence)
        try:
            result = self._workspace.execute(request, self._usage)
        except WorkspaceAuthorizationError as error:
            evidence = self._evidence_store.outcome(
                request,
                status=ToolCallStatus.DENIED,
                producer_id="tool-gateway",
                started_at=started_at,
                completed_at=datetime.now(UTC),
                duration_ms=self._duration_ms(started_timer),
                error_type=error.decision.code.value,
            )
            self._evidence.append(evidence)
            raise MCPAuthorizationError(error.decision, evidence) from error
        except WorkspaceBoundaryError as error:
            duration_ms = self._duration_ms(started_timer)
            self._record_usage(duration_ms, 0)
            evidence = self._error_evidence(
                request,
                started_at,
                duration_ms,
                type(error).__name__,
            )
            self._evidence.append(evidence)
            raise MCPGatewayError("workspace call failed its boundary", evidence) from error
        duration_ms = self._duration_ms(started_timer)
        self._record_usage(duration_ms, result.size_bytes)
        self._evidence.append(result.evidence)
        return result

    @staticmethod
    def _text_result(result: str | Sequence[Any]) -> str:
        if isinstance(result, str):
            return result
        parts: list[str] = []
        for item in result:
            if getattr(item, "type", None) != "text" or not isinstance(
                getattr(item, "text", None), str
            ):
                raise TypeError("MCP gateway accepts only text content")
            parts.append(item.text)
        return "\n".join(parts)

    def _error_evidence(
        self,
        request: ToolRequest,
        started_at: datetime,
        duration_ms: int,
        error_type: str,
    ) -> ToolCallEvidence:
        return self._evidence_store.outcome(
            request,
            status=ToolCallStatus.ERROR,
            producer_id="mcp-gateway",
            started_at=started_at,
            completed_at=datetime.now(UTC),
            duration_ms=duration_ms,
            exit_code=1,
            error_type=error_type[:512],
        )

    def _record_usage(self, elapsed_ms: int, output_bytes: int) -> None:
        self._usage = ToolUsage(
            completed_calls=self._usage.completed_calls + 1,
            elapsed_ms=self._usage.elapsed_ms + elapsed_ms,
            output_bytes=self._usage.output_bytes + output_bytes,
        )

    @staticmethod
    def _duration_ms(started_timer: float) -> int:
        return max(0, int((time.monotonic() - started_timer) * 1_000))
