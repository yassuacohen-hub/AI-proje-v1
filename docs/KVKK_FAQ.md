# KVKK FAQ & Troubleshooting

> **Task:** DOKUMAN-KVKK-FAQ-33  
> **Tarih:** 2026-09-25  
> **SSOT:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani` (D-200/D-208)  
> **Hub:** `hubs/ADMIN_DASHBOARD_HUB.md`

---

## 1. Giriş

Bu doküman Huginn Company Master sistemindeki KVKK (Kişisel Verilerin Korunması Kanunu) maskeleme mantığını, admin kontrol seçeneklerini ve sık karşılaşılan sorunların çözümlerini açıklar.

### Kapsam
- **KVKK Sınıflandırması:** 33 field × 4 sınıf (açık/yarı-açık/kısıtlı/yasak)
- **Tier-based Görünürlük:** Terminal/Strategic/Enterprise paketlere göre farklı görünürlük
- **Admin Kontrol:** Strict (varsayılan) ↔ Lenient (admin onayıyla) mod geçişi
- **Karantina Mekanizması:** Ç1-Ç4 çelişki çözümleri

---

## 2. Sık Sorulan Sorular

### Q1: Field neden maskeli?

**A:** KVKK sınıflandırmasına göre. 33 field × 4 sınıf:

| Sınıf | Açıklama | Örnek | Müşteri Görür mü? |
|-------|----------|-------|-------------------|
| **Açık** | Kamu verisi, KVKK kapsam dışı | `legal_name`, `trade_name`, `nace_kodu`, `il`, `ilce` | ✅ Her zaman |
| **Yarı-Açık** | Ticari bilgi, bazı durumlarda hassas | `web_site`, `sektor`, `yil`, `calisan_sayisi` | ⚠️ Pakete göre |
| **Kısıtlı** | KVKK özel veri (KVKK md. 6) | `primary_phone`, `primary_email`, `yetkili_kisi`, `adres` | 🔒 Tier'e göre |
| **Yasak** | KVKK özel veri + karantina | `tc_kimlik_no`, `vergi_no`, `quarantine_reason` | ❌ Hiçbir zaman |

**Örnek:**
- `legal_name` (açık) → `"ARITES METAL SANAYI VE TİCARET A.Ş."` ✅
- `primary_phone` (kısıtlı) → Strict: `"053***67"`, Lenient: `"0532 555 12 34"` 🔒
- `quarantine_reason` (yasak) → Her zaman maskeli ❌

**Kaynak:** `src/company_master/api/core/normalize.py` → `_KVKK_FIELD_CLASS` (satır 27-82)

---

### Q2: Strict vs Lenient mod fark?

| Mod | Kısıtlı Alanlar | Yasak Alanlar | Kullanım |
|-----|-----------------|---------------|----------|
| **Strict (varsayılan)** | Maskeli (`053***67`) | Maskeli | Tüm müşteriler, API varsayılan |
| **Lenient (admin)** | Açık (`0532 555 12 34`) | Maskeli | Sadece admin, audit zorunlu |

**Farklar:**
- **Strict:** KVKK mutlak koruma. Kısıtlı alanlar her zaman maskeli.
- **Lenient:** Admin riski üstlenir. Kısıtlı alanlar açılır. Yasak alanlar **hala maskeli**.

**Admin Panel:** KVKK Mode sekmesinde `strict` ↔ `lenient` toggle. `reason` (min 3 karakter) zorunlu. Her değişiklik `admin_kvkk_mode` tablosuna yazılır (D-205).

**API:** `GET/POST /api/admin/kvkk-mode` — `web_app.py` satır 2734-2810.

---

### Q3: Quarantine flag nedir?

Veri **asla silinmez** (D-208). Çelişki varsa **karantina** (`quarantine_reason` + `is_sahis` bayrakları) ile çözülür.

| Kod | Çelişki | Açıklama | `quarantine_reason` | `is_sahis` |
|-----|---------|----------|---------------------|------------|
| **Ç1** | GSM Silme vs Take-All | Müşteri telefon silmek ister ama take-all paketi tüm veriyi çeker | `c1_telefon` | `true` (bireysel) |
| **Ç2** | E-posta Domain Çelişkisi | Farklı kaynaklardan farklı domain geliyor | `c2_email` | `true/false` |
| **Ç3** | Kişi Adı | Farklı kaynaklardan farklı isim geliyor | `c3_isim` | `true` (bireysel) |
| **Ç4** | WhatsApp | WhatsApp numarası vs GSM çelişkisi | `c4_whatsapp` | `true/false` |

**Karantina Bayrakları:**
- `quarantine_reason`: `c1_telefon` | `c2_email` | `c3_isim` | `c4_whatsapp` (birden fazla olabilir, virgülle ayrılır)
- `is_sahis`: `true` = bireysel veri (KVKK md. 6 kapsamında), `false` = kurumsal

**Kaynak:** `src/company_master/schema/migrations/0018_visibility_layer.sql` → `companies` tablosu ALTER.

---

### Q4: Tier upgrade sonrası alanlar değişir mi?

**Evet.** `plan_field_group` tablosundan tier-bazında görünürlük yüklenir (D-203):

| Grup | Terminal | Strategic | Enterprise |
|------|----------|-----------|------------|
| **kimlik** | Açık | Açık | Açık |
| **iletisim** | Kısıtlı (Strict) | Yarı-Açık | Açık (Lenient) |
| **lokasyon** | Yarı-Açık | Yarı-Açık | Açık |
| **dijital** | Kısıtlı | Yarı-Açık | Açık |
| **ticari** | Açık | Açık | Açık |
| **sınai** | Açık | Açık | Açık |

**Örnek:**
- Terminal → Strategic: `iletisim` = kısıtlı → yarı-açık
- Strategic → Enterprise: hepsi açık

**Admin Panel:** "Veri Kalitesi" sekmesinde `plan_field_group` matrisi görüntülenebilir/ayarlanır.

---

### Q5: Kontör eksikse ne olur?

**402 Payment Required.** Tier'in kontör limiti aşıldı.

**Çözüm:**
```bash
# 1. Kontör durumu kontrol et
curl -X GET "http://localhost:8000/api/buyer/ledger" -H "X-API-Key: user_key"

