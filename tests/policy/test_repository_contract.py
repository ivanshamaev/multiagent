import ast
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
    airflow_image = (ROOT / "platform/airflow/Dockerfile").read_text(encoding="utf-8")

    assert ":latest" not in compose
    assert "clickhouse/clickhouse-server:25.8.33.6" in compose
    assert "agentic-data-platform-dbt:1.11.14-1.10.2" in compose
    assert (
        "apache/airflow:3.3.1-python3.12@sha256:"
        "b01a795dfbd113bbbfdf3ee169b8f27e9a0090ccef105f1a452b3594a11ed316" in airflow_image
    )
    assert (
        "postgres:16.15-bookworm@sha256:"
        "bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825" in compose
    )
    assert '"127.0.0.1:${CLICKHOUSE_HTTP_PORT:-8123}:8123"' in compose
    assert '"127.0.0.1:${CLICKHOUSE_NATIVE_PORT:-9000}:9000"' in compose
    assert '"127.0.0.1:${AIRFLOW_API_PORT:-8080}:8080"' in compose


def test_data_platform_does_not_receive_llm_token() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    dockerignore = (ROOT / "platform/dbt/.dockerignore").read_text(encoding="utf-8")

    assert "API_TOKEN" not in compose
    assert "env_file:" not in compose
    assert "/var/run/docker.sock" not in compose
    assert "_PIP_ADDITIONAL_REQUIREMENTS" not in compose
    assert dockerignore.splitlines() == ["*", "!Dockerfile", "!requirements.lock"]
    airflow_ignore = (ROOT / "platform/airflow/Dockerfile.dockerignore").read_text(encoding="utf-8")
    assert airflow_ignore.splitlines() == [
        "*",
        "!platform/",
        "!platform/airflow/",
        "!platform/airflow/Dockerfile",
        "!platform/airflow/requirements.lock",
        "!platform/dbt/",
        "!platform/dbt/requirements.lock",
    ]
    assert "./platform/dbt:/opt/airflow/dbt:ro" in compose
    assert "./platform/airflow/fixtures:/opt/airflow/fixtures:ro" in compose
    assert "./platform/clickhouse/tests:/opt/airflow/checks:ro" in compose


def test_airflow_has_minimal_localexecutor_topology() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    for service in (
        "airflow-postgres:",
        "airflow-init:",
        "airflow-api-server:",
        "airflow-scheduler:",
        "airflow-dag-processor:",
    ):
        assert service in compose

    assert "AIRFLOW__CORE__EXECUTOR: LocalExecutor" in compose
    assert 'AIRFLOW__CORE__PARALLELISM: "2"' in compose
    assert "http://airflow-api-server:8080/execution/" in compose
    assert "airflow-worker:" not in compose
    assert "redis:" not in compose
    assert "airflow-triggerer:" not in compose


def test_airflow_dags_use_only_the_public_sdk() -> None:
    # Runtime API tests own the exact graph assertion, independent of factory layout.
    imports = [
        node
        for path in (ROOT / "platform/airflow/dags").glob("*.py")
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("airflow")
    ]
    assert imports
    assert all(node.module == "airflow.sdk" for node in imports)


def test_airflow_keeps_dbt_dependencies_isolated() -> None:
    dockerfile = (ROOT / "platform/airflow/Dockerfile").read_text(encoding="utf-8")
    airflow_lock = (ROOT / "platform/airflow/requirements.lock").read_text(encoding="utf-8")

    assert "python -m venv /opt/airflow/dbt-venv" in dockerfile
    assert "--system-site-packages" not in dockerfile
    assert "--require-hashes" in dockerfile
    assert "COPY platform/dbt/requirements.lock" in dockerfile
    assert "--no-deps --require-hashes" in dockerfile
    assert "astronomer-cosmos==1.15.0" in airflow_lock
    assert "--hash=sha256:" in airflow_lock


def test_airflow_entrypoints_are_eligible_for_safe_discovery() -> None:
    for name in ("ecommerce_hourly.py", "ecommerce_acceptance.py", "ecommerce_failure_probe.py"):
        source = (ROOT / "platform/airflow/dags" / name).read_bytes().lower()
        assert b"airflow" in source and b"dag" in source


def test_airflow_uses_cosmos_instead_of_a_custom_dbt_runner() -> None:
    source = (ROOT / "platform/airflow/dags/cosmos_pipeline.py").read_text(encoding="utf-8")

    assert "DbtTaskGroup" in source
    assert "ExecutionMode.LOCAL" in source
    assert "InvocationMode.SUBPROCESS" in source
    assert "TestBehavior.AFTER_ALL" in source
    assert "subprocess" not in source
    assert not (ROOT / "platform/airflow/dags/dbt_pipeline.py").exists()


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
    assert ".user.yml" in ignored_patterns
    assert not (ROOT / "platform/dbt/.user.yml").exists()
