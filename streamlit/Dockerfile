# ABOUTME: Docker image for natural language query UI.
# Uses uv for fast dependency management.

FROM ghcr.io/astral-sh/uv:0.7.4 AS uv
FROM python:3.12-slim

COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml *.py /app/
RUN uv sync --no-dev --no-install-project

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD [".venv/bin/streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
