# Brief: ALTYAPI-WEB-MONITOR-01 — Web Uygulaması Canlı Monitoring

**Görev ID:** ALTYAPI-WEB-MONITOR-01  
**Sahip:** SALİH (Test Danışman)  
**Öncelik:** P2  
**Tahmini Süre:** 2s  
**Dosyalar:** `src/company_master/monitoring/`, `docker-compose.yml`

---

## DURUM
Zincir başlangıcı (SALİH'in 1. görev). Önceki görev yok; hemen tetiklenir.

---

## AMAÇ
Huginn (müşteri) ve Muninn (admin) web uygulamaları için monitoring altyapısı:
- Health check endpoint'leri (8000, 8501 portları)
- Canlı uptime takibi (logs + metrics)
- Alert kuralları (response time, error rate)
- Grafana dashboard (opsiyonel, temel)

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. Health Check Endpoint'leri
- Huginn (8000):
  - GET `/health` → `{status: "ok", timestamp: "...", uptime: 1234}`
  - Kontrol: DB bağlantısı, API yanıt süresi
- Muninn (8501):
  - GET `/health` → Streamlit process aktif mi?
  - Kontrol: Session state, cache status

### 2. Logging & Metrics
- FastAPI (huginn):
  - `middlewares/monitoring.py` — request duration, status codes (Prometheus format)
  - `logs/app.log` — saat, endpoint, status, latency
- Streamlit (muninn):
  - `logs/streamlit.log` — page load, widget event, error
  - Canlı takip: `tail -f logs/streamlit.log`

### 3. Alert Kuralları
- Kurallar (JSON config):
  ```json
  {
    "rule": "response_time_p95_gt_2000ms",
    "action": "log_warning"
  },
  {
    "rule": "error_rate_gt_5percent",
    "action": "log_critical"
  }
  ```
- Action: `log_warning`, `log_critical`, `send_alert` (optional)

### 4. Docker Compose Güncellemesi
- Huginn (8000): health check script
  ```yaml
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
  ```
- Muninn (8501): process check (Streamlit native)

### 5. Test Dosyası
- `tests/test_web_monitor.py` — 7 test
  - `test_health_endpoint_huginn` (2 test)
  - `test_health_endpoint_muninn` (2 test)
  - `test_logging_format` (2 test)
  - `test_alert_rules_load` (1 test)
- Tüm testler yeşil: `python -X utf8 -m pytest tests/test_web_monitor.py -v`

---

## DOSYALAR
- Yaz: `src/company_master/monitoring/health.py`
- Yaz: `src/company_master/monitoring/metrics.py`
- Yaz: `src/company_master/monitoring/alerts.py`
- Düzenle: `docker-compose.yml`
- Düzenle: `tests/test_web_monitor.py`

---

## DEĞERLENDİRME KRİTERLERİ
✅ Health check endpoint (8000, 8501) çalışıyor  
✅ Logging format tutarlı  
✅ Alert kuralları yükleniyor  
✅ Docker compose healthcheck tanımlı  
✅ Test sayısı: 7 (tümü yeşil)  
✅ UTF-8 temiz

---

## SONRAKI GÖREV
ALTYAPI-PROXY-CONFIG-02 (zincir otomatik tetiklenir)
