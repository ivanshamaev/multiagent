"""Versioned, repeated and content-free Phase K offline evaluation benchmark."""

from __future__ import annotations

import argparse
import json
import os
import selectors
import signal
import stat
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from math import ceil
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field, StrictFloat, StrictInt, StringConstraints, TypeAdapter, model_validator

from contracts.common import (
    FrozenModel,
    Identifier,
    RelativePath,
    Sha256,
    UtcDateTime,
    relative_path,
)

ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "evals/phase_k/suite.json"
BASELINE_PATH = ROOT / "evals/phase_k/baseline.json"
REPORT_ROOT = ROOT / ".scenario-state/evaluations"
MAX_MANIFEST_BYTES = 1_000_000
MAX_FINGERPRINT_INPUT_BYTES = 10_000_000

PytestNodeId = Annotated[
    str,
    StringConstraints(
        min_length=16,
        max_length=512,
        pattern=r"^tests/[A-Za-z0-9_./-]+\.py::test_[A-Za-z0-9_]+$",
    ),
]
ReportFilename = Annotated[
    str,
    StringConstraints(pattern=r"^[a-z][a-z0-9-]{0,62}\.json$"),
]


class EvaluationError(RuntimeError):
    """Evaluation configuration, execution or report boundary failed closed."""


class EvaluationCategory(StrEnum):
    RELIABILITY = "reliability"
    QUALITY = "quality"
    SAFETY = "safety"


class FailureMode(StrEnum):
    WORKFLOW = "workflow"
    BUDGET = "budget"
    INFRASTRUCTURE = "infrastructure"
    REASONING = "reasoning"
    POLICY = "policy"


class RunOutcome(StrEnum):
    PASS = "pass"
    ASSERTION_FAILURE = "assertion_failure"
    TIMEOUT = "timeout"
    HARNESS_ERROR = "harness_error"


class EvaluationCase(FrozenModel):
    id: Identifier
    category: EvaluationCategory
    failure_mode: FailureMode
    node_id: PytestNodeId

    @model_validator(mode="after")
    def validate_node_path(self) -> Self:
        relative_path(self.node_id.split("::", maxsplit=1)[0])
        return self


class EvaluationSuite(FrozenModel):
    schema_version: Literal[1] = 1
    suite_id: Identifier
    protocol_version: Identifier
    repetitions: StrictInt = Field(ge=3, le=20)
    case_timeout_seconds: StrictInt = Field(ge=1, le=120)
    max_output_bytes: StrictInt = Field(ge=1_024, le=1_000_000)
    configuration_inputs: tuple[RelativePath, ...] = Field(min_length=1, max_length=128)
    cases: tuple[EvaluationCase, ...] = Field(min_length=10, max_length=64)

    @model_validator(mode="after")
    def validate_coverage(self) -> Self:
        if len({case.id for case in self.cases}) != len(self.cases):
            raise ValueError("evaluation case IDs must be unique")
        if len({case.node_id for case in self.cases}) != len(self.cases):
            raise ValueError("evaluation pytest nodes must be unique")
        if set(case.category for case in self.cases) != set(EvaluationCategory):
            raise ValueError("evaluation suite must cover reliability, quality and safety")
        if len(set(self.configuration_inputs)) != len(self.configuration_inputs):
            raise ValueError("configuration inputs must be unique")
        return self


class EvaluationBaseline(FrozenModel):
    schema_version: Literal[1] = 1
    suite_id: Identifier
    minimum_case_count: StrictInt = Field(ge=10)
    minimum_repetitions: StrictInt = Field(ge=3)
    required_overall_pass_rate: StrictFloat = Field(ge=1.0, le=1.0)
    required_reliability_pass_rate: StrictFloat = Field(ge=1.0, le=1.0)
    required_quality_pass_rate: StrictFloat = Field(ge=1.0, le=1.0)
    required_safety_pass_rate: StrictFloat = Field(ge=1.0, le=1.0)
    maximum_policy_violations: StrictInt = Field(ge=0, le=0)
    maximum_offline_tokens: StrictInt = Field(ge=0, le=0)
    maximum_offline_cost_rub: StrictFloat = Field(ge=0.0, le=0.0)


