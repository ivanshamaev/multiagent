"""Pure deny-by-default authorization for version-one data-engineering tools."""

from __future__ import annotations

import re
import stat
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Annotated, Literal, Self

import sqlglot
from pydantic import Field, StrictBool, StrictInt, model_validator
from sqlglot import exp
from sqlglot.errors import SqlglotError

from contracts.common import FrozenModel, Identifier, NonNegativeInt, RelativePath, ShortText
from contracts.tools import (
    ClickHouseListTablesCall,
    ClickHouseRunQueryCall,
    DatabaseName,
    DbtShowCall,
    ToolName,
    ToolRequest,
    WorkspaceReadCall,
    WorkspaceWriteCall,
)

PROTECTED_PATH_PARTS = frozenset(
    {
        ".env",
        ".git",
        ".scenario-state",
        ".scenario-workspace.json",
        "agents",
        "contracts",
        "grader",
        "orchestrator",
        "plan",
        "policies",
        "runtime",
    }
)
SENSITIVE_FUNCTIONS = frozenset(
    {
        "azureblobstorage",
        "cluster",
        "clusterallreplicas",
        "dictget",
        "dictgetordefault",
        "dictgetornull",
        "executable",
        "file",
        "hdfs",
        "jdbc",
        "mongodb",
        "mysql",
        "odbc",
        "postgresql",
        "redis",
        "remote",
        "remotesecure",
        "s3",
        "url",
    }
)
MAX_PROFILE_BYTES = 32_000

PathPattern = Annotated[str, Field(min_length=1, max_length=512)]
DatabaseTuple = Annotated[tuple[DatabaseName, ...], Field(max_length=32)]
ToolTuple = Annotated[tuple[ToolName, ...], Field(min_length=1, max_length=64)]
PatternTuple = Annotated[tuple[PathPattern, ...], Field(max_length=64)]


def _validate_path_pattern(pattern: str) -> str:
    if (
        not pattern
        or pattern != pattern.strip()
        or "\x00" in pattern
        or "\\" in pattern
        or pattern.startswith("/")
    ):
        raise ValueError("path pattern must be a relative POSIX glob")
    parts = pattern.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("path pattern contains an unsafe component")
    if any(not re.fullmatch(r"[A-Za-z0-9._*-]+", part) for part in parts):
        raise ValueError("path pattern contains unsupported characters")
    if any("**" in part and part != "**" for part in parts):
        raise ValueError("recursive wildcard must occupy a complete path component")
    return pattern


class CapabilityProfile(FrozenModel):
    schema_version: Literal[1] = 1
    profile_id: Identifier
    role: Identifier
    allowed_tools: ToolTuple
    readable_paths: PatternTuple = ()
    writable_paths: PatternTuple = ()
    allowed_databases: DatabaseTuple = ()
    max_query_rows: StrictInt = Field(ge=1, le=1_000)
    max_query_chars: StrictInt = Field(ge=1, le=20_000)
    max_read_bytes: StrictInt = Field(ge=1, le=100_000)
    max_write_bytes: StrictInt = Field(ge=1, le=100_000)
    max_tool_calls: StrictInt = Field(ge=1, le=1_000)
    max_wall_time_seconds: StrictInt = Field(ge=1, le=3_600)
    max_output_bytes: StrictInt = Field(ge=1, le=10_000_000)

    @model_validator(mode="after")
    def validate_allowlists(self) -> Self:
        for field_name in (
            "allowed_tools",
            "readable_paths",
            "writable_paths",
            "allowed_databases",
        ):
            values = getattr(self, field_name)
            if len(values) != len(set(values)):
                raise ValueError(f"{field_name} must not contain duplicates")
        for pattern in (*self.readable_paths, *self.writable_paths):
            _validate_path_pattern(pattern)
        return self


class ToolUsage(FrozenModel):
    completed_calls: NonNegativeInt = 0
    elapsed_ms: NonNegativeInt = 0
    output_bytes: NonNegativeInt = 0


class PolicyCode(StrEnum):
    ALLOWED = "allowed"
    ROLE_DENIED = "role_denied"
    TOOL_DENIED = "tool_denied"
    PATH_DENIED = "path_denied"
    DATABASE_DENIED = "database_denied"
    QUERY_DENIED = "query_denied"
    BUDGET_DENIED = "budget_denied"


class ToolPolicyDecision(FrozenModel):
    allowed: StrictBool
    code: PolicyCode
    reason: ShortText

    @model_validator(mode="after")
    def validate_code(self) -> Self:
        if self.allowed != (self.code is PolicyCode.ALLOWED):
            raise ValueError("allowed flag and policy code disagree")
        return self


def load_capability_profile(path: Path) -> CapabilityProfile:
    """Load a small stable JSON profile without following a symlink."""

    if path.is_symlink():
        raise ValueError("capability profile must not be a symlink")
    try:
        before = path.stat()
    except OSError as error:
        raise ValueError(f"capability profile cannot be read: {type(error).__name__}") from None
    if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_PROFILE_BYTES:
        raise ValueError("capability profile must be a bounded regular file")
    try:
        payload = path.read_bytes()
        after = path.stat()
    except OSError as error:
        raise ValueError(f"capability profile cannot be read: {type(error).__name__}") from None
    before_identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    after_identity = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if before_identity != after_identity or len(payload) != before.st_size:
        raise ValueError("capability profile changed while reading")
    try:
        return CapabilityProfile.model_validate_json(payload)
    except ValueError as error:
        raise ValueError("capability profile is not valid version-one JSON") from error


