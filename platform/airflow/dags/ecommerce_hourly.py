"""Airflow DAG for the hourly ecommerce dbt pipeline."""

from dbt_pipeline import build_ecommerce_dag

ecommerce_hourly = build_ecommerce_dag(dag_id="ecommerce_hourly", schedule="@hourly")
