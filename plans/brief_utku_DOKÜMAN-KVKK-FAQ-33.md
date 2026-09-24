# DOKÜMAN-KVKK-FAQ-33 — KVKK FAQ & Troubleshooting

**Task ID:** DOKÜMAN-KVKK-FAQ-33  
**Sahip:** Utku  
**Öncelik:** P2  
**Dependency:** ALTYAPI-VERI-GORUNURLUK-01

---

## Amaç

Yeni dosya `docs/KVKK_FAQ.md`. SSS: Field neden maskeli? Strict vs Lenient fark? Quarantine nedir? Kontör eksikse? Örnekler + çözüm.

---

## İçerik Bölümleri

### 1. Giriş
- KVKK maskeleme SSS
- Tier-based görünürlük
- Admin control seçenekleri

### 2. Sık Sorulan Sorular

#### Q1: Field neden maskeli?
**A:** KVKK sınıflandırması. 33 field × 4 class (açık/yarı-açık/kısıtlı/yasak). Örnek:
- legal_name (açık) → görülür
- primary_phone (kısıtlı) → strict=053***67, lenient=açık
- quarantine_reason (yasak) → hep maskeli

#### Q2: Strict vs Lenient mod fark?
**A:** 
- Strict: KVKK mutlak. Kısıtlı alanlar maskeli.
- Lenient: Admin riski kabul etti. Kısıtlı açık. Yasak hala maskeli.

#### Q3: Quarantine flag nedir?
**A:** Veri silme yerine karantina. Çelişki çözümü (Ç1-Ç4):
- Ç1: GSM silme vs take-all → quarantine_reason="ç1_telefon"
- Ç2: Email domain çelişkisi → quarantine_reason="ç2_email"
- Ç3: Kişi adı → quarantine_reason="ç3_isim"
- Ç4: WhatsApp → quarantine_reason="ç4_whatsapp"

#### Q4: Tier upgrade sonra alanlar değişir mi?
**A:** Evet. plan_field_group tablosundan tier-bazında görünürlük yüklenir:
- Terminal → Strategic: iletişim=kısıtlı → yarı-açık
- Strategic → Enterprise: hepsi açık

#### Q5: Kontör eksikse ne olur?
**A:** 402 Payment Required. Tier'in kontör limiti aşıldı. Credit Pack satın al ya da tier upgrade yap.

#### Q6: Maskeleme log var mı?
**A:** Evet. admin_kvkk_mode tablosunda mode geçişleri kaydedilir. /api/admin/kvkk-mode endpoint'te sebep (reason) mandatory.

#### Q7: API query'de mask parameter?
**A:** Evet. /api/company/{id}?mask=1 → lenient mod (kısıtlı açık). Default mask=0 → strict.

### 3. Troubleshooting

#### Sorun: "Kontör yetersiz" hatası
**Çözüm:**
```
1. /api/buyer/ledger'den kontör durumu kontrol et
2. Tier'i kontrol et (terminal=düşük kontör)
3. Credit Pack satın al (web_app.py /api/admin/credit endpoint)
4. Strategic → Enterprise upgrade yap
```

#### Sorun: Admin mode toggle çalışmıyor
**Çözüm:**
```
1. Admin authorization kontrol et (Bearer token?)
2. /api/admin/kvkk-mode endpoint'te reason min 3 char
3. DB'de admin_kvkk_mode tablosu var mı? (0018 migration)
```

#### Sorun: Field hala maskeli lenient mod'da
**Çözüm:**
```
1. Layer 1 sınıflandırması: yasak alanlar hep maskeli
2. Quarantine_reason check (Ç1-Ç4 bayrak?)
3. is_sahis flag kontrol (karantina durumu)
```

### 4. Kod Örnekleri

**Örnek 1: Terminal User - Match Query**
```bash
curl -X GET "http://localhost/api/match?q=ABC&limit=10" \
  -H "X-API-Key: user_terminal_key"

# Cevap: legal_name açık, primary_phone=053***67 (maskeli)
# Kontör: 10 kredi düş (terminal/match=10)
```

**Örnek 2: Admin Lenient Mode**
```bash
curl -X POST "http://localhost/api/admin/kvkk-mode" \
  -H "Authorization: Bearer admin_token" \
  -d '{"mode":"lenient","reason":"Audit request for special case"}'

# Cevap: {ok: true, previous_mode: "strict", new_mode: "lenient"}
# Sonra /api/company/{id}?mask=1 → primary_phone açık
```

**Örnek 3: Quarantine Check**
```sql
SELECT company_id, primary_phone, quarantine_reason, is_sahis
FROM companies
WHERE quarantine_reason IS NOT NULL;

-- Ç1 telefon silme çelişkisi
-- is_sahis=1 bireysel veri işareti
```

---

## Kabul Kriteri

- [x] docs/KVKK_FAQ.md oluşturuldu
- [x] 7 SSS (field, strict/lenient, quarantine, tier, kontör, log, mask param)
- [x] 3+ troubleshooting senaryosu
- [x] 3 kod örneği (curl/SQL)
- [x] Linkler doğru (API endpoints, tablolar)

---

## İlgili Nodlar

- [[Huginn Data Insights/src/company_master/api/core/normalize.py#27-82|_KVKK_FIELD_CLASS]]
- [[Huginn Data Insights/web_app.py#2734-2810|/api/admin/kvkk-mode endpoint]]
- [[Huginn Data Insights/src/company_master/schema/migrations/0018_visibility_layer.sql|admin_kvkk_mode tablo]]
