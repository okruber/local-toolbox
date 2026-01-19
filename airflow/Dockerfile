FROM apache/airflow:2.8.1-python3.11

USER root

RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN uv venv /opt/dbt_venv && \
    uv pip install --python /opt/dbt_venv/bin/python --no-cache \
        dbt-duckdb \
        dbt-core \
        duckdb \
        "protobuf>=5.26.0,<6.0.0"

RUN printf '#!/bin/bash\nexec /opt/dbt_venv/bin/dbt "$@"\n' > /usr/local/bin/dbt && \
    chmod +x /usr/local/bin/dbt

USER airflow

RUN pip install --no-cache-dir duckdb requests pandas
