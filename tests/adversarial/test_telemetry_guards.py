from pathlib import Path

import pytest

from runtime.telemetry import SanitizedJsonSpanExporter, TelemetryError


def test_trace_exporter_rejects_escape_and_symlink_paths(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside.jsonl"
    with pytest.raises(TelemetryError, match="escaped"):
        SanitizedJsonSpanExporter(tmp_path, outside)

    target = tmp_path / "target.jsonl"
    target.touch(mode=0o600)
    link = tmp_path / "trace-link.jsonl"
    link.symlink_to(target)
    with pytest.raises(TelemetryError, match="symlink"):
        SanitizedJsonSpanExporter(tmp_path, link)


def test_trace_exporter_rejects_shared_directory_and_file_modes(tmp_path: Path) -> None:
    shared = tmp_path / "shared"
    shared.mkdir(mode=0o755)
    shared.chmod(0o755)
    with pytest.raises(TelemetryError, match="0700"):
        SanitizedJsonSpanExporter(tmp_path, shared / "spans.jsonl")

    private = tmp_path / "private"
    private.mkdir(mode=0o700)
    output = private / "spans.jsonl"
    output.touch(mode=0o644)
    output.chmod(0o644)
    with pytest.raises(TelemetryError, match="0600"):
        SanitizedJsonSpanExporter(tmp_path, output)