class CaseRun(FrozenModel):
    case_id: Identifier
    category: EvaluationCategory
    failure_mode: FailureMode
    repetition: StrictInt = Field(ge=1, le=20)
    outcome: RunOutcome
    exit_code: StrictInt
    duration_ms: StrictInt = Field(ge=0)
    output_bytes: StrictInt = Field(ge=0)
    output_sha256: Sha256


class EvaluationMetrics(FrozenModel):
    case_count: StrictInt = Field(ge=0)
    run_count: StrictInt = Field(ge=0)
    passed_runs: StrictInt = Field(ge=0)
    overall_pass_rate: StrictFloat = Field(ge=0.0, le=1.0)
    reliability_pass_rate: StrictFloat = Field(ge=0.0, le=1.0)
    quality_pass_rate: StrictFloat = Field(ge=0.0, le=1.0)
    safety_pass_rate: StrictFloat = Field(ge=0.0, le=1.0)
    latency_p50_ms: StrictInt = Field(ge=0)
    latency_p95_ms: StrictInt = Field(ge=0)
    policy_violations: StrictInt = Field(ge=0)
    offline_tokens: Literal[0] = 0
    offline_cost_rub: Literal[0.0] = 0.0
    assertion_failures: StrictInt = Field(ge=0)
    timeouts: StrictInt = Field(ge=0)
    harness_errors: StrictInt = Field(ge=0)


class EvaluationReport(FrozenModel):
    schema_version: Literal[1] = 1
    suite_id: Identifier
    protocol_version: Identifier
    generated_at: UtcDateTime
    configuration_fingerprint: Sha256
    repetitions: StrictInt = Field(ge=3, le=20)
    metrics: EvaluationMetrics
    runs: tuple[CaseRun, ...]
    verdict: Literal["pass", "regression"]
    regressions: tuple[str, ...]


def _load_json(path: Path, model_type):
    if path.is_symlink() or not path.is_file():
        raise EvaluationError("evaluation config must be a regular non-symlink file")
    if path.stat().st_size > MAX_MANIFEST_BYTES:
        raise EvaluationError("evaluation config exceeds the size limit")
    try:
        return model_type.model_validate_json(path.read_bytes(), strict=True)
    except (TypeError, ValueError) as error:
        raise EvaluationError("evaluation config failed closed validation") from error


def load_evaluation_suite(root: Path = ROOT) -> EvaluationSuite:
    suite = _load_json(root / "evals/phase_k/suite.json", EvaluationSuite)
    for case in suite.cases:
        _read_input(root, case.node_id.split("::", maxsplit=1)[0])
    return suite


def load_evaluation_baseline(root: Path = ROOT) -> EvaluationBaseline:
    return _load_json(root / "evals/phase_k/baseline.json", EvaluationBaseline)


def _read_input(root: Path, relative: str) -> bytes:
    if root.is_symlink():
        raise EvaluationError("repository root must not be a symlink")
    resolved_root = root.resolve(strict=True)
    candidate = resolved_root / relative
    current = resolved_root
    for part in Path(relative).parts:
        current /= part
        if current.is_symlink():
            raise EvaluationError("fingerprint input must not contain symlinks")
    try:
        resolved = candidate.resolve(strict=True)
        metadata = resolved.stat()
    except OSError as error:
        raise EvaluationError("fingerprint input is missing") from error
    if not resolved.is_relative_to(resolved_root) or not stat.S_ISREG(metadata.st_mode):
        raise EvaluationError("fingerprint input escaped the repository")
    if metadata.st_size > MAX_FINGERPRINT_INPUT_BYTES:
        raise EvaluationError("fingerprint input exceeds the size limit")
    payload = resolved.read_bytes()
    if len(payload) != metadata.st_size:
        raise EvaluationError("fingerprint input changed while reading")
    return payload


