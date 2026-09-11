"""Trusted loading of immutable human-authored scenario specifications."""

from __future__ import annotations

import stat
from hashlib import sha256
from pathlib import Path

from contracts import ScenarioSpecification
from runtime.scenario_harness import HarnessError, load_manifest, verify_workspace

MAX_SPECIFICATION_BYTES = 64_000


class SpecificationBoundaryError(RuntimeError):
    """A scenario specification was missing, unstable, or inconsistent."""


def _stable_regular_file(path: Path, workspace: Path) -> bytes:
    if path.is_symlink():
        raise SpecificationBoundaryError("specification input must not be a symlink")
    try:
        resolved = path.resolve(strict=True)
        before = path.stat(follow_symlinks=False)
    except OSError as error:
        raise SpecificationBoundaryError(
            f"specification input cannot be resolved: {type(error).__name__}"
        ) from None
    if not resolved.is_relative_to(workspace) or not stat.S_ISREG(before.st_mode):
        raise SpecificationBoundaryError("specification input escaped the workspace")
    if before.st_size > MAX_SPECIFICATION_BYTES:
        raise SpecificationBoundaryError("specification input exceeds the byte limit")
    try:
        contents = path.read_bytes()
        after = path.stat(follow_symlinks=False)
    except OSError as error:
        raise SpecificationBoundaryError(
            f"specification input cannot be read: {type(error).__name__}"
        ) from None
    before_identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    after_identity = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if before_identity != after_identity or len(contents) != before.st_size:
        raise SpecificationBoundaryError("specification input changed while reading")
    return contents


def load_scenario_specification(
    repository_root: Path,
    scenario_id: str,
    *,
    requested_state_root: Path | None = None,
) -> ScenarioSpecification:
    """Load a typed specification only after verifying its managed workspace."""

    manifest = load_manifest(repository_root, scenario_id)
    try:
        status = verify_workspace(
            repository_root,
            manifest,
            requested_state_root=requested_state_root,
        )
    except HarnessError as error:
        raise SpecificationBoundaryError(str(error)) from None
    workspace = Path(str(status["workspace"])).resolve(strict=True)
    specification_path = workspace / f"scenarios/{scenario_id}/specification.json"
    task_path = workspace / "TASK.md"
    specification_bytes = _stable_regular_file(specification_path, workspace)
    task_bytes = _stable_regular_file(task_path, workspace)
    try:
        envelope = ScenarioSpecification.model_validate_json(specification_bytes)
    except ValueError as error:
        raise SpecificationBoundaryError(
            "scenario specification is not valid version-one JSON"
        ) from error
    if envelope.scenario_id != manifest.scenario_id:
        raise SpecificationBoundaryError("specification scenario does not match the manifest")
    if envelope.scenario_version != manifest.version:
        raise SpecificationBoundaryError("specification version does not match the manifest")
    if envelope.task_sha256 != sha256(task_bytes).hexdigest():
        raise SpecificationBoundaryError("specification task hash does not match TASK.md")
    return envelope
