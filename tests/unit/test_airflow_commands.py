"""Regression coverage for propagating failed CLI validation through Make."""

import shlex
import subprocess
from pathlib import Path


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
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )

    assert result.returncode != 0
    assert "Error 23" in result.stderr
