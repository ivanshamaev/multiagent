"""Request-bound local bearer authentication in front of the MCP policy gateway."""

from __future__ import annotations

import base64
import binascii
import hmac
import json
import os
import stat
import tempfile
from collections.abc import Mapping
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Protocol

from pydantic import Field, StringConstraints

from contracts import ToolRequest, ToolResult
from contracts.common import FrozenModel, Identifier, Sha256
from policies import CapabilityProfile
from runtime.runner_isolation import LoadedRunnerProfile

MCP_AUTH_ISSUER = "agentic-control-plane"
MCP_AUTH_AUDIENCE = "local-mcp-gateway"
MAX_MCP_TOKEN_BYTES = 4_096
MAX_MCP_TOKEN_TTL_SECONDS = 300
MAX_MCP_KEYRING_BYTES = 4_096
MIN_MCP_KEY_BYTES = 32

Base64Url = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_-]+$")]


class MCPAuthenticationError(RuntimeError):
    """A bearer credential failed closed without exposing credential material."""


class MCPTokenClaims(FrozenModel):
    version: int = Field(ge=1, le=1)
    issuer: str = Field(min_length=1, max_length=64)
    audience: str = Field(min_length=1, max_length=64)
    key_id: Identifier
    runner_id: Identifier
    profile_id: Identifier
    role: Identifier
    actor_id: Identifier
    task_id: Identifier
    request_sha256: Sha256
    issued_at: int = Field(ge=0)
    expires_at: int = Field(ge=0)


class MCPKeyringDocument(FrozenModel):
    schema_version: int = Field(ge=1, le=1)
    active_key_id: Identifier
    keys: dict[Identifier, Base64Url] = Field(min_length=1, max_length=2)


class MCPGatewayProtocol(Protocol):
    @property
    def allowed_tools(self): ...

    async def execute(self, request: ToolRequest) -> ToolResult: ...


