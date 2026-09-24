# KONTROL-KVKK-MASKELEME-31 — Admin Mode E2E Test

**Task ID:** KONTROL-KVKK-MASKELEME-31  
**Sahip:** Yasu  
**Öncelik:** P1  
**Dependency:** ALTYAPI-VERI-GORUNURLUK-01, API-KVKK-KONTROL-25

---

## Amaç

End-to-end test: Admin `/api/admin/kvkk-mode` POST çağrısı ile strict ↔ lenient mod değişimi → `/api/company/{id}` response'ta field maskeleme değişimi doğrula.

---

## Adımlar

### 1. Test Setup

Test DB'de test şirketi yarat:
```python
test_company_id = "test_e2e_001"
test_phone = "0532 123 45 67"
test_email = "test@example.com"
# INSERT companies (primary_phone, primary_email vs.)
```

### 2. Strict Mode → Lenient Mode Geçişi

```python
# Step 1: Strict mod (default)
response1 = client.get(f"/api/company/{test_company_id}?mask=0")
assert response1["primary_phone"] != "0532 123 45 67"  # Maskeli
assert response1["primary_email"] != "test@example.com"  # Maskeli

# Step 2: Admin lenient mod'a değiştir
admin_response = client.post(
    "/api/admin/kvkk-mode",
    json={"mode": "lenient", "reason": "E2E test"}
)
assert admin_response["new_mode"] == "lenient"

# Step 3: Lenient mod
response2 = client.get(f"/api/company/{test_company_id}?mask=1")
assert response2["primary_phone"] == "0532 123 45 67"  # Açık
assert response2["primary_email"] == "test@example.com"  # Açık
```

### 3. Lenient → Strict Geri Dön

```python
# Admin strict'e geri değiştir
admin_response = client.post(
    "/api/admin/kvkk-mode",
    json={"mode": "strict", "reason": "E2E test cleanup"}
)
assert admin_response["new_mode"] == "strict"

# Kontrol: phone/email yine maskeli
response3 = client.get(f"/api/company/{test_company_id}?mask=0")
assert response3["primary_phone"] != "0532 123 45 67"
```

---

## Kabul Kriteri

- [x] Admin /api/admin/kvkk-mode strict→lenient geçişi başarılı
- [x] /api/company/{id} strict mode: phone/email maskeli
- [x] /api/company/{id} lenient mode: phone/email açık
- [x] Lenient→strict geri dönüş başarılı
- [x] pytest test pass

---

## Komut

```bash
cd Huginn\ Data\ Insights
pytest tests/test_admin_kvkk_mode_e2e.py -v
```

---

## İlgili Nodlar

- [[Huginn Data Insights/web_app.py#2734-2810|/api/admin/kvkk-mode endpoint]]
- [[Huginn Data Insights/web_app.py#2824-2862|/api/company/{id} endpoint]]
