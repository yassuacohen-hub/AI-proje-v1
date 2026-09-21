# Brief: ALTYAPI-WEB-MONITOR-01 — Web Uygulaması Canlı Monitoring

**Görev ID:** ALTYAPI-WEB-MONITOR-01  
**Sahip:** UTKU (Üretim/Hacim)  
**Öncelik:** P2  
**Tahmini Süre:** 2s  
**Dosyalar:** `src/company_master/monitoring/`, `docker-compose.yml`

---

## DURUM
Zincir başlangıcı (UTKU'nun 4. görev zinciri, 1. adım). Önceki görev yok; hemen tetiklenir.

---

## AMAÇ
Huginn (müşteri, port 8000) ve Muninn (admin, port 8501) web uygulamaları için monitoring altyapısı:
- Health check endpoint'leri (`/health`) — durum, uptime, kontroller
- Canlı logging — request duration, status codes (Prometheus format)
- Alert kuralları — response time, error rate
- Docker health check integration

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. Health Check Endpoint'leri
- **Huginn (8000):**
  - GET `/health` → `{status: "ok", timestamp: "...", uptime: 1234, db: "ok"}`
  - Kontroller: DB bağlantısı, API yanıt süresi

- **Muninn (8501):**
  - GET `/health` → `{status: "ok", streamlit_alive: true, session_active: true}`

### 2. Logging & Metrics (FastAPI middleware)
- Middleware: `src/company_master/monitoring/middleware.py`
  - Request duration, status codes
  - Format: `{timestamp, method, path, status, duration_ms}`
  - Dosya: `logs/app.log` (JSON satır bazlı)

### 3. Alert Kuralları (JSON config)
- Dosya: `src/company_master/monitoring/alert_rules.json`
  ```json
  [
    {"rule": "response_time_p95_gt_2000ms", "action": "log_warning"},
    {"rule": "error_rate_gt_5percent", "action": "log_critical"}
  ]
  ```

### 4. Docker Compose Güncellemesi
- Huginn (8000) & Muninn (8501) health check tanımları
- Health check timeout: 5s, interval: 30s, retries: 3

---

## TEST DOSYASI
- **Path:** `tests/test_monitoring_health.py`
- **Test sayısı:** 6
  1. `test_huginn_health_endpoint` — GET /health status 200
  2. `test_huginn_health_content` — response JSON valid
  3. `test_muninn_health_endpoint` — GET /health status 200
  4. `test_monitoring_middleware_installed` — middleware aktif mi
  5. `test_alert_rules_json_valid` — alert_rules.json valid JSON
  6. `test_docker_health_check_config` — docker-compose.yml health check tanımı var mı

- Komut: `python -X utf8 -m pytest tests/test_monitoring_health.py -v`
- Hedef: 6/6 passed

---

## DOSYALAR
- `src/company_master/monitoring/` — yeni dizin
- `src/company_master/monitoring/__init__.py`
- `src/company_master/monitoring/middleware.py` — logging middleware
- `src/company_master/monitoring/alert_rules.json` — kural tanımları
- `docker-compose.yml` — health check entegrasyonu
- `tests/test_monitoring_health.py` — 6 test
- `logs/` — app.log dosyası oluşturulacak

---

## DEĞERLENDİRME KRİTERLERİ
1. ✓ Health check endpoint'leri her iki port'ta (8000, 8501) çalışıyor
2. ✓ Request logging middleware FastAPI'ye entegre edilmiş
3. ✓ Alert rules JSON valid ve okunabilir
4. ✓ Docker compose health check tanımları tamamlandı
5. ✓ 6 birim test yeşil
6. ✓ Kodlama denetimi temiz (UTF-8, BOM yok, Türkçe karakterler bozulmamış)

---

## SONRAKI GÖREV
ALTYAPI-PROXY-CONFIG-02 (Nginx reverse proxy yapılandırması)  
Otomatik tetiklenir: bu görev teslim edilince.
