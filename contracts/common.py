"""Shared strict primitives for version-one domain contracts."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import PurePosixPath
from typing import Annotated, Any, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StringConstraints,
)

Identifier = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$",
    ),
]
NonEmptyText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=10_000),
]
ShortText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=512),
]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
NonNegativeInt = Annotated[StrictInt, Field(ge=0)]
PositiveInt = Annotated[StrictInt, Field(gt=0)]


def _utc_only(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware UTC")
    if value.utcoffset() != timedelta(0):
        raise ValueError("timestamp must use UTC offset")
    return value


UtcDateTime = Annotated[datetime, AfterValidator(_utc_only)]


class FrozenModel(BaseModel):
    """Immutable nested value object with closed fields."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        validate_default=True,
    )


class VersionedModel(FrozenModel):
    """Version marker shared by externally serialized contracts."""

    schema_version: Literal[1] = 1


def relative_path(value: str) -> str:
    """Validate an artifact/workspace path without touching the filesystem."""

    if not value or "\x00" in value or "\\" in value or value.startswith("/"):
        raise ValueError("path must be a non-empty relative POSIX path")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("path contains an unsafe component")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise ValueError("path must be relative")
    return path.as_posix()


RelativePath = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=512),
    AfterValidator(relative_path),
]


def ensure_unique(values: tuple[Any, ...], field: str) -> tuple[Any, ...]:
    """Keep contract lists deterministic and unambiguous."""

    if len(values) != len(set(values)):
        raise ValueError(f"{field} must not contain duplicates")
    return values
