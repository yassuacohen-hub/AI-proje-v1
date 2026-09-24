# VISIBILITY_LAYER_GUIDE — Görünürlük Katmanı Kullanım Kılavuzu

> **Task:** DOC-VISIBILITY-KATMANI-29  
> **Tarih:** 2026-09-25  
> **SSOT:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani` (D-200/D-208)  
> **Hub:** `hubs/ADMIN_DASHBOARD_HUB.md`

---

## 1. Layer 1 & 2 Mimarisi

### Layer 1 — KVKK Sabit (Kullanıcı Kapatamaz)

| Sınıf | Açıklama | Örnek Alanlar | Müşteri Görür mü? |
|-------|----------|---------------|-------------------|
| **Açık** | Kamu verisi, KVKK kapsam dışı | `legal_name`, `trade_name`, `nace_kodu`, `il`, `ilce` | ✅ Her zaman |
| **Yarı-Açık** | Ticari bilgi, bazı durumlarda hassas | `web_site`, `sektor`, `yil`, `calisan_sayisi` | ⚠️ Sadece pakete göre |
| **Kısıtlı** | KVKK özel veri (KVKK md. 6) | `primary_phone`, `primary_email`, `yetkili_kisi`, `adres` | 🔒 Tier'e göre (Strict/Lenient) |
| **Yasak** | KVKK özel veri + karantina | `tc_kimlik_no`, `vergi_no`, `quarantine_reason` | ❌ Hiçbir zaman |

**Kural (D-202):** Müşteri gizlemeyi **kapatamaz**. `?mask=0` parametresi **kaldırıldı**. Parametre sadece sıkılaştırır (`mask=1` → lenient, `mask=0` → strict).

### Layer 2 — Admin Kontrol (Strict ↔ Lenient)

| Mod | Kısıtlı Alanlar | Yasak Alanlar | Audit |
|-----|-----------------|---------------|-------|
| **Strict (varsayılan)** | Maskeli (`053***67`) | Maskeli | — |
| **Lenient (admin)** | Açık (`0532 555 12 34`) | Maskeli | Zorunlu (`admin_kvkk_mode` tablosuna yazılır) |

**Kural (D-201):** Lenient sadece admin, audit zorunlu. `admin_kvkk_mode` tablosuna her değişiklik yazılır (who/when/old/new/reason).

---

## 2. Admin KVKK Mode

### API: `/api/admin/kvkk-mode`

| Metot | Açıklama |
|-------|----------|
| `GET` | Mevcut mod + son değişim bilgisi |
| `POST` | Mod değiştir: `{ "mode": "strict|lenient", "reason": "..." }` |

**Zorunlu alanlar:**
- `mode`: `strict` veya `lenient`
- `reason`: min 3 karakter (audit için)

**Yanıt:**
```json
{
  "ok": true,
  "previous_mode": "strict",
  "new_mode": "lenient",
  "changed_at": "2026-09-25T10:30:00Z",
  "changed_by": "admin@huginn.local"
}
```

### Admin Panel Sekmesi: KVKK Mode

- Mevcut mod göstergesi (Strict/Lenient badge)
- Radio button: Strict / Lenient
- Reason textarea (min 3 karakter)
- Submit butonu → POST `/api/admin/kvkk-mode`
- Success/error feedback toast

---

## 3. Modül Kontör Matrisi

### Modül Tanımları

| Modül ID | Modül Adı | Açıklama | Maliyet Birimi |
|----------|-----------|----------|----------------|
| `match` | Firma Eşleştirme | Arama + detay getirme | 10 kredi/istek |
| `detail` | Firma Detayı | Tek firma detay görüntüleme | 5 kredi/istek |
| `analyze` | Analiz/Rapor | Segmentasyon, LTV, CAC | 20 kredi/rapor |
| `export` | Dışa Aktarma | CSV/Excel indirme | 1 kredi/satır |
| `osint` | OSINT Kazıma | Web veri toplama | 0 kredi (kontörsüz) |

### Tier Kontör Limitleri (Aylık)

| Tier | Aylık Kontör | Modül Erişimi |
|------|--------------|---------------|
| **Terminal** | 100 | `match`, `detail` |
| **Strategic** | 500 | `match`, `detail`, `analyze` |
| **Enterprise** | Sınırsız (`-1`) | Tüm modüller + `export`, `osint` |

**Kontör Düşümü (D-204):** Grup + firma başına 1 düşüm. `/api/buyer/reveal?company_id=X&group=Y` ile kontör düşer.

---

## 4. Çelişki Çözümleri (Ç1-Ç4 Karantina)

Veri **asla silinmez** (D-208). Çelişki varsa **karantina** (`quarantine_reason` + `is_sahis` bayrakları) ile çözülür.

| Kod | Çelişki | Açıklama | Karantina Reason | Çözüm |
|-----|---------|----------|------------------|-------|
| **Ç1** | GSM Silme vs Take-All | Müşteri telefon silmek ister ama take-all paketi tüm veriyi çeker | `c1_telefon` | Telefon karantinaya alınır, take-all'da maskelenir |
| **Ç2** | E-posta Domain Çelişkisi | Farklı kaynaklardan farklı domain geliyor | `c2_email` | Domain karantinaya alınır, manuel doğrulama beklenir |
| **Ç3** | Kişi Adı | Farklı kaynaklardan farklı isim geliyor | `c3_isim` | İsim karantinaya alınır, en güncel kaynak tercih edilir |
| **Ç4** | WhatsApp | WhatsApp numarası vs GSM çelişkisi | `c4_whatsapp` | WhatsApp karantinaya alınır, GSM öncelikli |

**Karantina Bayrakları:**
- `quarantine_reason`: `c1_telefon` | `c2_email` | `c3_isim` | `c4_whatsapp` (birden fazla olabilir, virgülle ayrılır)
- `is_sahis`: `true` = bireysel veri (KVKK md. 6 kapsamında), `false` = kurumsal

---

## 5. Senaryo Örnekleri

### Senaryo 1: Terminal Müşteri - Match Query

```bash
curl -X GET "http://localhost:8000/api/match?q=ABC&limit=10" \
  -H "X-API-Key: user_terminal_key"
