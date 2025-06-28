# TauTranslator Production Docker Image
# =====================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
# Install project with optional LLM extras
COPY pyproject.toml ./
COPY src ./src
COPY backend ./backend
RUN pip install --no-cache-dir \
    ".[llm]" \
    uvicorn[standard] fastapi

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 tau && \
    chown -R tau:tau /app

USER tau

# Expose ports
EXPOSE 5000 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV TAU_LOG_LEVEL=INFO
ENV TAU_DEFAULT_MODEL=gpt-3.5-turbo

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Default command starts the API server
CMD ["uvicorn", "backend.api.server:app", "--host", "0.0.0.0", "--port", "8000"]