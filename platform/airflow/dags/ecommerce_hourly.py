"""Executable Airflow contract for the ecommerce pipeline stage order.

The tasks deliberately validate orchestration only. A later step will connect
these stages to the isolated seed and dbt runners without a Docker socket.
"""

from datetime import UTC, datetime, timedelta

from airflow.sdk import dag, task


def require_stage(actual: str, expected: str) -> None:
    """Fail deterministically when an upstream stage returned the wrong marker."""
    if actual != expected:
        raise ValueError(f"expected upstream stage {expected!r}, received {actual!r}")


@dag(
    dag_id="ecommerce_hourly",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1, tzinfo=UTC),
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=5),
    default_args={"retries": 0, "execution_timeout": timedelta(seconds=30)},
    tags=["agentic-data-platform", "baseline"],
)
def ecommerce_hourly() -> None:
    """Prove the six-stage orchestration contract through the Execution API."""

    @task
    def load_raw() -> str:
        return "raw_loaded"

    @task
    def dbt_staging(upstream: str) -> str:
        require_stage(upstream, "raw_loaded")
        return "staging_built"

    @task
    def dbt_intermediate(upstream: str) -> str:
        require_stage(upstream, "staging_built")
        return "intermediate_built"

    @task
    def dbt_marts(upstream: str) -> str:
        require_stage(upstream, "intermediate_built")
        return "marts_built"

    @task
    def dbt_tests(upstream: str) -> str:
        require_stage(upstream, "marts_built")
        return "tests_passed"

    @task
    def publish(upstream: str) -> str:
        require_stage(upstream, "tests_passed")
        return "published"

    publish(dbt_tests(dbt_marts(dbt_intermediate(dbt_staging(load_raw())))))


ecommerce_hourly()
