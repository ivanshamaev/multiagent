"""Independent, allowlisted validation of an autonomous scenario candidate."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from math import ceil
from pathlib import Path
from typing import Protocol

from contracts import (
    ArtifactReference,
    Evidence,
    EvidenceKind,
    ValidationDecision,
    ValidationResult,
)
from contracts.common import UtcDateTime
from orchestrator import (
    BudgetCharge,
    Stage,
    TransitionCommand,
    WorkflowEvent,
    WorkflowState,
    append_transition,
    verify_event_chain,
)
from runtime.scenario_harness import load_manifest

MAX_VALIDATION_OUTPUT_BYTES = 2_000_000
_PASSTHROUGH_ENVIRONMENT = frozenset(
    {"HOME", "LANG", "LC_ALL", "PATH", "TERM", "USER", "XDG_RUNTIME_DIR"}
)


class ValidationBoundaryError(RuntimeError):
    """Validator input or retained output crossed a trusted boundary."""


class ValidationGate(StrEnum):
    WORKSPACE_INTEGRITY = "workspace-integrity"
    PUBLIC_BUILD = "public-build"
    INDEPENDENT_SQL = "independent-sql"
    POLICY = "repository-policy"


@dataclass(frozen=True)
class ValidationCommand:
    gate: ValidationGate
    argv: tuple[str, ...]
    timeout_seconds: int


@dataclass(frozen=True)
class ValidationGateOutcome:
    evidence: Evidence
    duration_ms: int
    infrastructure_error: bool = False


@dataclass(frozen=True)
class ValidationRunResult:
    artifact: ValidationResult
    state: WorkflowState
    events: tuple[WorkflowEvent, ...]
    outcomes: tuple[ValidationGateOutcome, ...]


class ValidationRunner(Protocol):
    def run(self, command: ValidationCommand, *, task_id: str) -> ValidationGateOutcome: ...


def _identifier(prefix: str, *parts: str) -> str:
    digest = sha256("\x00".join(parts).encode()).hexdigest()[:24]
    return f"{prefix}-{digest}"


def validation_environment(source: dict[str, str]) -> dict[str, str]:
    """Copy only process settings needed by local Python, Make, Compose, and Docker."""

    return {
        key: value
        for key, value in source.items()
        if key in _PASSTHROUGH_ENVIRONMENT
        or key.startswith("DOCKER_")
        or key.startswith("COMPOSE_")
    }


def validation_plan(scenario_id: str) -> tuple[ValidationCommand, ...]:
    """Return the complete command allowlist; no model or manifest shell is executed."""

    scenario_assignment = f"SCENARIO={scenario_id}"
    return (
        ValidationCommand(
            ValidationGate.WORKSPACE_INTEGRITY,
            (
                sys.executable,
                "-m",
                "runtime.scenario_harness",
                "verify",
                "--scenario",
                scenario_id,
            ),
            30,
        ),
        ValidationCommand(
            ValidationGate.PUBLIC_BUILD,
            ("make", "--no-print-directory", "scenario-run", scenario_assignment),
            600,
        ),
        ValidationCommand(
            ValidationGate.INDEPENDENT_SQL,
            ("make", "--no-print-directory", "scenario-contract-test", scenario_assignment),
            120,
        ),
        ValidationCommand(
            ValidationGate.POLICY,
            (sys.executable, "-m", "pytest", "-q", "tests/policy", "tests/adversarial"),
            120,
        ),
    )


class ValidationCommandRunner:
    """Run only the exact code-owned validation plan and retain bounded output."""

    def __init__(self, repository_root: Path, scenario_id: str) -> None:
        self.repository = repository_root.resolve(strict=True)
        self.scenario_id = scenario_id
        self._allowed = {command.gate: command for command in validation_plan(scenario_id)}
        state_root = self.repository / ".scenario-state/evidence/validator"
        if state_root.is_symlink():
            raise ValidationBoundaryError("validator evidence root must not be a symlink")
        state_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self._evidence_root = state_root.resolve(strict=True)
        if not self._evidence_root.is_relative_to(self.repository):
            raise ValidationBoundaryError("validator evidence escaped the repository")

    def run(self, command: ValidationCommand, *, task_id: str) -> ValidationGateOutcome:
        if self._allowed.get(command.gate) != command:
            raise ValidationBoundaryError("validator command is not in the exact allowlist")
        started_ns = time.monotonic_ns()
        environment = validation_environment(dict(os.environ))
        infrastructure_error = False
        try:
            with tempfile.TemporaryFile() as output:
                process = subprocess.Popen(
                    command.argv,
                    cwd=self.repository,
                    env=environment,
                    stdin=subprocess.DEVNULL,
                    stdout=output,
                    stderr=subprocess.STDOUT,
                )
                try:
                    exit_code = process.wait(timeout=command.timeout_seconds)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                    exit_code = 124
                    infrastructure_error = True
                output.seek(0)
                contents = output.read(MAX_VALIDATION_OUTPUT_BYTES + 1)
        except OSError as error:
            exit_code = 125
            infrastructure_error = True
            contents = f"validator process error: {type(error).__name__}\n".encode()
        if len(contents) > MAX_VALIDATION_OUTPUT_BYTES:
            contents = contents[:MAX_VALIDATION_OUTPUT_BYTES]
            exit_code = 125
            infrastructure_error = True
        duration_ms = max(0, (time.monotonic_ns() - started_ns) // 1_000_000)
        artifact = self._retain(contents)
        evidence_id = _identifier(
            "validation-evidence",
            task_id,
            command.gate.value,
            str(started_ns),
        )
        evidence = Evidence(
            evidence_id=evidence_id,
            task_id=task_id,
            producer_id="validator",
            kind=EvidenceKind.TEST,
            source=command.gate.value,
            invocation=shlex.join(command.argv),
            exit_code=exit_code,
            artifact=artifact,
            occurred_at=datetime.now(UTC),
        )
        return ValidationGateOutcome(
            evidence=evidence,
            duration_ms=duration_ms,
            infrastructure_error=infrastructure_error,
        )

    def _retain(self, contents: bytes) -> ArtifactReference:
        digest = sha256(contents).hexdigest()
        target = self._evidence_root / f"{digest}.txt"
        if target.is_symlink():
            raise ValidationBoundaryError("validator evidence target must not be a symlink")
        if target.exists():
            if not target.is_file() or target.read_bytes() != contents:
                raise ValidationBoundaryError("validator evidence hash collision")
        else:
            descriptor, temporary_text = tempfile.mkstemp(
                prefix=".validation-", dir=self._evidence_root
            )
            temporary = Path(temporary_text)
            try:
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(contents)
                    stream.flush()
                    os.fsync(stream.fileno())
                    os.fchmod(stream.fileno(), 0o600)
                os.replace(temporary, target)
            finally:
                if temporary.exists():
                    temporary.unlink()
        return ArtifactReference(
            path=target.relative_to(self.repository).as_posix(),
            sha256=digest,
            media_type="text/plain; charset=utf-8",
            size_bytes=len(contents),
        )


def validate_candidate(
    repository_root: Path,
    scenario_id: str,
    state: WorkflowState,
    events: tuple[WorkflowEvent, ...],
    *,
    runner: ValidationRunner | None = None,
    clock: Callable[[], UtcDateTime] | None = None,
) -> ValidationRunResult:
    """Run independent gates and let their exit codes choose the reducer transition."""

    if state.stage is not Stage.IMPLEMENTED:
        raise ValidationBoundaryError("validation requires implemented workflow state")
    manifest = load_manifest(repository_root, scenario_id)
    if state.task_id != f"scenario-{manifest.scenario_id}":
        raise ValidationBoundaryError("validator scenario does not match workflow task")
    now = clock or (lambda: datetime.now(UTC))
    started_at = now()
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id=_identifier("cmd", state.workflow_id, str(state.revision), "validate-start"),
            task_id=state.task_id,
            actor_id="validator",
            target_stage=Stage.VALIDATING,
            occurred_at=started_at,
        ),
        events,
    )
    active_runner = runner or ValidationCommandRunner(repository_root, scenario_id)
    outcomes: list[ValidationGateOutcome] = []
    for command in validation_plan(scenario_id):
        outcome = active_runner.run(command, task_id=state.task_id)
        outcomes.append(outcome)
        if not outcome.evidence.succeeded:
            break
    completed_at = max(now(), *(item.evidence.occurred_at for item in outcomes))
    evidence = tuple(item.evidence for item in outcomes)
    passed = len(outcomes) == len(validation_plan(scenario_id)) and all(
        item.evidence.succeeded for item in outcomes
    )
    infrastructure_error = any(item.infrastructure_error for item in outcomes)
    decision = (
        ValidationDecision.PASS
        if passed
        else ValidationDecision.ERROR
        if infrastructure_error
        else ValidationDecision.FAIL
    )
    artifact = ValidationResult(
        artifact_id=_identifier("validation", state.workflow_id, scenario_id, str(state.revision)),
        task_id=state.task_id,
        producer_id="validator",
        created_at=completed_at,
        decision=decision,
        gates=tuple(item.evidence.source for item in outcomes),
        summary=(
            "All independent validation gates passed."
            if passed
            else f"Validation stopped at failing gate {outcomes[-1].evidence.source}."
        ),
        evidence=evidence,
    )
    target = Stage.VALIDATED if passed else Stage.FAILED if infrastructure_error else Stage.REWORK
    total_duration_ms = sum(item.duration_ms for item in outcomes)
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id=_identifier(
                "cmd", state.workflow_id, str(state.revision), "validate-result"
            ),
            task_id=state.task_id,
            actor_id="validator",
            target_stage=target,
            occurred_at=completed_at,
            artifact=artifact,
            charge=BudgetCharge(
                wall_time_seconds=ceil(total_duration_ms / 1_000),
                rework_attempts=1 if target is Stage.REWORK else 0,
            ),
            reason=None if target is Stage.VALIDATED else artifact.summary,
        ),
        events,
    )
    verify_event_chain(events, expected_state=state)
    return ValidationRunResult(artifact, state, events, tuple(outcomes))
