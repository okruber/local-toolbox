# ABOUTME: Config-driven Pokedex ETL DAG for Airflow.
# ABOUTME: Stateless pipeline that reads all parameters from pipeline_config.yaml.

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from extractors import extract_source
from loaders import load_all_sources

CONFIG_PATH = Path("/opt/airflow/config/pipeline_config.yaml")


def load_config() -> dict[str, Any]:
    """Load pipeline configuration from YAML file."""
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config()
pipeline_config = config["pipeline"]
paths_config = config["paths"]

with DAG(
    dag_id=pipeline_config["name"],
    start_date=datetime.fromisoformat(pipeline_config["start_date"]),
    schedule_interval=pipeline_config["schedule"],
    catchup=False,
) as dag:

    extract_pokemon = PythonOperator(
        task_id="extract_pokemon",
        python_callable=extract_source,
        op_args=["pokemon"],
    )

    extract_types = PythonOperator(
        task_id="extract_types",
        python_callable=extract_source,
        op_args=["types"],
    )

    load_to_duckdb = PythonOperator(
        task_id="load_to_duckdb",
        python_callable=load_all_sources,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {paths_config['dbt_project']} && dbt run --profiles-dir .",
    )

    [extract_pokemon, extract_types] >> load_to_duckdb >> dbt_run
