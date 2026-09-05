"""Content-addressed evidence produced by deterministic tools and validators."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import Field, StrictInt

from contracts.common import (
    FrozenModel,
    Identifier,
    NonEmptyText,
    NonNegativeInt,
    RelativePath,
    Sha256,
    ShortText,
    UtcDateTime,
    VersionedModel,
)


class EvidenceKind(StrEnum):
    COMMAND = "command"
    QUERY = "query"
    TEST = "test"
    ARTIFACT = "artifact"


class ArtifactReference(FrozenModel):
    """Immutable reference to retained output rather than self-reported prose."""

    path: RelativePath
    sha256: Sha256
    media_type: ShortText
    size_bytes: NonNegativeInt


class Evidence(VersionedModel):
    """A tool observation required at workflow gates."""

    evidence_id: Identifier
    task_id: Identifier
    producer_id: Identifier
    kind: EvidenceKind
    source: ShortText
    invocation: NonEmptyText
    exit_code: StrictInt
    artifact: ArtifactReference
    occurred_at: UtcDateTime

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0


EvidenceTuple = Annotated[tuple[Evidence, ...], Field(max_length=256)]
NonEmptyEvidenceTuple = Annotated[tuple[Evidence, ...], Field(min_length=1, max_length=256)]
