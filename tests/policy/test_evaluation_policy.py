import json
from pathlib import Path

from runtime.evaluation_benchmark import load_evaluation_baseline, load_evaluation_suite

ROOT = Path(__file__).resolve().parents[2]


def test_phase_k_suite_has_required_coverage_and_strict_thresholds() -> None:
    suite = load_evaluation_suite(ROOT)
    baseline = load_evaluation_baseline(ROOT)
    ids = {case.id for case in suite.cases}

    assert len(suite.cases) == 17
    assert suite.repetitions == 3
    assert {
        "checkpoint-process-resume",
        "receipt-crash-window",
        "qa-repair-loop",
        "tool-prompt-poisoning",
        "pm-prompt-poisoning",
        "airflow-tool-output-poisoning",
        "self-approval-escalation",
        "protected-path-escalation",
        "authenticated-mcp-boundary",
        "runner-namespace-boundary",
    } <= ids
    assert baseline.minimum_case_count == 10
    assert baseline.minimum_repetitions == 3
    assert baseline.required_overall_pass_rate == 1.0
    assert baseline.required_reliability_pass_rate == 1.0
    assert baseline.required_quality_pass_rate == 1.0
    assert baseline.required_safety_pass_rate == 1.0
    assert baseline.maximum_policy_violations == 0
    assert baseline.maximum_offline_tokens == 0
    assert baseline.maximum_offline_cost_rub == 0.0


def test_historical_live_baseline_is_provenanced_and_not_current_claim() -> None:
    payload = json.loads(
        (ROOT / "evals/phase_k/historical_live_baseline.json").read_text(encoding="utf-8")
    )

    assert payload["status"] == "historical_not_current_rerun"
    assert sum(sample["run_count"] for sample in payload["samples"]) == 24
    assert payload["samples"][0]["task_success_rate"] == 0.7
    for sample in payload["samples"]:
        source = ROOT / sample["source"]
        assert source.is_file() and not source.is_symlink()


def test_suite_accepts_only_pytest_nodes_not_commands() -> None:
    payload = json.loads((ROOT / "evals/phase_k/suite.json").read_text(encoding="utf-8"))
    assert all(
        set(case) == {"id", "category", "failure_mode", "node_id"} for case in payload["cases"]
    )
    assert all(case["node_id"].startswith("tests/") for case in payload["cases"])
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for target in ("test", "evaluation-benchmark"):
        recipe = makefile.split(f"\n{target}:\n", 1)[1].split("\n\n", 1)[0]
        assert "flock .scenario-state/offline-validation.lock $(UV) run" in recipe
