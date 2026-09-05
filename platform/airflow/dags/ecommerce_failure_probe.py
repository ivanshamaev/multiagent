"""Airflow DAG for the manual fail-before-publish acceptance probe."""

from cosmos_pipeline import build_failure_probe_dag

ecommerce_failure_probe = build_failure_probe_dag()
