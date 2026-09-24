# Huginn Data Insights - Dockerfile (Faz 1, 2026-09-09)
# API + vanilla JS dashboard tek konteyner; DB harici (Supabase veya compose db servisi)
FROM python:3.12-slim

WORKDIR /app

# Sadece healthcheck için curl gerekli
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Önce bağımlılıklar (layer cache: kod değişince yeniden kurulmaz)
COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt

# Uygulama kodu (.dockerignore sayesinde .env, backups, AI proje v1 dahil DEĞİL)
COPY . .

# Root olmayan kullanıcı
RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /app/logs && chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "8000"]