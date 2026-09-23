# ALTYAPI-WEB-MONITOR-01 Briefi

## GÖREV TANIMI
Huginn (8000) ve Muninn (8501) web uygulamaları için canlı monitoring altyapısı (zincir başlangıcı). Health check endpoint'leri, request logging middleware, alert kuralları ve Docker health check entegrasyonu. Detaylı brif: `data_worktree/orchestrator/ALTYAPI-WEB-MONITOR-01_brif_2026-09-20_uretim.md`.

## İŞ MADDELERİ
1. `src/company_master/monitoring/__init__.py` + `middleware.py` (JSON satır bazlı log: logs/app.log)
2. Health endpoint'ler: Huginn `{status, timestamp, uptime, db}` / Muninn `{status, streamlit_alive, session_active}`
3. `src/company_master/monitoring/alert_rules.json` — response_time / error_rate kuralları
4. `docker-compose.yml` health check tanımları (timeout 5s, interval 30s, retries 3)
5. `tests/test_monitoring_health.py` — 6 test

## KENDİ-KONTROL
- [ ] İş tamamlandı
- [ ] 6/6 test yeşil
- [ ] UTF-8 temiz
