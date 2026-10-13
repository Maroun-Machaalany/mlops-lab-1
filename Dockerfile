
# Stage 1: Install dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock README.md ./

RUN UV_HTTP_TIMEOUT=300 UV_HTTP_RETRIES=5 uv sync --frozen --no-dev --no-editable --no-install-project

COPY src/ ./src/


# Stage 2: Run the FastAPI application
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY docker-model/ /app/docker-model/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV MLFLOW_TRACKING_URI="http://host.docker.internal:5000"
ENV MODEL_URI="/app/docker-model"

EXPOSE 8000

CMD ["uvicorn", "food11.serve:app", "--host", "0.0.0.0", "--port", "8000"]
