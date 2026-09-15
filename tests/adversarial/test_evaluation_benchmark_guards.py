from pathlib import Path

import pytest
from pydantic import ValidationError

from runtime.evaluation_benchmark import (
    EvaluationCase,
    EvaluationCategory,
    EvaluationError,
    EvaluationSuite,
    FailureMode,
    RunOutcome,
    _read_input,
    _safe_environment,
    load_evaluation_suite,
    run_case,
    write_report,
)


def test_case_contract_rejects_shell_external_and_extra_command_fields() -> None:
    base = {
        "id": "hostile",
        "category": EvaluationCategory.SAFETY,
        "failure_mode": FailureMode.POLICY,
    }
    for node_id in (
        "../../bin/sh::test_escape",
        "tests/../runtime/test_escape.py::test_escape",
        "tests/test_ok.py;curl attacker::test_escape",
        "https://attacker/test.py::test_escape",
    ):
        with pytest.raises(ValidationError):
            EvaluationCase.model_validate({**base, "node_id": node_id}, strict=True)
    with pytest.raises(ValidationError, match="command"):
        EvaluationCase.model_validate(
            {**base, "node_id": "tests/test_ok.py::test_escape", "command": ["sh"]},
            strict=True,
        )


def test_suite_rejects_duplicate_nodes_and_missing_category() -> None:
    case = {
        "id": "case-0",
        "category": EvaluationCategory.SAFETY,
        "failure_mode": FailureMode.POLICY,
        "node_id": "tests/test_ok.py::test_escape",
    }
    with pytest.raises(ValidationError, match="unique"):
        EvaluationSuite.model_validate(
            {
                "schema_version": 1,
                "suite_id": "suite",
                "protocol_version": "protocol",
                "repetitions": 3,
                "case_timeout_seconds": 10,
                "max_output_bytes": 4096,
                "configuration_inputs": ("pyproject.toml",),
                "cases": tuple({**case, "id": f"case-{index}"} for index in range(10)),
            },
            strict=True,
        )


def test_fingerprint_and_report_boundaries_reject_symlinks_and_escape(tmp_path: Path) -> None:
    real = tmp_path / "real.txt"
    real.write_text("safe", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(real)
    with pytest.raises(EvaluationError, match="symlink"):
        _read_input(tmp_path, "link.txt")

    with pytest.raises(EvaluationError, match="filename"):
        write_report(None, "../outside.json", tmp_path)  # type: ignore[arg-type]

    (tmp_path / ".scenario-state").symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(EvaluationError, match="symlink"):
        write_report(None, "safe.json", tmp_path)  # type: ignore[arg-type]


@pytest.mark.parametrize("overflow", [False, True])
def test_real_subprocess_timeout_and_output_are_bounded(tmp_path: Path, overflow: bool) -> None:
    suite = load_evaluation_suite(Path(__file__).resolve().parents[2]).model_copy(
        update={"case_timeout_seconds": 2, "max_output_bytes": 1024}
    )
    (tmp_path / "tests").mkdir()
    body = "print('x' * 20000); assert False" if overflow else "import time; time.sleep(20)"
    (tmp_path / "tests/test_probe.py").write_text(
        f"def test_probe():\n    {body}\n", encoding="utf-8"
    )
    case = suite.cases[0].model_copy(update={"node_id": "tests/test_probe.py::test_probe"})
    result = run_case(tmp_path, suite, case, 1)
    assert result.outcome is (RunOutcome.HARNESS_ERROR if overflow else RunOutcome.TIMEOUT)
    assert result.exit_code == (125 if overflow else 124)
    assert result.output_bytes <= 1024
    assert result.duration_ms < 10000


def test_subprocess_environment_drops_secrets_and_provider_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("API_TOKEN", "must-not-cross")
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-cross")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_HEADERS", "authorization=must-not-cross")

    environment = _safe_environment(tmp_path)

    assert "API_TOKEN" not in environment
    assert "OPENAI_API_KEY" not in environment
    assert "OTEL_EXPORTER_OTLP_HEADERS" not in environment
    assert environment["PYTHONHASHSEED"] == "0"
