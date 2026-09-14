import shutil
from pathlib import Path

from runtime.runner_isolation import IsolatedRunner, load_runner_profile

ROOT = Path(__file__).resolve().parents[2]
PROBE = r"""
import json, os, socket, sys
from pathlib import Path
request = json.load(sys.stdin)
def attempt(action):
    try:
        action()
        return True
    except Exception:
        return False
payload = {
    "uid": os.getuid(),
    "runner_id": os.environ.get("RUNNER_ID"),
    "environment": sorted(os.environ),
    "workspace_exists": Path("/workspace").exists(),
    "task_read": attempt(lambda: Path("/workspace/TASK.md").read_text()),
    "env_visible": Path("/workspace/.env").exists() or Path("/.env").exists(),
    "docker_socket_visible": Path("/var/run/docker.sock").exists(),
    "repository_visible": Path("/repo").exists(),
    "network_connect": attempt(lambda: socket.create_connection(("1.1.1.1", 53), timeout=0.2)),
    "task_write": attempt(lambda: Path("/workspace/TASK.md").write_text("changed")),
    "model_write": attempt(
        lambda: Path("/workspace/platform/dbt/models/new.sql").write_text("select 1")
    ),
    "test_write": attempt(
        lambda: Path("/workspace/platform/dbt/tests/new.sql").write_text("select 1")
    ),
}
json.dump(payload, sys.stdout, separators=(",", ":"), sort_keys=True)
"""


def _repository(tmp_path: Path) -> tuple[Path, Path]:
    repository = tmp_path / "repository"
    shutil.copytree(ROOT / "policies", repository / "policies")
    workspace = repository / ".scenario-state/workspaces/task-1"
    files = {
        ".scenario/manifest.json": "{}",
        "TASK.md": "immutable task",
        ".env": "API_TOKEN=hostile",
        "scenarios/net-revenue/specification.json": "{}",
        "platform/dbt/models/marts/fct_orders.sql": "select 1",
        "platform/dbt/models/marts/fct_net_revenue.sql": "select 1",
        "platform/dbt/models/staging/sources.yml": "version: 2",
        "platform/dbt/tests/assert_fct_net_revenue_contract.sql": "select 1",
        "platform/airflow/dags/ecommerce_hourly.py": "# dag",
    }
    for relative, contents in files.items():
        path = workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
    return repository, workspace


def test_five_role_processes_have_distinct_uid_zero_network_and_scoped_filesystem(
    tmp_path: Path,
) -> None:
    repository, workspace = _repository(tmp_path)
    results = {}
    for profile_name in (
        "analyst_v1.json",
        "pm_v1.json",
        "data_engineer_v1.json",
        "qa_v1.json",
        "reviewer_v1.json",
    ):
        profile = load_runner_profile(repository, profile_name)
        runner = IsolatedRunner(
            repository,
            profile,
            None if profile.runner.role == "pm" else workspace,
        )
        result = runner.run_json(("/usr/bin/python3", "-I", "-c", PROBE), {"task_id": "task-1"})
        results[profile.runner.role] = result.payload

    assert {payload["uid"] for payload in results.values()} == {
        62001,
        62002,
        62003,
        62004,
        62005,
    }
    assert all(not payload["network_connect"] for payload in results.values())
    assert all(not payload["env_visible"] for payload in results.values())
    assert all(not payload["docker_socket_visible"] for payload in results.values())
    assert all(not payload["repository_visible"] for payload in results.values())
    assert all(
        set(payload["environment"])
        == {
            "HOME",
            "LANG",
            "PATH",
            "PWD",
            "PYTHONDONTWRITEBYTECODE",
            "RUNNER_ACTOR_ID",
            "RUNNER_ID",
            "RUNNER_ROLE",
            "TMPDIR",
        }
        for payload in results.values()
    )
    assert results["pm"]["workspace_exists"] is False
    assert results["pm"]["task_read"] is False
    for role in ("analyst", "qa", "reviewer"):
        assert results[role]["task_write"] is False
        assert results[role]["model_write"] is False
        assert results[role]["test_write"] is False
    assert results["data-engineer"]["task_write"] is False
    assert results["data-engineer"]["model_write"] is True
    assert results["data-engineer"]["test_write"] is True
    assert (workspace / "TASK.md").read_text() == "immutable task"
    assert (workspace / ".env").read_text() == "API_TOKEN=hostile"
