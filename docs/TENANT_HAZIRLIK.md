# TEN-01 Multi-tenant Hazırlığı

## Yapılan
- `TenantContext` frozen dataclass oluşturuldu
- `VARSAYILAN_TENANT` ("huginn", "Huginn Data", "kurumsal") tanımlandı
- `tenant_coz(kaynak)` — tenant_id'den TenantContext üretir, varsayılanı döndürür
- `tenant_dogrula(tenant_id)` — regex `^[a-z0-9_-]{2,32}$` ile doğrulama
- `tests/test_tenant.py` — 8 test (çözümleme, frozen, varsayilan, hatalı id)
- `tests/test_tenant_bekci.py` — AST tarama (streamlit/auth import yasağı, frozen kontrol)

## Yapılmadı
- Veritabanı şeması değişikliği yok (bu turda yasak)
- Faturalama modülü yok
- KVKK ayrımı yok (iş modeli netleşince eklenecek)
- `tenant_id` kolonnarı eklenecek tablolar: henüz belirlenmedi (liste değil)

## İleriye Aşama
- `tenant_coz()` → auth/middleware katmanında çağrılacak
- `VARSAYILAN_TENANT` → tüm tenant-id yoksa kullanılacak
- DB migration → `tenant_id` NULLABLE column + index

## Kısıtlamalar
- `tenant` paketi `streamlit`/`auth` import etmez (bekçi testiyle doğrulanr)
- `frozen=True` — tenant context değiştirilemez

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]

- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
