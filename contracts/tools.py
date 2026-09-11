"""Strict version-one contracts for bounded tool requests and retained evidence."""

from __future__ import annotations

import json
import re
from enum import StrEnum
from hashlib import sha256
from typing import Annotated, Literal, Self

from pydantic import (
    ConfigDict,
    Field,
    StrictInt,
    StringConstraints,
    field_validator,
    model_validator,
)

from contracts.common import (
    FrozenModel,
    Identifier,
    NonNegativeInt,
    RelativePath,
    Sha256,
    ShortText,
    UtcDateTime,
    VersionedModel,
)
from contracts.evidence import ArtifactReference

DatabaseName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
    ),
]
QueryText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=20_000),
]
WorkspaceContent = Annotated[str, StringConstraints(max_length=100_000)]
OptionalPattern = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=256),
]


class ToolName(StrEnum):
    WORKSPACE_READ_FILE = "workspace.read_file"
    WORKSPACE_WRITE_FILE = "workspace.write_file"
    CLICKHOUSE_LIST_DATABASES = "clickhouse.list_databases"
    CLICKHOUSE_LIST_TABLES = "clickhouse.list_tables"
    CLICKHOUSE_RUN_QUERY = "clickhouse.run_query"
    DBT_PARSE = "dbt.parse"
    DBT_COMPILE = "dbt.compile"
    DBT_BUILD = "dbt.build"
    DBT_TEST = "dbt.test"
    DBT_SHOW = "dbt.show"
    DBT_LIST = "dbt.list"
    DBT_GET_LINEAGE_DEV = "dbt.get_lineage_dev"
    DBT_GET_NODE_DETAILS_DEV = "dbt.get_node_details_dev"


class DbtResourceType(StrEnum):
    MODEL = "model"
    SEED = "seed"
    SNAPSHOT = "snapshot"
    SOURCE = "source"
    TEST = "test"


