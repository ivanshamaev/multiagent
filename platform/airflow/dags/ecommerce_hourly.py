"""Airflow DAG for the hourly ecommerce dbt pipeline."""

from cosmos_pipeline import build_ecommerce_dag

ecommerce_hourly = build_ecommerce_dag(dag_id="ecommerce_hourly", schedule="@hourly")
