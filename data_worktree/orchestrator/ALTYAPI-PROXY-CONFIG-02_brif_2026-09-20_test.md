# Brief: ALTYAPI-PROXY-CONFIG-02 — Reverse Proxy Yapılandırması (Nginx)

**Görev ID:** ALTYAPI-PROXY-CONFIG-02  
**Sahip:** SALİH (Test Danışman)  
**Öncelik:** P2  
**Tahmini Süre:** 2s  
**Dosyalar:** `config/nginx.conf`, `docker-compose.yml`

---

## DURUM
Zincir adımı 2. Önceki: **ALTYAPI-WEB-MONITOR-01** (tamamlanınca otomatik tetiklenir).

---

## AMAÇ
Nginx reverse proxy oluştur:
- Huginn (Flask/FastAPI) → port 8000
- Muninn (Streamlit) → port 8501
- Staging: localhost/api → 8000, localhost/admin → 8501
- Health check integration (ALTYAPI-WEB-MONITOR-01'den)

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. Nginx Yapısı
- Upstreams:
  ```nginx
  upstream huginn { server api:8000; }
  upstream muninn { server web_dashboard:8501; }
  ```
- Virtual hosts:
  - `localhost/api/*` → huginn
  - `localhost/admin/*` → muninn
  - `localhost/health` → health check (JSON dönü)

### 2. Proxy Headers
- `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Real-IP`
- Timeout: 30s (long-polling için Streamlit)
- Buffer size: 4k (form data)

### 3. Health Check Binding
- Nginx `/health` → `http://huginn/health` + `http://muninn/health`
- Dönüş: ikisi de ok ise `{status: "healthy"}`
- Log: `/logs/nginx_health.log`

### 4. SSL (Test ortamında self-signed)
- Certificate: `config/certs/selfsigned.crt/.key`
- HTTPS: `https://localhost/api`, `https://localhost/admin`
- Redirect: HTTP → HTTPS (opsiyonel)

### 5. Test Dosyası
- `tests/test_nginx_config.py` — 8 test
  - `test_nginx_syntax` (1 test)
  - `test_upstream_huginn` (2 test)
  - `test_upstream_muninn` (2 test)
  - `test_proxy_headers` (2 test)
  - `test_nginx_health_endpoint` (1 test)
- Tüm testler yeşil: `python -X utf8 -m pytest tests/test_nginx_config.py -v`

---

## DOSYALAR
- Yaz: `config/nginx.conf`
- Yaz: `config/certs/generate_self_signed.sh`
- Düzenle: `docker-compose.yml` (nginx servis ekle)
- Düzenle: `tests/test_nginx_config.py`

---

## DEĞERLENDİRME KRİTERLERİ
✅ Nginx config syntax doğru  
✅ Upstream'ler tanımlı ve çalışıyor  
✅ Proxy headers tam  
✅ Health check endpoint aktif  
✅ Self-signed sertifika kurulu  
✅ Test sayısı: 8 (tümü yeşil)  
✅ UTF-8 temiz

---

## SONRAKI GÖREV
TEST-PLAN-COVERAGE-03 (zincir otomatik tetiklenir)
