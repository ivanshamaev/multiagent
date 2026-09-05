"""Cosmos-managed dbt graph and deterministic Airflow boundary tasks."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from airflow.sdk import dag, get_current_context, task
from cosmos import DbtTaskGroup, ExecutionConfig, ProfileConfig, ProjectConfig, RenderConfig
from cosmos.constants import ExecutionMode, InvocationMode, LoadMode, TestBehavior
from cosmos.operators.local import DbtTestLocalOperator
from seed_readiness import PipelineCheckError, clickhouse_env, verify_seed_readiness

DBT_BIN = "/opt/airflow/dbt-venv/bin/dbt"
DBT_PROJECT = "/opt/airflow/dbt"
DBT_PROFILE = "/opt/airflow/dbt/profiles.yml"
FAILURE_PROJECT = "/opt/airflow/fixtures/failing_dbt"


def _profile_config() -> ProfileConfig:
    return ProfileConfig(
        profile_name="agentic_data_platform",
        target_name="dev",
        profiles_yml_filepath=DBT_PROFILE,
    )


def _project_config(project_dir: str = DBT_PROJECT) -> ProjectConfig:
    return ProjectConfig(
        dbt_project_path=project_dir,
        install_dbt_deps=False,
        env_vars=clickhouse_env(),
        partial_parse=True,
    )


def _execution_config() -> ExecutionConfig:
    return ExecutionConfig(
        execution_mode=ExecutionMode.LOCAL,
        invocation_mode=InvocationMode.SUBPROCESS,
        dbt_executable_path=DBT_BIN,
    )


def _render_config() -> RenderConfig:
    return RenderConfig(
        load_method=LoadMode.DBT_LS,
        invocation_mode=InvocationMode.SUBPROCESS,
        dbt_executable_path=DBT_BIN,
        test_behavior=TestBehavior.AFTER_ALL,
        emit_datasets=False,
    )


def _operator_args() -> dict[str, Any]:
    return {
        "append_env": False,
        "install_deps": False,
        "full_refresh": True,
        "fail_fast": True,
        "execution_timeout": timedelta(minutes=2),
    }


def build_ecommerce_dag(*, dag_id: str, schedule: str | None):
    """Build the production or manual acceptance DAG from the same dbt project."""

    @dag(
        dag_id=dag_id,
        schedule=schedule,
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        catchup=False,
        max_active_runs=1,
        dagrun_timeout=timedelta(minutes=10),
        is_paused_upon_creation=True,
        default_args={"retries": 0},
        tags=["agentic-data-platform", "dbt", "cosmos"],
    )
    def ecommerce_pipeline() -> None:
        @task(task_id="load_raw", execution_timeout=timedelta(minutes=1))
        def load_raw() -> dict[str, Any]:
            return verify_seed_readiness()

        @task(task_id="publish")
        def publish() -> dict[str, Any]:
            return {
                "published": True,
                "runner": "astronomer-cosmos",
                "run_id": str(get_current_context()["run_id"]),
            }

        dbt_graph = DbtTaskGroup(
            group_id="dbt",
            project_config=_project_config(),
            profile_config=_profile_config(),
            execution_config=_execution_config(),
            render_config=_render_config(),
            operator_args=_operator_args(),
        )
        load_raw() >> dbt_graph >> publish()

    return ecommerce_pipeline()


def build_failure_probe_dag():
    """Build a manual-only Cosmos test that must fail before publication."""

    @dag(
        dag_id="ecommerce_failure_probe",
        schedule=None,
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        catchup=False,
        max_active_runs=1,
        is_paused_upon_creation=True,
        default_args={"retries": 0},
        tags=["agentic-data-platform", "dbt", "cosmos", "failure-probe"],
    )
    def failure_probe() -> None:
        @task(task_id="load_raw")
        def load_raw() -> dict[str, Any]:
            return verify_seed_readiness()

        @task(task_id="publish")
        def publish() -> None:
            raise PipelineCheckError("failure probe must never publish")

        dbt_test = DbtTestLocalOperator(
            task_id="dbt_tests",
            project_dir=FAILURE_PROJECT,
            profile_config=_profile_config(),
            dbt_executable_path=DBT_BIN,
            env=clickhouse_env(),
            append_env=False,
            install_deps=False,
            partial_parse=False,
            fail_fast=True,
            emit_datasets=False,
            execution_timeout=timedelta(minutes=2),
        )
        load_raw() >> dbt_test >> publish()

    return failure_probe()
