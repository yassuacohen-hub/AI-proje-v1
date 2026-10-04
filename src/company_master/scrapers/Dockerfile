# Huginn Data Insights - Kazima (scraper) Dockerfile
# Brief: plans/2026-10-01_docker_tasi... (SCRAPE-005-KAZIMA-DOCKER-INTEGRATION)
# Kullanim:
#   docker compose --profile localdb --profile jobs build kazima
#   docker compose --profile localdb --profile jobs run --rm kazima
#
# NOT: bu image TEK SEFERLIK bir batch isidir (CMD -> refresh_pipeline.py).
# Surekli bir HTTP servisi DEGILDIR; bu yuzden brifin "curl localhost:5000/health"
# healthcheck'i UYGULANMADI - o port proje hicbir yerinde kullanilmaz (olculdu:
# docker-compose.yml, Dockerfile, scripts/refresh_pipeline.py icinde 0 eslesme).
# Bunun yerine isin gercek bagimliligi olan PostgreSQL erisimi denetlenir.

FROM python:3.12-slim

WORKDIR /app

COPY requirements-app.txt .
RUN pip install -q --no-cache-dir -r requirements-app.txt

# .dockerignore `logs/` ve `data/` dizinlerini build contextinden cikarir;
# scripts/refresh_pipeline.py modul seviyesinde logs/scrape_refresh.log acar.
# Volume mount gelmeden once dizinler mevcut olmali, yoksa FileNotFoundError.
RUN mkdir -p /app/logs /app/data

COPY . .

# psycopg[binary] requirements-app.txt icinde kuruludur; asagidaki healthcheck
# kurulum ek paketi istemez (curl de gerekmez).
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import os, psycopg; psycopg.connect(os.environ['DATABASE_URL']).close()" || exit 1

CMD ["python", "scripts/refresh_pipeline.py"]
