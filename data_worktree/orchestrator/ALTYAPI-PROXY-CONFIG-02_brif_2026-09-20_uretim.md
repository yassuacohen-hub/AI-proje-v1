# Brief: ALTYAPI-PROXY-CONFIG-02 — Reverse Proxy Yapılandırması (Nginx)

**Görev ID:** ALTYAPI-PROXY-CONFIG-02  
**Sahip:** UTKU (Üretim/Hacim)  
**Öncelik:** P2  
**Tahmini Süre:** 2s  
**Dosyalar:** `config/nginx.conf`, `docker-compose.yml`

---

## DURUM
Zincir adımı 2. Önceki: **ALTYAPI-WEB-MONITOR-01** (tamamlanınca otomatik tetiklenir).

---

## AMAÇ
Nginx reverse proxy oluştur:
- Huginn (FastAPI, port 8000) → `/api`
- Muninn (Streamlit, port 8501) → `/admin`
- Health check entegrasyonu (ALTYAPI-WEB-MONITOR-01'den)
- SSL self-signed (test ortamı)

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. Nginx Yapısı & Upstreams
```nginx
upstream huginn {
  server api:8000;
}
upstream muninn {
  server web_dashboard:8501;
}

server {
  listen 80;
  server_name localhost;

  location /api/ {
    proxy_pass http://huginn/;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 30s;
  }

  location /admin/ {
    proxy_pass http://muninn/;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 30s;
  }

  location /health {
    return 200 '{"status":"healthy"}';
    add_header Content-Type application/json;
  }
}
```

### 2. Proxy Headers
- `X-Forwarded-For` — client IP
- `X-Forwarded-Proto` — request scheme (http/https)
- `X-Real-IP` — real client IP
- Timeout: 30s (Streamlit long-polling)

### 3. Health Check Binding
- `/health` endpoint → basit JSON `{"status":"healthy"}`
- Log: `logs/nginx_health.log` (access_log)

### 4. SSL (self-signed, test ortamı)
- Certificate: `config/certs/selfsigned.crt` & `config/certs/selfsigned.key`
- HTTPS port: 443
- HTTP → HTTPS yönlendirmesi (isteğe bağlı)

### 5. Docker Compose Entegrasyonu
- Nginx container service ekleme
- Volumes: `config/nginx.conf` → `/etc/nginx/nginx.conf`
- Ports: `80:80`, `443:443`
- Depends-on: api, web_dashboard
- Health check: `curl -f http://localhost/health || exit 1`

---

## TEST DOSYASI
- **Path:** `tests/test_nginx_config.py`
- **Test sayısı:** 8
  1. `test_nginx_syntax` — nginx -t geçer mi
  2. `test_upstream_huginn_exists` — upstream huginn tanımı var mı
  3. `test_upstream_huginn_server_address` — server api:8000
  4. `test_upstream_muninn_exists` — upstream muninn tanımı var mı
  5. `test_upstream_muninn_server_address` — server web_dashboard:8501
  6. `test_proxy_headers_set` — X-Forwarded-* headers var mı
  7. `test_health_endpoint_config` — /health location tanımı var mı
  8. `test_docker_compose_nginx_service` — nginx servisi docker-compose.yml'de tanımlı mı

- Komut: `python -X utf8 -m pytest tests/test_nginx_config.py -v`
- Hedef: 8/8 passed

---

## DOSYALAR
- `config/nginx.conf` — Ana Nginx yapılandırma (yeni veya güncelleme)
- `config/certs/selfsigned.crt` — Test SSL sertifikası
- `config/certs/selfsigned.key` — Test SSL anahtarı
- `docker-compose.yml` — Nginx servisi ekleme/güncelleme
- `tests/test_nginx_config.py` — 8 test
- `logs/nginx_health.log` — Nginx access log (çalışma zamanında oluşturulacak)

---

## DEĞERLENDİRME KRİTERLERİ
1. ✓ Nginx yapılandırması syntax hatası yok (nginx -t)
2. ✓ Upstreams tanımlanmış: huginn (8000), muninn (8501)
3. ✓ Proxy locations: /api → huginn, /admin → muninn
4. ✓ Proxy headers (X-Forwarded-*) ayarlanmış
5. ✓ Health check endpoint (/health) çalışıyor
6. ✓ SSL sertifikası ve anahtarı mevcut
7. ✓ Docker Compose'de nginx servisi tanımlanmış
8. ✓ 8 birim test yeşil
9. ✓ Kodlama denetimi temiz

---

## SONRAKI GÖREV
TEST-PLAN-COVERAGE-03 (Test kapsam planı)  
Otomatik tetiklenir: bu görev teslim edilince.
