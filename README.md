# Local Data Stack Toolbox

An experimentation sandbox for building and testing local data pipelines. This project provides a containerized environment with data stack components for prototyping.

## Components

| Technology | Purpose | Port |
|------------|---------|------|
| **Airflow** | Workflow orchestration and scheduling | 8080 |
| **DuckDB** | Embedded OLAP database | - |
| **dbt** | Data transformation and modeling | - |
| **Cube** | Semantic layer and analytics API | 4000, 15432 |

## Quick Start

```bash
docker compose up
```

Services available at:
- Airflow UI: http://localhost:8080 (credentials: `airflow` / `airflow`)
- Cube Playground: http://localhost:4000

## Project Structure

```
.
├── airflow/              # Airflow DAGs and configuration
├── cube/                 # Cube semantic layer configuration
├── dbt_project/          # dbt models and configuration
├── dwh/                  # DuckDB database files
└── docker-compose.yaml   # Service orchestration
```

## Documentation

- [cube.md](cube.md) - Cube semantic layer setup, API usage, and model definitions
