# ALTYAPI-WEB-MONITOR-01 Rapor — 2026-09-20

## Görev
- **Task ID:** ALTYAPI-WEB-MONITOR-01
- **Ajan:** utku
- **Durum:** TAMAMLANDI → TESLİM
- **Öncelik:** P2
- **Brif:** data/orchestrator/ALTYAPI-WEB-MONITOR-01_brif_2026-09-20_uretim.md

## Yapılan İş
1. **`src/company_master/monitoring/__init__.py`** — paket export
2. **`src/company_master/monitoring/middleware.py`** — FastAPI MonitoringMiddleware
   - Request/response logging (JSON Lines: timestamp, method, path, status, duration_ms)
   - `logs/app.log` dosyasına append
   - `setup_monitoring(app)` ile tek satır entegrasyon
3. **`src/company_master/monitoring/alert_rules.json`** — alert kuralları
   - `response_time_p95_gt_2000ms` → log_warning
   - `error_rate_gt_5percent` → log_critical
3. **`web_app.py`** — entegrasyon
   - `setup_monitoring(app)` middleware eklendi
   - `/health` detailed endpoint: status, timestamp, uptime_seconds, db, version
   - Mevcut `/api/health` korundu
4. **`docker-compose.yml`** — health check güncellemeleri
   - `api` service: curl `/health`, interval 30s, timeout 5s, retries 3, start_period 20s
   - `streamlit`: timeout 10s → 5s (brief uyumu)
4. **`src/company_master/monitoring/alert_rules.json`** — 2 kural
5. **`tests/test_monitoring_health.py`** — 6 test

## Test Sonuçları
```
tests/test_monitoring_health.py -v  →  6 PASSED
```

## Full Suite Regression
```
4 failed, 3954 passed, 22 skipped, 127 warnings in 68.59s
```

### Bilinen Test Failure'ları (ALTYAPI-WEB-MONITOR-01 Dışı — Önceden Var)
1. `test_find_root_finds_env` — .env konfigürasyonu
2. `test_sekme_rehberi_metinleri_utf8_ve_yapili` — encoding
3. `test_auth_modal_icerik_fonksiyonu` — app.py "Şifremi unuttum" eksik
4. `test_render_webhook_monitor_tab_renders_metrics` — st.metric çağrısı eksik

**ALTYAPI-WEB-MONITOR-01 çalışması BU failure'lara neden olmamıştır.**

## Kodlama Denetim
- `python scripts/kodlama_denetim.py --tam-repo` — `middleware.py`, `alert_rules.json`, `test_monitoring_health.py` listede yok (temiz)

## Health Endpoint Detayları
- **Huginn (8000)**: GET `/health` → `{status, timestamp, uptime_seconds, db, version}`
- **Muninn (8501)**: Docker health check → `curl /_stcore/health` (timeout 5s)

## Docker Health Check
- `api` (8000): `curl /health`, interval 30s, timeout 5s, retries 3, start_period 20s
- `streamlit` (8501): `curl /_stcore/health`, interval 30s, timeout 5s, retries 3

## Alert Rules
- `response_time_p95_gt_2000ms` → log_warning
- `error_rate_gt_5percent` → log_critical

## Log Format (logs/app.log — JSON Lines)
```json
{"timestamp":"2026-09-20T12:34:56.789Z","method":"GET","path":"/health","status":200,"duration_ms":12.5}
```

## Zincir Devamı
⏭ **ALTYAPI-PROXY-CONFIG-02** (Nginx reverse proxy) otomatik tetiklenir.

## Bulgular
🟢 **Tamam:** Middleware + health endpoint + alert rules + docker healthcheck + 6 test
🟢 **Tamam:** `datetime.utcnow()` → `datetime.now(timezone.utc)` (deprecation fix)
🟡 **Dikkat:** `logs/app.log` JSON Lines formatında yazılıyor — rotation/size limit eklenebilir (ALTYAPI-PROXY-CONFIG-02)
🔵 **Öneri:** Prometheus exporter /metrics endpoint'i zaten var (line 461) — Grafana dashboard için kullanılabilir
🔵 **Öneri:** Alert evaluation logic (p95, error_rate) ilerleyen görevlerde implement edilebilir