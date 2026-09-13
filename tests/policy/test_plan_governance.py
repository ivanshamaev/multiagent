from pathlib import Path

from policies.plan_governance import collect_issues

ROOT = Path(__file__).resolve().parents[2]


def test_repository_plan_ledger_is_consistent() -> None:
    assert collect_issues(ROOT) == []


def test_plan_lint_rejects_bad_name_and_missing_index(tmp_path: Path) -> None:
    for directory in ("steps", "decisions", "problems", "evidence"):
        (tmp_path / "plan" / directory).mkdir(parents=True)
    (tmp_path / "plan/decisions/README.md").write_text("# index\n", encoding="utf-8")
    (tmp_path / "plan/problems/README.md").write_text("# index\n", encoding="utf-8")
    (tmp_path / "plan/steps/STEP-0001-good.md").write_text(
        "# step\n\nStatus: in progress\n", encoding="utf-8"
    )
    (tmp_path / "plan/problems/PROBLEM-0001-bad.md").write_text(
        "# bad\n\nStatus: open\n", encoding="utf-8"
    )

    assert collect_issues(tmp_path) == ["invalid problems filename: PROBLEM-0001-bad.md"]


def test_plan_lint_rejects_multiple_active_steps(tmp_path: Path) -> None:
    for directory in ("steps", "decisions", "problems", "evidence"):
        (tmp_path / "plan" / directory).mkdir(parents=True)
    (tmp_path / "plan/decisions/README.md").write_text("# index\n", encoding="utf-8")
    (tmp_path / "plan/problems/README.md").write_text("# index\n", encoding="utf-8")
    for number in (1, 2):
        (tmp_path / f"plan/steps/STEP-{number:04d}-active.md").write_text(
            "# step\n\nStatus: in progress\n", encoding="utf-8"
        )

    assert collect_issues(tmp_path) == ["expected at most one active step, found 2"]
