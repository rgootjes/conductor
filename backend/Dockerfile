FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install project dependencies first to leverage Docker layer caching
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir .

# Copy application source
COPY src ./src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
