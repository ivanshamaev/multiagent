import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from contracts import ToolRequest
from runtime.mcp_auth import (
    AuthenticatedMCPGateway,
    MCPAuthenticationError,
    MCPKeyStore,
    MCPTokenAuthority,
    mcp_request_sha256,
)
from runtime.runner_isolation import load_runner_profile

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)


class RecordingGateway:
    def __init__(self) -> None:
        self.requests: list[ToolRequest] = []

    async def execute(self, request: ToolRequest):
        self.requests.append(request)
        return request


def _request(**updates) -> ToolRequest:
    values = {
        "request_id": "request-1",
        "task_id": "task-1",
        "actor_id": "analyst-agent",
        "role": "analyst",
        "call": {"tool": "dbt.list", "resource_type": ["model"]},
    }
    values.update(updates)
    return ToolRequest.model_validate(values)


def _authority() -> MCPTokenAuthority:
    return MCPTokenAuthority({"key-v1": b"a" * 32}, "key-v1")


def test_request_bound_bearer_authenticates_before_gateway_call() -> None:
    identity = load_runner_profile(ROOT, "analyst_v1.json")
    request = _request()
    authority = _authority()
    token = authority.mint(identity, request, now=NOW, ttl_seconds=30)
    gateway = RecordingGateway()
    authenticated = AuthenticatedMCPGateway(
        gateway,
        identity.capability,
        identity,
        authority,  # type: ignore[arg-type]
    )

    result = asyncio.run(authenticated.execute(request, authorization=token, now=NOW))
    claims = authority.verify(token, identity, request, now=NOW)

    assert result == request
    assert gateway.requests == [request]
    assert claims.request_sha256 == mcp_request_sha256(request)
    assert claims.runner_id == "analyst-runner-v1"
    assert claims.profile_id == "analyst-v1"
    assert "a" * 32 not in token
    assert "a" * 32 not in repr(authority)


@pytest.mark.parametrize("mode", ["changed_request", "expired", "tampered", "wrong_key"])
def test_bearer_rejects_cross_scope_and_tampering_before_gateway(mode: str) -> None:
    identity = load_runner_profile(ROOT, "analyst_v1.json")
    request = _request()
    authority = _authority()
    token = authority.mint(identity, request, now=NOW, ttl_seconds=30)
    checked_request = request
    checked_now = NOW
    verifier = authority
    if mode == "changed_request":
        checked_request = _request(request_id="request-2")
    elif mode == "expired":
        checked_now = NOW + timedelta(seconds=31)
    elif mode == "tampered":
        token = token[:-1] + ("A" if token[-1] != "A" else "B")
    else:
        verifier = MCPTokenAuthority({"key-v2": b"b" * 32}, "key-v2")
    gateway = RecordingGateway()
    authenticated = AuthenticatedMCPGateway(
        gateway,
        identity.capability,
        identity,
        verifier,  # type: ignore[arg-type]
    )

    with pytest.raises(MCPAuthenticationError, match="authentication failed") as captured:
        asyncio.run(authenticated.execute(checked_request, authorization=token, now=checked_now))
    assert gateway.requests == []
    assert token not in str(captured.value)


def test_owner_only_key_store_rotates_with_one_previous_key(tmp_path: Path) -> None:
    store = MCPKeyStore(tmp_path, tmp_path / "private" / "mcp-keyring.json")
    first = store.load_or_create()
    identity = load_runner_profile(ROOT, "analyst_v1.json")
    request = _request()
    old_token = first.mint(identity, request, now=NOW)
    second = store.rotate()

    assert first.active_key_id != second.active_key_id
    assert store.path.parent.stat().st_mode & 0o777 == 0o700
    assert store.path.stat().st_mode & 0o777 == 0o600
    assert second.verify(old_token, identity, request, now=NOW).key_id == first.active_key_id
    assert "redacted" in repr(second)