def _safe_dbt_selector(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_+.@,:/*-]+(?: [A-Za-z0-9_+.@,:/*-]+)*", value):
        raise ValueError("dbt selector contains unsupported characters")
    if any(token.startswith("-") for token in value.split()):
        raise ValueError("dbt selector tokens must not look like options")
    return value


class WorkspaceReadCall(FrozenModel):
    tool: Literal[ToolName.WORKSPACE_READ_FILE] = ToolName.WORKSPACE_READ_FILE
    path: RelativePath


class WorkspaceWriteCall(FrozenModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=False,
        validate_default=True,
    )

    tool: Literal[ToolName.WORKSPACE_WRITE_FILE] = ToolName.WORKSPACE_WRITE_FILE
    path: RelativePath
    content: WorkspaceContent = Field(repr=False)


class ClickHouseListDatabasesCall(FrozenModel):
    tool: Literal[ToolName.CLICKHOUSE_LIST_DATABASES] = ToolName.CLICKHOUSE_LIST_DATABASES


class ClickHouseListTablesCall(FrozenModel):
    tool: Literal[ToolName.CLICKHOUSE_LIST_TABLES] = ToolName.CLICKHOUSE_LIST_TABLES
    database: DatabaseName
    page_size: StrictInt = Field(default=50, ge=1, le=100)
    include_detailed_columns: bool = False
    like: OptionalPattern | None = None
    not_like: OptionalPattern | None = None
    page_token: OptionalPattern | None = None


class ClickHouseRunQueryCall(FrozenModel):
    tool: Literal[ToolName.CLICKHOUSE_RUN_QUERY] = ToolName.CLICKHOUSE_RUN_QUERY
    query: QueryText


class DbtParseCall(FrozenModel):
    tool: Literal[ToolName.DBT_PARSE] = ToolName.DBT_PARSE


class DbtSelectionCall(FrozenModel):
    node_selection: str | None = Field(default=None, min_length=1, max_length=512)
    yml_selector: Identifier | None = None

    @field_validator("node_selection")
    @classmethod
    def safe_node_selection(cls, value: str | None) -> str | None:
        return None if value is None else _safe_dbt_selector(value.strip())

    @model_validator(mode="after")
    def selectors_are_mutually_exclusive(self) -> Self:
        if self.node_selection is not None and self.yml_selector is not None:
            raise ValueError("node_selection and yml_selector are mutually exclusive")
        return self


class DbtCompileCall(DbtSelectionCall):
    tool: Literal[ToolName.DBT_COMPILE] = ToolName.DBT_COMPILE


class DbtBuildCall(DbtSelectionCall):
    tool: Literal[ToolName.DBT_BUILD] = ToolName.DBT_BUILD


class DbtTestCall(DbtSelectionCall):
    tool: Literal[ToolName.DBT_TEST] = ToolName.DBT_TEST


class DbtShowCall(FrozenModel):
    tool: Literal[ToolName.DBT_SHOW] = ToolName.DBT_SHOW
    sql_query: QueryText
    limit: StrictInt = Field(default=5, ge=1, le=100)


class DbtListCall(FrozenModel):
    tool: Literal[ToolName.DBT_LIST] = ToolName.DBT_LIST
    node_selection: str | None = Field(default=None, min_length=1, max_length=512)
    yml_selector: Identifier | None = None
    resource_type: Annotated[tuple[DbtResourceType, ...], Field(max_length=5)] = ()

    @field_validator("node_selection")
    @classmethod
    def safe_node_selection(cls, value: str | None) -> str | None:
        return None if value is None else _safe_dbt_selector(value.strip())

    @model_validator(mode="after")
    def validate_list_filters(self) -> Self:
        if self.node_selection is not None and self.yml_selector is not None:
            raise ValueError("node_selection and yml_selector are mutually exclusive")
        if len(self.resource_type) != len(set(self.resource_type)):
            raise ValueError("resource_type must not contain duplicates")
        return self


class DbtGetLineageCall(FrozenModel):
    tool: Literal[ToolName.DBT_GET_LINEAGE_DEV] = ToolName.DBT_GET_LINEAGE_DEV
    unique_id: Identifier
    depth: StrictInt = Field(default=1, ge=0, le=5)


class DbtGetNodeDetailsCall(FrozenModel):
    tool: Literal[ToolName.DBT_GET_NODE_DETAILS_DEV] = ToolName.DBT_GET_NODE_DETAILS_DEV
    node_id: Identifier


ToolCall = Annotated[
    WorkspaceReadCall
    | WorkspaceWriteCall
    | ClickHouseListDatabasesCall
    | ClickHouseListTablesCall
    | ClickHouseRunQueryCall
    | DbtParseCall
    | DbtCompileCall
    | DbtBuildCall
    | DbtTestCall
    | DbtShowCall
    | DbtListCall
    | DbtGetLineageCall
    | DbtGetNodeDetailsCall,
    Field(discriminator="tool"),
]


class ToolRequest(VersionedModel):
    request_id: Identifier
    task_id: Identifier
    actor_id: Identifier
    role: Identifier
    call: ToolCall


class ToolCallStatus(StrEnum):
    SUCCESS = "success"
    DENIED = "denied"
    ERROR = "error"
    TIMEOUT = "timeout"


class ToolCallEvidence(VersionedModel):
    """Secret-free metadata plus an optional content-addressed retained output."""

    evidence_id: Identifier
    request_id: Identifier
    task_id: Identifier
    producer_id: Identifier
    tool: ToolName
    arguments_sha256: Sha256
    started_at: UtcDateTime
    completed_at: UtcDateTime
    status: ToolCallStatus
    exit_code: StrictInt | None = None
    duration_ms: NonNegativeInt
    output_bytes: NonNegativeInt
    output: ArtifactReference | None = None
    error_type: ShortText | None = None

    @model_validator(mode="after")
    def validate_outcome(self) -> Self:
        if self.completed_at < self.started_at:
            raise ValueError("tool evidence cannot complete before it starts")
        if self.output is not None and self.output.size_bytes != self.output_bytes:
            raise ValueError("tool evidence output size does not match its artifact")
        if self.output is None and self.output_bytes != 0:
            raise ValueError("tool evidence without an artifact must have zero output bytes")
        if self.status is ToolCallStatus.SUCCESS:
            if self.exit_code != 0 or self.output is None or self.error_type is not None:
                raise ValueError("successful tool evidence requires exit 0 and retained output")
        elif self.status is ToolCallStatus.DENIED:
            if self.exit_code is not None or self.output is not None or self.error_type is None:
                raise ValueError("denied tool evidence must not contain process output")
        elif self.status is ToolCallStatus.ERROR:
            if self.exit_code in {None, 0} or self.error_type is None:
                raise ValueError("error tool evidence requires a non-zero exit and error type")
        elif self.exit_code is not None or self.error_type is None:
            raise ValueError("timeout tool evidence requires an error type and no exit code")
        return self


class ToolResult(VersionedModel):
    """Bounded untrusted content tied to independently retained execution evidence."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=False,
        validate_default=True,
    )

    request_id: Identifier
    task_id: Identifier
    tool: ToolName
    content: Annotated[str, StringConstraints(max_length=2_000_000)] = Field(repr=False)
    content_type: ShortText
    size_bytes: NonNegativeInt
    sha256: Sha256
    evidence: ToolCallEvidence

    @model_validator(mode="after")
    def validate_content_address(self) -> Self:
        encoded = self.content.encode("utf-8")
        if self.size_bytes != len(encoded) or self.sha256 != sha256(encoded).hexdigest():
            raise ValueError("tool result content address does not match content")
        if (
            self.evidence.status is not ToolCallStatus.SUCCESS
            or self.evidence.request_id != self.request_id
            or self.evidence.task_id != self.task_id
            or self.evidence.tool != self.tool
            or self.evidence.output is None
            or self.evidence.output.sha256 != self.sha256
            or self.evidence.output.size_bytes != self.size_bytes
            or self.evidence.output.media_type != self.content_type
        ):
            raise ValueError("tool result does not match its successful evidence")
        return self


def tool_arguments_sha256(call: ToolCall) -> str:
    """Hash canonical arguments without retaining their potentially sensitive contents."""

    encoded = json.dumps(
        call.model_dump(mode="json", exclude={"tool"}),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()
