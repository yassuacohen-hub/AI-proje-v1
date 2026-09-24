# API-LAYER2-DINAMIK-YÜKLEME-30 — Layer 2 Tablo Yükleme

**Task ID:** API-LAYER2-DINAMIK-YÜKLEME-30  
**Sahip:** Yasu  
**Öncelik:** P1  
**Dependency:** ALTYAPI-VERI-GORUNURLUK-01, API-KVKK-KONTROL-25

---

## Amaç

/api/company/{id} ve /api/match endpoints'te `plan_field_group` tablosundan paket-bazında alan görünürlüğü oku. `apply_kvkk_mask()` çağrısında `plan_field_visibility` parametre geç.

---

## Adımlar

### 1. plan_field_group Tablo Sorgusu

**Dosya:** web_app.py, `/api/company/{id}` endpoint

```python
# plan_field_group oku
with engine.connect() as conn:
    visibility_rows = conn.execute(
        text("""
            SELECT field_group, visibility FROM plan_field_group
            WHERE plan_id = :plan_id AND tier = :tier AND effective_to IS NULL
        """),
        {"plan_id": user.get("plan_id"), "tier": tier}
    ).mappings().all()

# Dict'e dönüştür: {field_group: visibility_type}
plan_field_visibility = {
    row["field_group"]: row["visibility"] 
    for row in visibility_rows
}
```

### 2. apply_kvkk_mask() Çağrısında Parameter Geç

```python
masked = apply_kvkk_mask(
    row, 
    admin_mode=admin_mode,
    plan_field_visibility=plan_field_visibility  # Layer 2
)
```

### 3. Kontrol

- Terminal tier: kimlik=açık, iletişim=kısıtlı, ticari=yasak
- Strategic tier: kimlik=açık, iletişim=yarı-açık, ticari=kısıtlı
- Enterprise tier: kimlık=açık, iletişim=açık, ticari=açık

---

## Kabul Kriteri

- [x] plan_field_group tablo sorgusu yazılı
- [x] plan_field_visibility dict oluşturuldu
- [x] apply_kvkk_mask() plan_field_visibility param geçti
- [x] Terminal/Strategic/Enterprise tier'ler fark doğru

---

## İlgili Nodlar

- [[Huginn Data Insights/src/company_master/schema/migrations/0018_visibility_layer.sql|plan_field_group tablo]]
- [[Huginn Data Insights/src/company_master/api/core/normalize.py#374-475|apply_kvkk_mask()]]