def configuration_fingerprint(
    root: Path, suite: EvaluationSuite, baseline: EvaluationBaseline
) -> str:
    paths = set(suite.configuration_inputs)
    for directory in (
        "agents",
        "contracts",
        "orchestrator",
        "policies",
        "runtime",
        "scenarios",
        "tests",
    ):
        for path in (root / directory).rglob("*"):
            if "__pycache__" not in path.parts and path.suffix in {".py", ".json", ".md", ".sql"}:
                paths.add(path.relative_to(root).as_posix())
    paths.update(case.node_id.split("::", maxsplit=1)[0] for case in suite.cases)
    inputs = {path: sha256(_read_input(root, path)).hexdigest() for path in sorted(paths)}
    payload = {
        "baseline": baseline.model_dump(mode="json"),
        "inputs": inputs,
        "suite": suite.model_dump(mode="json"),
    }
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return sha256(canonical).hexdigest()


def _safe_environment(root: Path) -> dict[str, str]:
    return {
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": str(root.resolve(strict=True)),
    }


def run_case(root: Path, suite: EvaluationSuite, case: EvaluationCase, repetition: int) -> CaseRun:
    started = time.monotonic_ns()
    process = subprocess.Popen(
        [sys.executable, "-m", "pytest", "-q", case.node_id],
        cwd=root,
        env=_safe_environment(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    timed_out = False
    overflow = False
    chunks: list[bytes] = []
    retained_bytes = 0
    deadline = time.monotonic() + suite.case_timeout_seconds
    assert process.stdout is not None
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    break
                for key, _ in selector.select(min(remaining, 0.1)):
                    chunk = os.read(key.fileobj.fileno(), 8192)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    capacity = suite.max_output_bytes - retained_bytes
                    chunks.append(chunk[:capacity])
                    retained_bytes += min(len(chunk), capacity)
                    if len(chunk) > capacity:
                        overflow = True
                        break
                if overflow:
                    break
        if timed_out or overflow:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.wait(timeout=max(0.1, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
    finally:
        process.stdout.close()
    duration_ms = (time.monotonic_ns() - started) // 1_000_000
    output = b"".join(chunks)
    if timed_out:
        outcome, exit_code = RunOutcome.TIMEOUT, 124
    elif overflow:
        outcome, exit_code = RunOutcome.HARNESS_ERROR, 125
    elif process.returncode == 0:
        outcome, exit_code = RunOutcome.PASS, 0
    elif process.returncode == 1:
        outcome, exit_code = RunOutcome.ASSERTION_FAILURE, 1
    else:
        outcome, exit_code = RunOutcome.HARNESS_ERROR, process.returncode
    return CaseRun(
        case_id=case.id,
        category=case.category,
        failure_mode=case.failure_mode,
        repetition=repetition,
        outcome=outcome,
        exit_code=exit_code,
        duration_ms=duration_ms,
        output_bytes=len(output),
        output_sha256=sha256(output).hexdigest(),
    )


def _pass_rate(runs: tuple[CaseRun, ...], category: EvaluationCategory | None = None) -> float:
    selected = runs if category is None else tuple(run for run in runs if run.category is category)
    return sum(run.outcome is RunOutcome.PASS for run in selected) / len(selected)


def build_metrics(suite: EvaluationSuite, runs: tuple[CaseRun, ...]) -> EvaluationMetrics:
    expected = {
        (case.id, repetition)
        for case in suite.cases
        for repetition in range(1, suite.repetitions + 1)
    }
    if len(runs) != len(expected) or {(run.case_id, run.repetition) for run in runs} != expected:
        raise EvaluationError("evaluation sample is incomplete or duplicated")
    durations = sorted(run.duration_ms for run in runs)
    passed = sum(run.outcome is RunOutcome.PASS for run in runs)
    return EvaluationMetrics(
        case_count=len(suite.cases),
        run_count=len(runs),
        passed_runs=passed,
        overall_pass_rate=_pass_rate(runs),
        reliability_pass_rate=_pass_rate(runs, EvaluationCategory.RELIABILITY),
        quality_pass_rate=_pass_rate(runs, EvaluationCategory.QUALITY),
        safety_pass_rate=_pass_rate(runs, EvaluationCategory.SAFETY),
        latency_p50_ms=durations[(len(durations) - 1) // 2],
        latency_p95_ms=durations[ceil(0.95 * len(durations)) - 1],
        policy_violations=sum(
            run.category is EvaluationCategory.SAFETY and run.outcome is not RunOutcome.PASS
            for run in runs
        ),
        assertion_failures=sum(run.outcome is RunOutcome.ASSERTION_FAILURE for run in runs),
        timeouts=sum(run.outcome is RunOutcome.TIMEOUT for run in runs),
        harness_errors=sum(run.outcome is RunOutcome.HARNESS_ERROR for run in runs),
    )


def compare_baseline(
    suite: EvaluationSuite, baseline: EvaluationBaseline, metrics: EvaluationMetrics
) -> tuple[str, ...]:
    checks = {
        "case_count": metrics.case_count >= baseline.minimum_case_count,
        "repetitions": suite.repetitions >= baseline.minimum_repetitions,
        "overall_pass_rate": metrics.overall_pass_rate >= baseline.required_overall_pass_rate,
        "reliability_pass_rate": (
            metrics.reliability_pass_rate >= baseline.required_reliability_pass_rate
        ),
        "quality_pass_rate": metrics.quality_pass_rate >= baseline.required_quality_pass_rate,
        "safety_pass_rate": metrics.safety_pass_rate >= baseline.required_safety_pass_rate,
        "policy_violations": metrics.policy_violations <= baseline.maximum_policy_violations,
        "offline_tokens": metrics.offline_tokens <= baseline.maximum_offline_tokens,
        "offline_cost_rub": metrics.offline_cost_rub <= baseline.maximum_offline_cost_rub,
    }
    return tuple(name for name, passed in checks.items() if not passed)


def write_report(report: EvaluationReport, filename: str, root: Path = ROOT) -> Path:
    try:
        filename = TypeAdapter(ReportFilename).validate_python(filename, strict=True)
    except ValueError:
        raise EvaluationError("report filename is invalid") from None
    if root.is_symlink():
        raise EvaluationError("report root must not be a symlink")
    directory = root.resolve(strict=True)
    for component in (".scenario-state", "evaluations"):
        directory /= component
        if directory.is_symlink():
            raise EvaluationError("report directory must not contain symlinks")
        directory.mkdir(exist_ok=True, mode=0o700)
    if stat.S_IMODE(directory.stat().st_mode) != 0o700:
        raise EvaluationError("report directory must have mode 0700")
    target = directory / filename
    if target.is_symlink():
        raise EvaluationError("report target must not be a symlink")
    descriptor, temporary_name = tempfile.mkstemp(prefix=".evaluation-", dir=directory)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(report.model_dump_json(indent=2).encode())
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o600)
        os.replace(temporary, target)
        target.chmod(0o600)
    finally:
        if temporary.exists():
            temporary.unlink()
    return target


def execute_benchmark(
    root: Path = ROOT, report_filename: str = "phase-k-latest.json"
) -> EvaluationReport:
    suite = load_evaluation_suite(root)
    baseline = load_evaluation_baseline(root)
    if suite.suite_id != baseline.suite_id:
        raise EvaluationError("suite and baseline IDs do not match")
    fingerprint = configuration_fingerprint(root, suite, baseline)
    runs = tuple(
        run_case(root, suite, case, repetition)
        for repetition in range(1, suite.repetitions + 1)
        for case in suite.cases
    )
    metrics = build_metrics(suite, runs)
    if (
        configuration_fingerprint(root, load_evaluation_suite(root), load_evaluation_baseline(root))
        != fingerprint
    ):
        raise EvaluationError("configuration changed during benchmark")
    regressions = compare_baseline(suite, baseline, metrics)
    report = EvaluationReport(
        suite_id=suite.suite_id,
        protocol_version=suite.protocol_version,
        generated_at=datetime.now(UTC),
        configuration_fingerprint=fingerprint,
        repetitions=suite.repetitions,
        metrics=metrics,
        runs=runs,
        verdict="regression" if regressions else "pass",
        regressions=regressions,
    )
    write_report(report, report_filename, root)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-name", default="phase-k-latest.json")
    args = parser.parse_args()
    try:
        report = execute_benchmark(ROOT, args.report_name)
    except EvaluationError as error:
        print(json.dumps({"error": type(error).__name__, "status": "failed"}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "configuration_fingerprint": report.configuration_fingerprint,
                "metrics": report.metrics.model_dump(mode="json"),
                "report": f".scenario-state/evaluations/{args.report_name}",
                "status": report.verdict,
            },
            sort_keys=True,
        )
    )
    return 0 if report.verdict == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