def mcp_request_sha256(request: ToolRequest) -> str:
    canonical = json.dumps(
        request.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    try:
        padding = "=" * (-len(value) % 4)
        decoded = base64.b64decode(value + padding, altchars=b"-_", validate=True)
        if _encode(decoded) != value:
            raise ValueError("non-canonical base64url")
        return decoded
    except (ValueError, binascii.Error, UnicodeEncodeError):
        raise MCPAuthenticationError("MCP bearer authentication failed") from None


def _strict_json(value: bytes) -> dict:
    def unique_pairs(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = item
        return result

    try:
        decoded = json.loads(value, object_pairs_hook=unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise MCPAuthenticationError("MCP bearer authentication failed") from None
    if not isinstance(decoded, dict):
        raise MCPAuthenticationError("MCP bearer authentication failed")
    return decoded


class MCPTokenAuthority:
    """Mint and verify short-lived request-bound HS256 credentials."""

    def __init__(self, keys: Mapping[str, bytes], active_key_id: str) -> None:
        if not 1 <= len(keys) <= 2 or active_key_id not in keys:
            raise MCPAuthenticationError("MCP keyring configuration is invalid")
        if any(len(secret) < MIN_MCP_KEY_BYTES for secret in keys.values()):
            raise MCPAuthenticationError("MCP keyring configuration is invalid")
        self._keys = dict(keys)
        self.active_key_id = active_key_id

    def __repr__(self) -> str:
        return f"MCPTokenAuthority(active_key_id={self.active_key_id!r}, keys=<redacted>)"

    def mint(
        self,
        identity: LoadedRunnerProfile,
        request: ToolRequest,
        *,
        now: datetime,
        ttl_seconds: int = 60,
    ) -> str:
        capability = identity.capability
        runner = identity.runner
        if capability is None:
            raise MCPAuthenticationError("runner has no MCP capability profile")
        if now.tzinfo is None or now.utcoffset() is None:
            raise MCPAuthenticationError("MCP credential time must be timezone-aware")
        if not 1 <= ttl_seconds <= MAX_MCP_TOKEN_TTL_SECONDS:
            raise MCPAuthenticationError("MCP credential TTL is outside the allowed bound")
        if request.role != runner.role or request.actor_id != runner.actor_id:
            raise MCPAuthenticationError("MCP request identity does not match runner")
        issued_at = int(now.astimezone(UTC).timestamp())
        claims = MCPTokenClaims(
            version=1,
            issuer=MCP_AUTH_ISSUER,
            audience=MCP_AUTH_AUDIENCE,
            key_id=self.active_key_id,
            runner_id=runner.runner_id,
            profile_id=capability.profile_id,
            role=runner.role,
            actor_id=runner.actor_id,
            task_id=request.task_id,
            request_sha256=mcp_request_sha256(request),
            issued_at=issued_at,
            expires_at=issued_at + ttl_seconds,
        )
        header = {"alg": "HS256", "kid": self.active_key_id, "typ": "MCP"}
        encoded_header = _encode(
            json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
        encoded_claims = _encode(claims.model_dump_json(exclude_none=True).encode("utf-8"))
        signed = f"{encoded_header}.{encoded_claims}".encode("ascii")
        signature = hmac.new(self._keys[self.active_key_id], signed, sha256).digest()
        return f"Bearer {encoded_header}.{encoded_claims}.{_encode(signature)}"

    def verify(
        self,
        authorization: str,
        identity: LoadedRunnerProfile,
        request: ToolRequest,
        *,
        now: datetime,
    ) -> MCPTokenClaims:
        try:
            if now.tzinfo is None or now.utcoffset() is None:
                raise MCPAuthenticationError("MCP bearer authentication failed")
            if not isinstance(authorization, str) or not authorization.startswith("Bearer "):
                raise MCPAuthenticationError("MCP bearer authentication failed")
            token = authorization.removeprefix("Bearer ")
            if len(token.encode("ascii")) > MAX_MCP_TOKEN_BYTES:
                raise MCPAuthenticationError("MCP bearer authentication failed")
            parts = token.split(".")
            if len(parts) != 3 or any(not part for part in parts):
                raise MCPAuthenticationError("MCP bearer authentication failed")
            header = _strict_json(_decode(parts[0]))
            if set(header) != {"alg", "kid", "typ"}:
                raise MCPAuthenticationError("MCP bearer authentication failed")
            if header["alg"] != "HS256" or header["typ"] != "MCP":
                raise MCPAuthenticationError("MCP bearer authentication failed")
            key_id = header["kid"]
            if not isinstance(key_id, str) or key_id not in self._keys:
                raise MCPAuthenticationError("MCP bearer authentication failed")
            signed = f"{parts[0]}.{parts[1]}".encode("ascii")
            expected = hmac.new(self._keys[key_id], signed, sha256).digest()
            if not hmac.compare_digest(expected, _decode(parts[2])):
                raise MCPAuthenticationError("MCP bearer authentication failed")
            claims = MCPTokenClaims.model_validate(_strict_json(_decode(parts[1])), strict=True)
            capability = identity.capability
            if capability is None:
                raise MCPAuthenticationError("MCP bearer authentication failed")
            current = int(now.astimezone(UTC).timestamp())
            expected_claims = {
                "issuer": MCP_AUTH_ISSUER,
                "audience": MCP_AUTH_AUDIENCE,
                "key_id": key_id,
                "runner_id": identity.runner.runner_id,
                "profile_id": capability.profile_id,
                "role": identity.runner.role,
                "actor_id": identity.runner.actor_id,
                "task_id": request.task_id,
                "request_sha256": mcp_request_sha256(request),
            }
            if any(getattr(claims, field) != value for field, value in expected_claims.items()):
                raise MCPAuthenticationError("MCP bearer authentication failed")
            if (
                claims.issued_at > current
                or claims.expires_at <= current
                or claims.expires_at - claims.issued_at > MAX_MCP_TOKEN_TTL_SECONDS
            ):
                raise MCPAuthenticationError("MCP bearer authentication failed")
            return claims
        except (UnicodeEncodeError, ValueError):
            raise MCPAuthenticationError("MCP bearer authentication failed") from None


class AuthenticatedMCPGateway:
    """Authenticate runner/request scope before deterministic MCP authorization."""

    def __init__(
        self,
        gateway: MCPGatewayProtocol,
        profile: CapabilityProfile,
        identity: LoadedRunnerProfile,
        authority: MCPTokenAuthority,
    ) -> None:
        if (
            identity.capability is None
            or identity.capability.profile_id != profile.profile_id
            or identity.runner.role != profile.role
        ):
            raise MCPAuthenticationError("runner and MCP capability profiles do not match")
        self._gateway = gateway
        self._profile = profile
        self._identity = identity
        self._authority = authority

    @property
    def allowed_tools(self):
        return self._gateway.allowed_tools

    async def execute(
        self,
        request: ToolRequest,
        *,
        authorization: str,
        now: datetime | None = None,
    ) -> ToolResult:
        self._authority.verify(
            authorization,
            self._identity,
            request,
            now=now or datetime.now(UTC),
        )
        if request.role != self._profile.role:
            raise MCPAuthenticationError("MCP bearer authentication failed")
        return await self._gateway.execute(request)


class MCPKeyStore:
    """Owner-only repository-contained signing key storage with two-key rotation."""

    def __init__(self, repository_root: Path, keyring_path: Path) -> None:
        if repository_root.is_symlink():
            raise MCPAuthenticationError("MCP key repository root must not be a symlink")
        root = repository_root.resolve(strict=True)
        if not keyring_path.is_absolute():
            raise MCPAuthenticationError("MCP keyring path must be absolute")
        try:
            relative = keyring_path.relative_to(root)
        except ValueError:
            raise MCPAuthenticationError("MCP keyring escaped repository") from None
        current = root
        for component in relative.parts:
            current /= component
            if current.is_symlink():
                raise MCPAuthenticationError("MCP keyring path contains a symlink")
        resolved = keyring_path.resolve(strict=False)
        if not resolved.is_relative_to(root):
            raise MCPAuthenticationError("MCP keyring escaped repository")
        resolved.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if stat.S_IMODE(resolved.parent.stat().st_mode) != 0o700:
            raise MCPAuthenticationError("MCP keyring directory must have mode 0700")
        self.path = resolved

    def load_or_create(self) -> MCPTokenAuthority:
        if not self.path.exists():
            secret = os.urandom(32)
            key_id = f"key-{sha256(secret).hexdigest()[:16]}"
            self._write(
                MCPKeyringDocument(
                    schema_version=1,
                    active_key_id=key_id,
                    keys={key_id: _encode(secret)},
                ),
                create=True,
            )
        return self.load()

    def load(self) -> MCPTokenAuthority:
        payload = self._read()
        try:
            document = MCPKeyringDocument.model_validate_json(payload, strict=True)
            keys = {key_id: _decode(secret) for key_id, secret in document.keys.items()}
        except (ValueError, MCPAuthenticationError):
            raise MCPAuthenticationError("MCP keyring content is invalid") from None
        if document.active_key_id not in keys:
            raise MCPAuthenticationError("MCP keyring content is invalid")
        return MCPTokenAuthority(keys, document.active_key_id)

    def rotate(self) -> MCPTokenAuthority:
        try:
            old_document = MCPKeyringDocument.model_validate_json(self._read(), strict=True)
        except ValueError:
            raise MCPAuthenticationError("MCP keyring content is invalid") from None
        secret = os.urandom(32)
        key_id = f"key-{sha256(secret).hexdigest()[:16]}"
        keys = {
            old_document.active_key_id: old_document.keys[old_document.active_key_id],
            key_id: _encode(secret),
        }
        document = MCPKeyringDocument(schema_version=1, active_key_id=key_id, keys=keys)
        self._write(document, create=False)
        return MCPTokenAuthority(
            {item: _decode(value) for item, value in document.keys.items()}, key_id
        )

    def _read(self) -> bytes:
        if self.path.is_symlink():
            raise MCPAuthenticationError("MCP keyring must not be a symlink")
        try:
            before = self.path.stat()
            payload = self.path.read_bytes()
            after = self.path.stat()
        except OSError as error:
            raise MCPAuthenticationError(
                f"MCP keyring cannot be read: {type(error).__name__}"
            ) from None
        before_id = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        after_id = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if (
            not stat.S_ISREG(before.st_mode)
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_size > MAX_MCP_KEYRING_BYTES
            or before_id != after_id
            or len(payload) != before.st_size
        ):
            raise MCPAuthenticationError("MCP keyring must be a stable mode-0600 bounded file")
        return payload

    def _write(self, document: MCPKeyringDocument, *, create: bool) -> None:
        payload = (document.model_dump_json() + "\n").encode("utf-8")
        if len(payload) > MAX_MCP_KEYRING_BYTES:
            raise MCPAuthenticationError("MCP keyring exceeds size limit")
        if create:
            try:
                descriptor = os.open(
                    self.path,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600,
                )
            except FileExistsError:
                return
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            self.path.chmod(0o600)
            return
        descriptor, temporary_name = tempfile.mkstemp(prefix=".mcp-keyring-", dir=self.path.parent)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                os.fchmod(stream.fileno(), 0o600)
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
            self.path.chmod(0o600)
        finally:
            if temporary.exists():
                temporary.unlink()
