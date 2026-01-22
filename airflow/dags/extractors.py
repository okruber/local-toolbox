# ABOUTME: Generic extractors for fetching data from REST APIs.
# ABOUTME: Stateless functions that read config and write to specified destinations.

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import requests
import yaml

logger = logging.getLogger(__name__)

CONFIG_PATH = Path("/opt/airflow/config/pipeline_config.yaml")


def load_config() -> dict[str, Any]:
    """Load pipeline configuration from YAML file."""
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_field(data: dict[str, Any], field_path: str) -> Any:
    """Extract a field from nested data using dot notation.

    Supports simple paths like "generation.name" and array paths like "types[*].type.name".
    """
    if "[*]" in field_path:
        array_field, rest = field_path.split("[*].", 1)
        array_data = data.get(array_field, [])
        return [extract_field(item, rest) for item in array_data]

    parts = field_path.split(".")
    result = data
    for part in parts:
        if result is None:
            return None
        result = result.get(part) if isinstance(result, dict) else None
    return result


def fetch_pokemon(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Fetch Pokemon data based on config."""
    source_config = config["sources"]["pokemon"]
    base_url = source_config["base_url"]
    id_start = source_config["id_range"]["start"]
    id_end = source_config["id_range"]["end"]
    fields = source_config["fields"]
    nested_fields = source_config.get("nested_fields", {})

    pokemon_data = []
    for pokemon_id in range(id_start, id_end + 1):
        url = f"{base_url}/{pokemon_id}"
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            logger.warning("Failed to fetch Pokemon %d: %s", pokemon_id, response.status_code)
            continue

        data = response.json()
        record = {field: data.get(field) for field in fields}

        for field_name, field_path in nested_fields.items():
            record[field_name] = extract_field(data, field_path)

        pokemon_data.append(record)

        if pokemon_id % 50 == 0:
            logger.info("Fetched %d Pokemon", pokemon_id)

    logger.info("Completed fetching %d Pokemon", len(pokemon_data))
    return pokemon_data


def fetch_types(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Fetch Pokemon type data based on config."""
    source_config = config["sources"]["types"]
    base_url = source_config["base_url"]
    fields = source_config["fields"]
    nested_fields = source_config.get("nested_fields", {})

    response = requests.get(base_url, timeout=30)
    if response.status_code != 200:
        logger.error("Failed to fetch type list: %s", response.status_code)
        return []

    type_list = response.json()["results"]
    type_details = []

    for type_item in type_list:
        detail_response = requests.get(type_item["url"], timeout=30)
        if detail_response.status_code != 200:
            logger.warning("Failed to fetch type %s", type_item["name"])
            continue

        data = detail_response.json()
        record = {field: data.get(field) for field in fields}

        for field_name, field_path in nested_fields.items():
            record[field_name] = extract_field(data, field_path)

        type_details.append(record)

    logger.info("Completed fetching %d types", len(type_details))
    return type_details


def save_to_json(data: list[dict[str, Any]], output_path: Path) -> None:
    """Save extracted data to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("Saved %d records to %s", len(data), output_path)


def extract_source(source_name: str) -> None:
    """Extract data for a named source from config."""
    config = load_config()
    raw_data_path = Path(config["paths"]["raw_data"])
    source_config = config["sources"][source_name]
    output_file = source_config["output_file"]

    if source_name == "pokemon":
        data = fetch_pokemon(config)
    elif source_name == "types":
        data = fetch_types(config)
    else:
        raise ValueError(f"Unknown source: {source_name}")

    save_to_json(data, raw_data_path / output_file)
