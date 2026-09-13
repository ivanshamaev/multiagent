"""Regression coverage for propagating failed CLI validation through Make."""

import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_validation_wrapper_retries_only_sigsegv(tmp_path: Path) -> None:
    counter = tmp_path / "attempts"
    flaky_cli = tmp_path / "flaky.sh"
    flaky_cli.write_text(
        f'count="$(cat "{counter}" 2>/dev/null || printf 0)"\n'
        f'printf "%s" "$((count + 1))" > "{counter}"\n'
        'test "$count" -gt 0 && exit 0\n'
        "exit 139\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "bash",
            str(ROOT / "platform/airflow/scripts/retry_on_sigsegv.sh"),
            "bash",
            str(flaky_cli),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert counter.read_text(encoding="utf-8") == "2"


def test_import_validation_preserves_cli_failure(tmp_path: Path) -> None:
    failing_cli = tmp_path / "airflow.sh"
    failing_cli.write_text("printf '[]\\n'\nexit 23\n", encoding="utf-8")

    result = subprocess.run(
        [
            "make",
            "-s",
            "airflow-validate",
            "COMPOSE=true",
            f"AIRFLOW=sh {shlex.quote(str(failing_cli))}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )

    assert result.returncode != 0
    assert "Error 23" in result.stderr
