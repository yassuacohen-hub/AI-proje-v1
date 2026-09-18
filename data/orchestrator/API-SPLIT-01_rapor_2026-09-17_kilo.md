# API-SPLIT-01 Raporu

**Tarih:** 2026-09-17
**Ajan:** kilo
**Paket:** `web_app.py` → `src/company_master/api/` (modülerleşme)
**Durum:** KISMI

## Yapılanlar

### normalize.py — Çıkarıldı ✅
- **Dosya:** `src/company_master/api/core/normalize.py` (574 satır)
- **İçerik:** `_tr_*, _mask_*, apply_kvkk_mask, normalize_company_name, normalize_company, extract_trade_name, tr_normalize`
- **DASH_MASK_PII** tanımları bu modüle taşındı
- **Düzeltme:** normalize.py'de eksik olan `DASH_MASK_PII` tanımı eklendi (test kırılması nedeni)

### web_app.py — İthalat Eklendi ✅
- Lines 72-77: `from src.company_master.api.core.normalize import (...)`
- `normalize_company_name`, `normalize_company` ve diğer fonksiyonlar re-export ediliyor
- 3795 test geçti, 4 failed (kilitle pré-eksist), 5 skipped

### Hatalar Düzeltildi
- normalize.py'den `_mask_active` çağrısında `DASH_MASK_PII` NameError → `DASH_MASK_PII` tanımı eklendi

## Kaldı (Zincir Sırası)

| Modül | Kapsam | Durum |
|-------|--------|-------|
| `api/core/cache.py` | cache_get, cache_set, admin_cache | Yapılmadı |
| `api/core/security.py` | require_api_key, _user_from_api_key, _record_api_usage, rate limit, _hash_password, _verify_password, _send_telegram | Yapılmadı |
| `api/routers/webhooks.py` | /api/webhooks/apify* | Yapılmadı |
| `api/routers/intelligence.py` | /api/intelligence/*, /api/kpi, /api/dashboard, /api/metrics | Yapılmadı |
| `api/routers/companies.py` | /api/companies*, /api/company/{id}, /api/sources, /api/quality-trend | Yapılmadı |
| `api/routers/match.py` | /api/match | Yapılmadı |
| `api/routers/buyer.py` | /api/buyer/* | Yapılmadı |
| `api/routers/admin.py` | /api/admin/* | Yapılmadı |

## Monkeypatch Re-export Listesi (Test Uyumu)

Aşağıdaki isimler `web_app.py`'de re-export edilmeli (testler `monkeypatch.setattr(web_app, ...)` kullanıyor):

- `get_engine` — import: `from company_master.db.connection import get_engine`
- `_verify_password` — `api/core/security.py`
- `_hash_password` — `api/core/security.py`
- `_user_from_token` — `api/core/security.py`
- `_send_telegram` — `api/core/security.py`
- `_fetch_dashboard_data` — `api/routers/intelligence.py`
- `_dl_mask_ip` — `api/core/security.py`
- `_mask_email` — normalize.py ✅
- `_mask_phone` — normalize.py ✅
- `apply_kvkk_mask` — normalize.py ✅
- `DASH_API_KEY` — web_app.py global (kalmalı)
- `MAX_COMPANIES_LIMIT` — web_app.py global (kalmalı)
- `DASH_MASK_PII` — normalize.py ✅
- `_RATE_LIMIT`, `_CACHE` — web_app.py global (kalmalı)

## Test Sonuçları
- **tests/test_kurallar.py:** 18 passed
- **Tam süit:** 3795 passed, 4 failed (locked __init__.py), 5 skipped
- **Kodlama_denetim:** temiz

## Riskler
- web_app.py kilidi: API-SPLIT-01 kendi kilidi (kilo sahibi)
- Monkeypatch hedefleri değiştirildikçe testler güncellenmeli
- Geriye uyumlu re-export ZORUNLU