# API-KVKK-KONTROL-25 — Kontör Endpoint Entegrasyonu

**Task ID:** API-KVKK-KONTROL-25  
**Sahip:** Yasu  
**Öncelik:** P1  
**Durum:** bekliyor  
**Dependency:** ALTYAPI-VERI-GORUNURLUK-01 (tamamlandı)

---

## Amaç

/api/match ve /api/ilan endpoints'te `_charge_module_credit()` fonksiyonu çağrısını entegre et. Modül maliyetini `module_cost` tablosundan dinamik olarak oku.

---

## Doğrulanacak Varsayım

- module_cost tablosu 0018 migration ile oluşturuldu (terminal/strategic/enterprise tier × 5 modul)
- _charge_module_credit(user_id, tier, module) fonksiyonu web_app.py:1388-1422'de yazılı
- /api/match ve /api/ilan endpoints'te tier parametresi var
- Kontör düşme sırası: query başında (authorization check sonrası)

---

## Adımlar

### 1. /api/match Endpoint'te Kontör Düşme

**Dosya:** web_app.py  
**Satır:** ~1145 (api_match fonksiyonu başı)

```python
@app.get("/api/match")
def api_match(...):
    # ... validasyon, tier kontrol ...
    
    # Kontör düş
    balance = _charge_module_credit(user_id, tier, "match")
    if balance < 0:  # Serbest (enterprise)
        pass
    elif balance == 0:  # Hata (kontör yetersiz)
        raise HTTPException(status_code=402, detail="Kontör yetersiz")
    
    # ... sorgu devam ...
```

### 2. /api/ilan Endpoint'te Kontör Düşme

Benzer mantık, module="ilan"

### 3. Kontrol

- Terminal: match=10 kredi, ilan=0 (kapalı)
- Strategic: match=5 kredi, ilan=3 kredi
- Enterprise: kontör serbest (balance=-1)

---

## Kabul Kriteri

- [x] /api/match'te _charge_module_credit(..., "match") çağrısı
- [x] /api/ilan'da _charge_module_credit(..., "ilan") çağrısı
- [x] Terminal tier: match=10 kredi düş (kontrol)
- [x] Strategic tier: match=5, ilan=3 kredi düş (kontrol)
- [x] Enterprise: kontör serbest (balance=-1 döner, sorgu devam)
- [x] Kontör yetersizse 402 Payment Required cevap

---

## Kurallar (ADMIN-KİT · D-206)

- Modül maliyeti **module_cost tablosundan** okunacak (hardcode yok)
- Kontör ledger otomatik kaydedilecek (_charge_credit ile)
- Audit trail: kontör_ledger tablosu (user_id, module, tier, cost, balance, ts)

---

## İlgili Nodlar

- [[Huginn Data Insights/web_app.py#1388-1422|_charge_module_credit()]]
- [[Huginn Data Insights/web_app.py#1131-1269|/api/match endpoint]]
- [[Huginn Data Insights/src/company_master/schema/migrations/0018_visibility_layer.sql|module_cost tablo]]
- [[Huginn Data Insights/AGENTS.md|D-206 kararı]]
