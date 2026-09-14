import asyncio
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from contracts import ToolRequest
from policies import load_capability_profile
from runtime.mcp_auth import AuthenticatedMCPGateway, MCPAuthenticationError, MCPTokenAuthority
from runtime.runner_isolation import load_runner_profile
from runtime.tools import MCPToolGateway, ToolEvidenceStore

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)


class RecordingCaller:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def call_tool(self, tool_name: str, **kwargs: Any) -> str:
        self.calls.append((tool_name, kwargs))
        return "OK"


def test_authenticated_runner_request_reaches_real_policy_gateway_without_token_passthrough(
    tmp_path: Path,
) -> None:
    identity = load_runner_profile(ROOT, "data_engineer_v1.json")
    profile = load_capability_profile(ROOT / "policies/profiles/data_engineer_v1.json")
    dbt = RecordingCaller()
    store = ToolEvidenceStore(tmp_path, tmp_path / ".scenario-state")
    gateway = MCPToolGateway(profile, RecordingCaller(), dbt, store)
    authority = MCPTokenAuthority({"key-v1": b"a" * 32}, "key-v1")
    authenticated = AuthenticatedMCPGateway(gateway, profile, identity, authority)
    request = ToolRequest(
        request_id="request-1",
        task_id="task-1",
        actor_id="data-engineer-agent",
        role="data-engineer",
        call={"tool": "dbt.parse"},
    )
    token = authority.mint(identity, request, now=NOW)

    with pytest.raises(MCPAuthenticationError):
        asyncio.run(authenticated.execute(request, authorization="", now=NOW))
    result = asyncio.run(authenticated.execute(request, authorization=token, now=NOW))

    assert dbt.calls == [("parse", {})]
    assert result.content == "OK"
    assert token not in result.model_dump_json()
    evidence_path = tmp_path / result.evidence.output.path  # type: ignore[union-attr]
    assert token not in evidence_path.read_text(encoding="utf-8")
