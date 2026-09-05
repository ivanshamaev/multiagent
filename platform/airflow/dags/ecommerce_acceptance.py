"""Manual Airflow DAG for deterministic Cosmos acceptance runs."""

from cosmos_pipeline import build_ecommerce_dag

ecommerce_acceptance = build_ecommerce_dag(dag_id="ecommerce_acceptance", schedule=None)