def _glob_matches(path: str, pattern: str) -> bool:
    sentinel = "\x00RECURSIVE\x00"
    expression = re.escape(pattern).replace(r"\*\*", sentinel).replace(r"\*", "[^/]*")
    expression = expression.replace(sentinel, ".*")
    return re.fullmatch(expression, path) is not None


def _path_is_allowed(path: RelativePath, patterns: tuple[str, ...]) -> bool:
    parts = PurePosixPath(path).parts
    if any(part in PROTECTED_PATH_PARTS for part in parts):
        return False
    return any(_glob_matches(path, pattern) for pattern in patterns)


def _query_denial(
    query: str,
    profile: CapabilityProfile,
    *,
    require_literal_limit: bool = True,
) -> str | None:
    if len(query) > profile.max_query_chars:
        return "query exceeds the profile character limit"
    try:
        statements = [item for item in sqlglot.parse(query, read="clickhouse") if item is not None]
    except SqlglotError:
        return "query does not parse as ClickHouse SQL"
    if len(statements) != 1:
        return "exactly one SQL statement is required"
    statement = statements[0]
    if not isinstance(statement, exp.Query):
        return "only read query expressions are allowed"
    if any(node.args.get("settings") for node in statement.walk()):
        return "query SETTINGS are not allowed"

    limit = statement.args.get("limit")
    if require_literal_limit:
        if (
            limit is None
            or not isinstance(limit.expression, exp.Literal)
            or not limit.expression.is_int
        ):
            return "a literal top-level LIMIT is required"
        row_limit = int(limit.expression.this)
        if row_limit < 1 or row_limit > profile.max_query_rows:
            return "query LIMIT is outside the profile row bound"
    elif limit is not None:
        return "dbt show SQL must use the separately bounded limit argument"

    cte_names = {cte.alias_or_name.casefold() for cte in statement.find_all(exp.CTE)}
    for table in statement.find_all(exp.Table):
        if not isinstance(table.this, exp.Identifier):
            return "table functions are not allowed"
        if table.catalog:
            return "catalog-qualified tables are not allowed"
        database = table.db
        if not database:
            if table.name.casefold() not in cte_names:
                return "physical tables must use an allowed database qualifier"
        elif database not in profile.allowed_databases:
            return "query database is not allowed by the profile"

    for function in statement.find_all(exp.Anonymous):
        if function.name.casefold() in SENSITIVE_FUNCTIONS:
            return "external or dictionary functions are not allowed"
    return None


def _deny(code: PolicyCode, reason: str) -> ToolPolicyDecision:
    return ToolPolicyDecision(allowed=False, code=code, reason=reason)


def authorize_tool_call(
    profile: CapabilityProfile,
    request: ToolRequest,
    usage: ToolUsage,
) -> ToolPolicyDecision:
    """Authorize a validated call without performing I/O or trusting prompt content."""

    if request.role != profile.role:
        return _deny(PolicyCode.ROLE_DENIED, "request role does not match the capability profile")
    tool = ToolName(request.call.tool)
    if tool not in profile.allowed_tools:
        return _deny(PolicyCode.TOOL_DENIED, "tool is not present in the exact allowlist")
    if (
        usage.completed_calls >= profile.max_tool_calls
        or usage.elapsed_ms >= profile.max_wall_time_seconds * 1_000
        or usage.output_bytes >= profile.max_output_bytes
    ):
        return _deny(PolicyCode.BUDGET_DENIED, "one or more tool budgets are exhausted")

    call = request.call
    if isinstance(call, WorkspaceReadCall):
        if not _path_is_allowed(call.path, profile.readable_paths):
            return _deny(PolicyCode.PATH_DENIED, "workspace path is not readable by this profile")
    elif isinstance(call, WorkspaceWriteCall):
        if not _path_is_allowed(call.path, profile.writable_paths):
            return _deny(PolicyCode.PATH_DENIED, "workspace path is not writable by this profile")
        if len(call.content.encode("utf-8")) > profile.max_write_bytes:
            return _deny(PolicyCode.PATH_DENIED, "workspace write exceeds the byte limit")
    elif isinstance(call, ClickHouseListTablesCall):
        if call.database not in profile.allowed_databases:
            return _deny(PolicyCode.DATABASE_DENIED, "database is not present in the allowlist")
    elif isinstance(call, ClickHouseRunQueryCall):
        if reason := _query_denial(call.query, profile):
            return _deny(PolicyCode.QUERY_DENIED, reason)
    elif isinstance(call, DbtShowCall):
        if call.limit > profile.max_query_rows:
            return _deny(PolicyCode.QUERY_DENIED, "dbt show limit exceeds the profile row bound")
        if reason := _query_denial(
            call.sql_query,
            profile,
            require_literal_limit=False,
        ):
            return _deny(PolicyCode.QUERY_DENIED, reason)
    return ToolPolicyDecision(allowed=True, code=PolicyCode.ALLOWED, reason="allowed by profile")
