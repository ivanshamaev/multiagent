from datetime import UTC, datetime
from pathlib import Path

import pytest

from runtime.evaluation_benchmark import (
    CaseRun,
    EvaluationCategory,
    EvaluationError,
    EvaluationMetrics,
    EvaluationReport,
    RunOutcome,
    build_metrics,
    compare_baseline,
    configuration_fingerprint,
    load_evaluation_baseline,
    load_evaluation_suite,
    write_report,
)

ROOT = Path(__file__).resolve().parents[2]


def _run(case, repetition: int, outcome: RunOutcome = RunOutcome.PASS) -> CaseRun:
    return CaseRun(
        case_id=case.id,
        category=case.category,
        failure_mode=case.failure_mode,
        repetition=repetition,
        outcome=outcome,
        exit_code=0 if outcome is RunOutcome.PASS else 1,
        duration_ms=100 + repetition,
        output_bytes=10,
        output_sha256="a" * 64,
    )


def test_committed_suite_fingerprint_is_stable_and_covers_selected_tests() -> None:
    suite = load_evaluation_suite(ROOT)
    baseline = load_evaluation_baseline(ROOT)

    first = configuration_fingerprint(ROOT, suite, baseline)
    second = configuration_fingerprint(ROOT, suite, baseline)

    assert first == second
    assert len(first) == 64
    assert len(suite.cases) == 17


def test_metrics_and_strict_baseline_detect_one_safety_regression() -> None:
    suite = load_evaluation_suite(ROOT)
    baseline = load_evaluation_baseline(ROOT)
    runs = tuple(
        _run(case, repetition)
        for repetition in range(1, suite.repetitions + 1)
        for case in suite.cases
    )
    passing = build_metrics(suite, runs)

    assert passing.overall_pass_rate == 1.0
    assert passing.policy_violations == 0
    assert compare_baseline(suite, baseline, passing) == ()

    first_safety = next(
        i for i, run in enumerate(runs) if run.category is EvaluationCategory.SAFETY
    )
    failed_runs = (
        *runs[:first_safety],
        _run(suite.cases[10], 1, RunOutcome.ASSERTION_FAILURE),
        *runs[first_safety + 1 :],
    )
    failed = build_metrics(suite, failed_runs)
    regressions = compare_baseline(suite, baseline, failed)

    assert failed.policy_violations == 1
    assert regressions == ("overall_pass_rate", "safety_pass_rate", "policy_violations")


def test_report_store_is_owner_only_and_atomic(tmp_path: Path) -> None:
    metrics = EvaluationMetrics(
        case_count=10,
        run_count=30,
        passed_runs=30,
        overall_pass_rate=1.0,
        reliability_pass_rate=1.0,
        quality_pass_rate=1.0,
        safety_pass_rate=1.0,
        latency_p50_ms=100,
        latency_p95_ms=200,
        policy_violations=0,
        assertion_failures=0,
        timeouts=0,
        harness_errors=0,
    )
    report = EvaluationReport(
        suite_id="phase-k-regression-v1",
        protocol_version="offline-pytest-v1",
        generated_at=datetime.now(UTC),
        configuration_fingerprint="b" * 64,
        repetitions=3,
        metrics=metrics,
        runs=(),
        verdict="pass",
        regressions=(),
    )

    target = write_report(report, "phase-k-test.json", tmp_path)

    assert target.stat().st_mode & 0o777 == 0o600
    assert target.parent.stat().st_mode & 0o777 == 0o700
    assert EvaluationReport.model_validate_json(target.read_bytes(), strict=True) == report


def test_metrics_reject_incomplete_sample() -> None:
    suite = load_evaluation_suite(ROOT)
    with pytest.raises(EvaluationError, match="incomplete"):
        build_metrics(suite, (_run(suite.cases[0], 1),))
