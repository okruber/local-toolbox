# ABOUTME: Cube REST API client for schema introspection and query execution.
# Provides typed interfaces for natural language query UI integration.

import json
import os
from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class CubeDimension:
    name: str
    type: str
    description: str


@dataclass(frozen=True)
class CubeMeasure:
    name: str
    type: str
    description: str


@dataclass(frozen=True)
class CubeSchema:
    cube_name: str
    dimensions: list[CubeDimension]
    measures: list[CubeMeasure]


@dataclass(frozen=True)
class CubeQueryResult:
    data: list[dict]
    query: dict


class CubeClientError(Exception):
    pass


class CubeClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or os.environ.get("CUBE_URL", "http://localhost:4000")

    def get_schema(self) -> list[CubeSchema]:
        url = f"{self.base_url}/cubejs-api/v1/meta"
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            raise CubeClientError(f"Failed to fetch schema: {response.status_code} {response.text}")

        meta = response.json()
        schemas = []

        cubes = meta.get("cubes", [])
        for cube in cubes:
            dimensions = [
                CubeDimension(
                    name=dim.get("name", ""),
                    type=dim.get("type", ""),
                    description=dim.get("description", dim.get("title", "")),
                )
                for dim in cube.get("dimensions", [])
            ]
            measures = [
                CubeMeasure(
                    name=m.get("name", ""),
                    type=m.get("type", ""),
                    description=m.get("description", m.get("title", "")),
                )
                for m in cube.get("measures", [])
            ]
            schemas.append(
                CubeSchema(
                    cube_name=cube.get("name", ""),
                    dimensions=dimensions,
                    measures=measures,
                )
            )

        return schemas

    def execute_query(self, query: dict) -> CubeQueryResult:
        url = f"{self.base_url}/cubejs-api/v1/load"
        response = requests.post(url, json={"query": query}, timeout=60)

        if response.status_code != 200:
            raise CubeClientError(f"Query failed: {response.status_code} {response.text}")

        result = response.json()
        data = result.get("data", [])

        return CubeQueryResult(data=data, query=query)


def schema_to_prompt_context(schemas: list[CubeSchema]) -> str:
    lines = ["Available Cube schema:"]

    for schema in schemas:
        lines.append(f"\nCube: {schema.cube_name}")

        if schema.dimensions:
            lines.append("  Dimensions:")
            for dim in schema.dimensions:
                desc = f" - {dim.description}" if dim.description else ""
                lines.append(f"    - {dim.name} ({dim.type}){desc}")

        if schema.measures:
            lines.append("  Measures:")
            for measure in schema.measures:
                desc = f" - {measure.description}" if measure.description else ""
                lines.append(f"    - {measure.name} ({measure.type}){desc}")

    return "\n".join(lines)
