"""Deterministic checks for the repository planning ledger."""

from __future__ import annotations

import re
import sys
from pathlib import Path

RECORDS = {
    "steps": re.compile(r"STEP-(\d{4})-[a-z0-9-]+\.md"),
    "decisions": re.compile(r"ADR-(\d{4})-[a-z0-9-]+\.md"),
    "problems": re.compile(r"PRB-(\d{4})-[a-z0-9-]+\.md"),
}
STEP_STATUSES = {"complete", "completed", "done", "in progress"}
PROBLEM_STATUSES = {"closed", "resolved"}


def _status(text: str) -> str | None:
    match = re.search(r"(?m)^-?\s*Status:\s*([^;\n]+)", text)
    return match.group(1).strip().lower() if match else None


def collect_issues(root: Path) -> list[str]:
    plan = root / "plan"
    issues: list[str] = []
    active = 0
    for directory, pattern in RECORDS.items():
        seen: set[str] = set()
        index = (
            (plan / directory / "README.md").read_text(encoding="utf-8")
            if directory != "steps"
            else ""
        )
        for path in sorted((plan / directory).glob("*.md")):
            if path.name == "README.md":
                continue
            match = pattern.fullmatch(path.name)
            if not match:
                issues.append(f"invalid {directory} filename: {path.name}")
                continue
            record_id = match.group(1)
            if record_id in seen:
                issues.append(f"duplicate {directory} id: {record_id}")
            seen.add(record_id)
            text = path.read_text(encoding="utf-8")
            status = _status(text)
            if directory == "steps":
                if status not in STEP_STATUSES:
                    issues.append(f"invalid step status: {path.name}")
                active += status == "in progress"
                if status != "in progress" and not list(
                    (plan / "evidence").glob(f"STEP-{record_id}-*.md")
                ):
                    issues.append(f"completed step lacks evidence: {path.name}")
            elif directory == "problems" and status not in PROBLEM_STATUSES:
                issues.append(f"invalid problem status: {path.name}")
            elif directory == "decisions" and status != "accepted":
                issues.append(f"invalid ADR status: {path.name}")
            if directory != "steps" and f"({path.name})" not in index:
                issues.append(f"unindexed {directory} record: {path.name}")
    if active > 1:
        issues.append(f"expected at most one active step, found {active}")
    return issues


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    issues = collect_issues(root)
    if issues:
        print("\n".join(issues))
        return 1
    print("plan governance: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
