FROM apache/airflow:2.8.1-python3.11

USER root

RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install DBT dependencies using uv project workflow
COPY dbt-requirements/pyproject.toml dbt-requirements/uv.lock /opt/dbt_venv/
WORKDIR /opt/dbt_venv
RUN uv sync --frozen --no-dev

RUN printf '#!/bin/bash\nexec /opt/dbt_venv/.venv/bin/dbt "$@"\n' > /usr/local/bin/dbt && \
    chmod +x /usr/local/bin/dbt

USER airflow

# Install Airflow DAG dependencies (using uv as pip replacement for Airflow's environment)
RUN uv pip install --no-cache duckdb requests pandas pyyaml
