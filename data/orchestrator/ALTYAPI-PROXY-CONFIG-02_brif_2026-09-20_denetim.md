# ALTYAPI-PROXY-CONFIG-02 Briefi

## GÖREV TANIMI
Nginx reverse proxy yapılandırması (zincir adımı 2, önceki: ALTYAPI-WEB-MONITOR-01). Huginn (FastAPI, 8000) → `/api`, Muninn (Streamlit, 8501) → `/admin`, health check ve self-signed SSL. Detaylı brif: `data_worktree/orchestrator/ALTYAPI-PROXY-CONFIG-02_brif_2026-09-20_uretim.md`.

## İŞ MADDELERİ
1. `config/nginx.conf` — upstreams (huginn: api:8000, muninn: web_dashboard:8501), proxy headers, `/health` endpoint
2. SSL self-signed: `config/certs/selfsigned.crt` + `.key`
3. `docker-compose.yml` — nginx servisi (ports 80/443, volumes, depends_on, healthcheck)
4. `tests/test_nginx_config.py` — 8 test

## KENDİ-KONTROL
- [ ] İş tamamlandı
- [ ] 8/8 test yeşil
- [ ] `python scripts/kodlama_denetim.py` temiz
