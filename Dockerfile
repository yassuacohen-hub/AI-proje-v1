# Huginn Data Insights - Dockerfile (Faz 2 — Multi-stage)
# Kullanim: docker compose --profile localdb up -d --build
#          docker compose up -d --build api

# ===== Stage 1: Builder =====
FROM python:3.12-slim AS builder

WORKDIR /build

# Sadece build-stage calisir; runtime'a gerek yok
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-app.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements-app.txt

# ===== Stage 2: Runtime =====
FROM python:3.12-slim AS runtime

WORKDIR /app

# Healthcheck + runtime icin curl (builder'dan copy edilebilir ama slim'de zaten yok)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Builder'dan kopyala
COPY --from=builder /install /usr/local

# Uygulama kodu
COPY . .

# Root olmayan kullanici
RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /app/logs /app/data /app/web_dashboard \
    && chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "8000"]