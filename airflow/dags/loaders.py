# ABOUTME: Generic loaders for writing data to DuckDB.
# ABOUTME: Stateless functions that read config and load data from JSON to tables.

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import duckdb
import yaml

logger = logging.getLogger(__name__)

CONFIG_PATH = Path("/opt/airflow/config/pipeline_config.yaml")


def load_config() -> dict[str, Any]:
    """Load pipeline configuration from YAML file."""
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_source_to_duckdb(source_name: str) -> None:
    """Load a single source's JSON data into DuckDB."""
    config = load_config()
    raw_data_path = Path(config["paths"]["raw_data"])
    db_path = Path(config["paths"]["database"])

    dest_config = config["destinations"][f"raw_{source_name}"]
    source_config = config["sources"][dest_config["source"]]
    table_name = dest_config["table_name"]
    json_file = raw_data_path / source_config["output_file"]

    db_path.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(db_path))
    con.execute(
        f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_json_auto('{json_file}')"
    )
    con.close()

    logger.info("Loaded %s into table %s", json_file, table_name)


def load_all_sources() -> None:
    """Load all configured sources into DuckDB."""
    config = load_config()

    for dest_name in config["destinations"]:
        source_name = dest_name.replace("raw_", "")
        load_source_to_duckdb(source_name)
