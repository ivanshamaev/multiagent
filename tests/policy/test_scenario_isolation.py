import hashlib
import json
from pathlib import Path

from runtime.scenario_harness import build_baseline, load_manifest

ROOT = Path(__file__).resolve().parents[2]


def test_hidden_grader_is_excluded_from_agent_snapshot() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    baseline = build_baseline(ROOT, manifest)

    assert all(not path.startswith(("grader/", "plan/", ".git/")) for path in baseline.files)
    assert ".env" not in baseline.files
    assert "oracle_sha256" not in baseline.contents[".scenario/manifest.json"].decode()


def test_hidden_oracle_hash_is_pinned_by_manifest() -> None:
    manifest = load_manifest(ROOT, "net-revenue")
    oracle = (ROOT / "grader/hidden/grade.py").read_bytes()

    assert hashlib.sha256(oracle).hexdigest() == manifest.hidden_grade.oracle_sha256


def test_public_material_does_not_contain_hidden_sql_or_expected_values() -> None:
    task = (ROOT / "scenarios/net-revenue/task.md").read_text(encoding="utf-8")
    public_manifest = (ROOT / "scenarios/net-revenue/manifest.json").read_text(encoding="utf-8")

    assert "SELECT " not in task
    assert "FROM raw." not in task
    assert "1804905000" not in task + public_manifest
    assert "65402953" not in task + public_manifest


def test_grader_container_has_restricted_capabilities() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    grader_section = compose.split("  scenario-grader:\n", maxsplit=1)[1].split(
        "  airflow-postgres:\n", maxsplit=1
    )[0]

    assert "read_only: true" in grader_section
    assert 'user: "65532:65532"' in grader_section
    assert "cap_drop:\n      - ALL" in grader_section
    assert "no-new-privileges:true" in grader_section
    assert ":/submission:ro" in grader_section
    assert "- grader" in grader_section
    assert "API_TOKEN" not in grader_section
    assert "/var/run/docker.sock" not in grader_section
    assert "internal: true" in compose


def test_grader_build_context_contains_only_oracle() -> None:
    dockerignore = (ROOT / "grader/Dockerfile.dockerignore").read_text(encoding="utf-8")
    dockerfile = (ROOT / "grader/Dockerfile").read_text(encoding="utf-8")

    assert dockerignore.splitlines() == [
        "*",
        "!grader/",
        "!grader/hidden/",
        "!grader/hidden/grade.py",
    ]
    assert "COPY --chown=65532:65532 grader/hidden/grade.py" in dockerfile
    assert "USER 65532:65532" in dockerfile
    assert "pip install" not in dockerfile


def test_manifest_schema_and_interface_are_versioned() -> None:
    schema = json.loads((ROOT / "scenarios/manifest.schema.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (ROOT / "scenarios/net-revenue/manifest.json").read_text(encoding="utf-8")
    )

    assert schema["$schema"].endswith("2020-12/schema")
    assert manifest["schema_version"] == 1
    assert manifest["hidden_grade"]["interface_version"] == 1
    assert manifest["hidden_grade"]["command"] == ("make scenario-grade SCENARIO=net-revenue")
