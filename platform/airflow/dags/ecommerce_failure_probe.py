"""Airflow DAG for the manual fail-before-publish acceptance probe."""

from dbt_pipeline import build_ecommerce_dag

ecommerce_failure_probe = build_ecommerce_dag(
    dag_id="ecommerce_failure_probe", schedule=None, failure_probe=True
)
