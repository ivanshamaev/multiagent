import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_required_governance_documents_exist() -> None:
    required_paths = (
        "AGENTS.md",
        "Claude.md",
        "plan/README.md",
        "plan/development-plan.md",
        "plan/progress.md",
    )

    assert all((ROOT / path).is_file() for path in required_paths)


def test_python_version_is_pinned_to_312() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert project["project"]["requires-python"] == ">=3.12,<3.13"
    assert (ROOT / ".python-version").read_text(encoding="utf-8").strip() == "3.12"


def test_compose_uses_pinned_image_and_loopback_ports() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert ":latest" not in compose
    assert "clickhouse/clickhouse-server:25.8.33.6" in compose
    assert "agentic-data-platform-dbt:1.11.14-1.10.2" in compose
    assert '"127.0.0.1:${CLICKHOUSE_HTTP_PORT:-8123}:8123"' in compose
    assert '"127.0.0.1:${CLICKHOUSE_NATIVE_PORT:-9000}:9000"' in compose


def test_data_platform_does_not_receive_llm_token() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    dockerignore = (ROOT / "platform/dbt/.dockerignore").read_text(encoding="utf-8")

    assert "API_TOKEN" not in compose
    assert dockerignore.splitlines() == ["*", "!Dockerfile", "!requirements.lock"]


def test_dbt_dependencies_and_project_are_pinned() -> None:
    dockerfile = (ROOT / "platform/dbt/Dockerfile").read_text(encoding="utf-8")
    requirements = (ROOT / "platform/dbt/requirements.lock").read_text(encoding="utf-8")
    project = (ROOT / "platform/dbt/dbt_project.yml").read_text(encoding="utf-8")

    assert dockerfile.startswith(
        "FROM python:3.12.14-slim-bookworm@sha256:"
        "782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254\n"
    )
    assert "dbt-core==1.11.14" in requirements
    assert "dbt-clickhouse==1.10.2" in requirements
    assert "--hash=sha256:" in requirements
    assert "name: agentic_data_platform" in project


def test_dbt_baseline_does_not_solve_net_revenue_scenario() -> None:
    model_root = ROOT / "platform/dbt/models"
    model_text = "\n".join(
        path.read_text(encoding="utf-8") for path in model_root.rglob("*.sql")
    ).lower()

    assert "net_revenue" not in model_text
    assert not (model_root / "intermediate/int_order_revenue.sql").exists()
    assert not (model_root / "marts/fct_net_revenue.sql").exists()


def test_real_environment_file_is_ignored() -> None:
    ignored_patterns = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert ".env" in ignored_patterns
