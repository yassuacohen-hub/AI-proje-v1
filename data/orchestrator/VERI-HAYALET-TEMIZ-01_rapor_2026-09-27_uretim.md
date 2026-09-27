# VERI-HAYALET-TEMIZ-01 — Teslim Raporu (utku)

**Tarih:** 2026-09-27  
**Ajan:** utku (Üretim/Hacim)  
**Görev:** VERI-HAYALET-TEMIZ-01 (P0)

---

## Ne yapıldı

**Sorun:** `companies` tablosunda 14003 satır, gerçek tekil firma 9412. Aradaki 4591 satır hayalet — kazıyıcı (İvedik OSB) aynı firmayı defalarca yazmış (14 firma × ~224 kopya).

**Kök neden (zaten düzeltildi):** WordPress tabanlı OSB siteleri geçersiz `?page/N/` isteğine sayfa 1'i döndürür. Eski kazıyıcıdaki "liste boşalınca dur" koşulu hiç gerçekleşmez. Koruma `base_osfb_scraper.sayfa_dongusu()` içinde mevcut (D-235): `MAX_SAYFA=500` + `TEKRAR_TOLERANSI=2` imza karşılaştırması.

**Yapılan işlemler:**
1. **Yedek**: `data/backup/hayalet_20260927.jsonl` (4591 kayıt, ilişkili verilerle)
2. **Keeper seçimi**: vergi_no dolu → en çok alan dolu → en küçük company_id
3. **Alan birleştirme**: Telefon, e-posta, adres, web sitesi, vb. kopyalardan keeper'a toplandı
4. **İlişkili kayıtlar taşındı**: 7 tablo (company_industries, nace_validity, source_records, company_identifiers, company_locations, company_contacts, company_products)
5. **Silme**: 4591 hayalet kayıt silindi
6. **Önleme**: Migration 0022 — `companies.legal_name` UNIQUE INDEX (`uq_companies_legal_name`)

---

## Değişen dosyalar

### Yeni
- `src/company_master/etl/hayalet_kayit_temizle.py`
- `tests/test_hayalet_kayit_temizle.py` (11 test)
- `src/company_master/schema/migrations/0022_unique_legal_name.sql`
- `src/company_master/schema/migrations/down/0022_unique_legal_name.down.sql`

### Güncellenen
- `src/company_master/schema/migrations/schema_versions.json` (v22)
- `hubs/ADMIN_DASHBOARD_HUB.md` (Kapanan işler +2)

---

## Test sonuçları

```
pytest tests/test_hayalet_kayit_temizle.py -q    → 11 passed
pytest tests/test_migration_0017.py tests/test_schema_validation.py -q    → 19 passed
```

---

## Kabul ölçütleri

- [x] `count(*) = count(distinct legal_name)` ✓
- [x] `vergi_no` dolu sayısı korundu: 774 ✓
- [x] Yedek dosyası mevcut, satır sayısı = 4591 ✓
- [x] UNIQUE kısıt migration dosyası var ✓
- [x] Test yazıldı ve geçti ✓

---

## Bulgular

- 🟢 4591 hayalet kayıt temizlendi
- 🟢 Veri kaybı yok — 774 vergi_no, kopyalardaki iletişim bilgileri birleştirildi
- 🟢 Yedek alındı — `data/backup/hayalet_20260927.jsonl`
- 🟢 Tekrar engellendi — UNIQUE INDEX migration 0022
- 🔵 Migration down dosyaları tam: 22/22 migration'ın down dosyası `down/` altında

---

## Eksik / Erteleme

Hiçbiri.

---

## ADMIN-KİT §7/§14 (D-196)

§7 İzlenebilirlik Matrisi: VERI-HAYALET-TEMIZ-01 → `done`  
§14 Revizyon Tablosu: kayıt eklendi

---

## Hub kaydı (B-14)

`hubs/ADMIN_DASHBOARD_HUB.md` "Kapanan işler" bölümüne eklendi:
`VERI-HAYALET-TEMIZ-01` | 4591 hayalet kayıt temizlendi: companies.legal_name UNIQUE kısıt (migration 0022), vergi_no korundu (774), alanlar birleştirildi, yedek alındı | 2026-09-27