```

**Cevap:**
```json
{
  "results": [
    {
      "legal_name": "ABC TEKSTİL SANAYİ VE TİCARET A.Ş.",
      "primary_phone": "053***67",        # Strict → maskeli
      "primary_email": "info***@abc.com",  # Strict → maskeli
      "nace_kodu": "13.92",                # Açık
      "il": "İSTANBUL"                     # Açık
    }
  ],
  "meta": {
    "credit_used": 10,
    "credit_remaining": 90,
    "tier": "terminal"
  }
}
```

---

### Senaryo 2: Admin Lenient Mode

```bash
# 1. Admin lenient mode'a geçir
curl -X POST "http://localhost:8000/api/admin/kvkk-mode" \
  -H "Authorization: Bearer admin_token" \
  -d '{"mode":"lenient","reason":"Audit request for special case"}'

# Cevap:
{"ok": true, "previous_mode": "strict", "new_mode": "lenient", "changed_at": "..."}

# 2. Müşteri lenient modda veri çeker
curl -X GET "http://localhost:8000/api/match?q=ABC&limit=10&mask=1" \
  -H "X-API-Key: user_terminal_key"
```

**Cevap (mask=1, lenient mod aktif):**
```json
{
  "results": [
    {
      "legal_name": "ABC TEKSTİL SANAYİ VE TİCARET A.Ş.",
      "primary_phone": "0532 555 12 34",   # Lenient → açık!
      "primary_email": "info@abc.com",       # Lenient → açık!
      "nace_kodu": "13.92",
      "il": "İSTANBUL"
    }
  ]
}
```

---

### Senaryo 3: Kontör Düşümü - Reveal Endpoint

```bash
# Grup bazlı detay görünürlük (kontör düşer)
curl -X GET "http://localhost:8000/api/buyer/reveal?company_id=123&group=iletisim" \
  -H "X-API-Key: user_strategic_key"
```

**Cevap:**
```json
{
  "company_id": 123,
  "group": "iletisim",
  "fields": {
    "primary_phone": "0532 555 12 34",
    "primary_email": "info@abc.com",
    "yetkili_kisi": "AHMET YILMAZ",
    "adres": "MASLAK MAH. BUYUKDERE CAD. NO:123"
  },
  "meta": {
    "credit_used": 1,
    "credit_remaining": 499,
    "tier": "strategic"
  }
}
```

---

### Senaryo 4: OSINT Paketi (Kontörsüz)

```bash
curl -X GET "http://localhost:8000/api/osint/scrape?domain=example.com" \
  -H "X-API-Key: user_enterprise_key"