# 2. Tier kontrol et (terminal=düşük kontör)
# Terminal: 100 kredi/ay, Strategic: 500, Enterprise: sınırsız

# 3. Credit Pack satın al
curl -X POST "http://localhost:8000/api/admin/credit" \
  -H "Authorization: Bearer admin_token" \
  -d '{"user_id": "...", "amount": 1000}'

# 4. Veya Tier upgrade yap
curl -X POST "http://localhost:8000/api/admin/tier" \
  -H "Authorization: Bearer admin_token" \
  -d '{"user_id": "...", "new_tier": "strategic"}'
```

**Kontör Düşümü (D-204):** Grup + firma başına 1 düşüm. `/api/buyer/reveal?company_id=X&group=Y` ile kontör düşer.

---

### Q6: Maskeleme log var mı?

**Evet.** `admin_kvkk_mode` tablosunda mode geçişleri kaydedilir (D-205).

**Endpoint:** `/api/admin/kvkk-mode` (GET/POST) — `web_app.py` satır 2734-2810.

**Log Alanları:** `admin_id`, `mode` (strict/lenient), `reason`, `changed_at`, `effective_to`.

**Query Param:** `mask=1` → lenient mod (kısıtlı açık). Default `mask=0` → strict.

---

### Q7: API query'de mask parameter?

**Evet.** `/api/company/{id}?mask=1` → lenient mod (kısıtlı açık). Default `mask=0` → strict.

**Örnek:**
```bash
# Strict (varsayılan)
curl "http://localhost:8000/api/company/123" -H "X-API-Key: key"
# primary_phone: "053***67"

# Lenient (admin mode + mask=1)
curl "http://localhost:8000/api/company/123?mask=1" -H "X-API-Key: key"
# primary_phone: "0532 555 12 34" (sadece admin lenient moddaysa)
```

---

## 3. Troubleshooting

### Sorun: "Kontör yetersiz" hatası (402)

**Çözüm:**
```bash
1. /api/buyer/ledger'den kontör durumu kontrol et
2. Tier'i kontrol et (terminal=düşük kontör)
3. Credit Pack satın al (web_app.py /api/admin/credit endpoint)
4. Strategic → Enterprise upgrade yap
```

### Sorun: Admin mode toggle çalışmıyor

**Çözüm:**
```bash
1. Admin authorization kontrol et (Bearer token?)
2. /api/admin/kvkk-mode endpoint'te reason min 3 char
3. DB'de admin_kvkk_mode tablosu var mı? (0018 migration)
```

### Sorun: Field hala maskeli lenient mod'da

**Çözüm:**
```bash
1. Layer 1 sınıflandırması: yasak alanlar hep maskeli
2. Quarantine_reason check (Ç1-Ç4 bayrak?)
3. is_sahis flag kontrol (karantina durumu)
```

---

## 4. Kod Örnekleri

### Örnek 1: Terminal User - Match Query

```bash
curl -X GET "http://localhost:8000/api/match?q=ABC&limit=10" \
  -H "X-API-Key: user_terminal_key"

# Cevap:
# legal_name açık, primary_phone=053***67 (maskeli)
# Kontör: 10 kredi düş (terminal/match=10)
```

### Örnek 2: Admin Lenient Mode

```bash
curl -X POST "http://localhost:8000/api/admin/kvkk-mode" \
  -H "Authorization: Bearer admin_token" \
  -d '{"mode":"lenient","reason":"Audit request for special case"}'

# Cevap: {ok: true, previous_mode: "strict", new_mode: "lenient"}

# Sonra /api/company/{id}?mask=1 → primary_phone açık
```

### Örnek 3: Karantina Check

```sql
SELECT company_id, primary_phone, quarantine_reason, is_sahis
FROM companies
WHERE quarantine_reason IS NOT NULL;

-- Ç1 telefon silme çelişkisi
-- is_sahis=1 bireysel veri işareti
```

---

## 5. İlgili Nodlar

- [[Huginn Data Insights/src/company_master/api/core/normalize.py|normalize.py (L27-82: _KVKK_FIELD_CLASS)]]
- [[Huginn Data Insights/web_app.py|web_app.py (L2734-2810: /api/admin/kvkk-mode endpoint)]]
- [[Huginn Data Insights/src/company_master/schema/migrations/0018_visibility_layer.sql|0018_visibility_layer.sql (admin_kvkk_mode tablo)]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB|ADMIN_DASHBOARD_HUB]]

---

> **Not:** Bu doküman `docs/KVKK_FAQ.md` olarak kaydedilir. Güncellemeler SSOT (ADMIN-KİT) ile senkronize edilir.