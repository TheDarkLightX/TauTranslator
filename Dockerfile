FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080 \
    PYTHONPATH="/app/src:/app"

WORKDIR /app

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt uvicorn

COPY . .

# Install the project so src packages import correctly and data files are included
RUN pip install . && python -c "import pkgutil, sys; print('installed packages ok')"

EXPOSE 8080

CMD ["uvicorn", "backend.api.server:app", "--host", "0.0.0.0", "--port", "8080"]