```

**Cevap:**
```json
{
  "domain": "example.com",
  "emails": ["info@example.com", "contact@example.com"],
  "phones": ["+90 212 555 12 34"],
  "social": {"linkedin": "https://linkedin.com/company/example"},
  "meta": {
    "credit_used": 0,
    "note": "OSINT paketi kontörsüz (plan=osint)"
  }
}
```

---

### Senaryo 5: Karantina Çözümü (Ç1)

```sql
-- Ç1: Telefon silme çelişkisi
SELECT company_id, primary_phone, quarantine_reason, is_sahis
FROM companies
WHERE quarantine_reason LIKE '%c1_telefon%';

-- Sonuç:
-- company_id | primary_phone | quarantine_reason | is_sahis
-- 12345      | 05325551234   | c1_telefon        | true
-- 12346      | 05336667788   | c1_telefon,c2_email | false
```

**Admin Panel'de:** Karantina kayıtları "Veri Kalitesi" sekmesinde listelenir, manuel onay/red bekler.

---

## 6. Admin Panel Sekmeleri

| Sekme | Fonksiyon | Açıklama |
|-------|-----------|----------|
| **KVKK Mode** | `render_kvkk_mode_tab` | Strict/Lenient toggle + reason |
| **KVKK Raporu** | `render_kvkk_rapor_tab` | Geçmiş + KPI + trend |
| **Kontrol Panosu** | `render_kontrol_panosu_tab` | KPI + bar/line chart + mode geçişleri |

---

## 7. Veritabanı Şeması (Özet)

### `admin_kvkk_mode` (D-205)
```sql
CREATE TABLE admin_kvkk_mode (
    id BIGSERIAL PRIMARY KEY,
    admin_id UUID REFERENCES users(user_id),
    mode VARCHAR(10) CHECK (mode IN ('strict','lenient')),
    reason TEXT NOT NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    effective_to TIMESTAMPTZ  -- NULL = süresiz
);
```

### `user_activity_log` (Aktivite Log)
```sql
CREATE TABLE user_activity_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    olay_tipi VARCHAR(20) CHECK (olay_tipi IN ('giris','arama','ai_kullanim','export','kvkk_mode')),
    olay_zamani TIMESTAMPTZ DEFAULT NOW(),
    detay JSONB,
    basarili BOOLEAN DEFAULT TRUE,
    ip_adresi INET,
    ulke_kodu CHAR(2)
);
```

### `plan_field_group` (D-203)
```sql
-- 6 grup × 3 paket = 18 satır
-- grup: kimlik, iletisim, lokasyon, dijital, ticari, sınai
-- paket: terminal, strategic, enterprise
-- visible: boolean (admin panelinde aç/kapa)
```

---

## 8. Test Senaryoları

| Test Dosyası | Açıklama |
|--------------|----------|
| `test_visibility_senaryo_1-5.py` | 5 senaryo E2E test |
| `test_kvkk_katman_iki.py` | Layer 1 sabit, Layer 2 kırılabilir |
| `test_module_cost.py` | Modül/tier/kontör doğrulama |
| `test_kvkk_katman_iki.py` | Layer 1 sabit, Layer 2 kırılabilir |

---

## 9. İlgili Nodlar

- [[Huginn Data Insights/src/company_master/api/core/normalize.py|normalize.py (apply_plan)]]
- [[Huginn Data Insights/web_app.py|web_app.py (4 çağrı noktası + /api/buyer/reveal)]]
- [[Huginn Data Insights/web_dashboard/tabs/admin_panel.py|admin_panel.py (3 yeni sekme)]]
- [[Huginn Data Insights/src/company_master/schema/migrations/0018_visibility_layer.sql|0018_visibility_layer.sql]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB|ADMIN_DASHBOARD_HUB]]

---

> **Not:** Bu doküman `docs/VISIBILITY_LAYER_GUIDE.md` olarak kaydedilir. Güncellemeler SSOT (ADMIN-KİT) ile senkronize edilir.