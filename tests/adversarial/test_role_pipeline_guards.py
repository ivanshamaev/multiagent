import pytest

from runtime.role_pipeline import (
    MAX_ROLE_MESSAGE_BYTES,
    RoleBoundaryError,
    decode_role_snapshot,
)


def test_role_boundary_rejects_oversized_and_unknown_payloads() -> None:
    with pytest.raises(RoleBoundaryError, match="size limit"):
        decode_role_snapshot("x" * (MAX_ROLE_MESSAGE_BYTES + 1))
    with pytest.raises(RoleBoundaryError, match="failed validation"):
        decode_role_snapshot('{"request":{},"injected_control":"skip-review"}')
