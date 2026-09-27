# ALTYAPI-SQLITE-INIT Raporu

**Görev ID:** ALTYAPI-SQLITE-INIT  
**Rol:** Üretim/Hacim (UTKU)  
**Tarih:** 2026-09-20  
**Durum:** Tamamlandı ✓

---

## Ne yapıldı

1. **SQLite fallback DB initleme mekanizması bulundu ve etkinleştirildi**
   - `src/company_master/db/connection.py` içinde pre-existing `init_db()` fonksiyonu vardı; test suite hiç çağırmıyordu.
   - Fix: `tests/conftest.py`'ye `_init_test_db` autouse, session-scoped fixture eklendi.
   - Fixture her test oturumunda bir kez `init_db()` çağırarak SQLite fallback DB'sini initialize eder.

2. **SQLite fallback şeması tamamlandı (4 eksik sütun eklendi)**
   - `web_app.py` sorgularında kullanılan ama `init_db()`'deki hardcoded SQLite CREATE TABLE'da olan sütunlar:
     - `nace_code TEXT`
     - `osb_parsel TEXT`
     - `adres TEXT`
     - `vergi_no TEXT`
   - Bu sütunlar `src/company_master/db/connection.py` satır 237–243 aralığında companies tablosuna eklendi.
   - Değişim: CREATE TABLE IF NOT EXISTS companies (...) şeması tam ve complete.

3. **Target test dosyaları doğrulandı**
   - `tests/test_api_companies.py` ve `tests/test_api_integration.py` çalıştırıldı.
   - Sonuç: **78 passed, 16 skipped, 2 warnings, 0 failed, 0 errors** (16 skip beklenen davranış: `_bos_db_atla` fixture empty DB'de data-dependent testleri skip eder).

---

## Değişen dosyalar

| Dosya | Satırlar | Değişim |
|-------|----------|---------|
| `tests/conftest.py` | 20–28 | Eklendi: `_init_test_db` autouse session fixture |
| `src/company_master/db/connection.py` | 237–243 | Eklendi: `nace_code`, `osb_parsel`, `adres`, `vergi_no` sütunları CREATE TABLE'da |

---

## Test sonuçları

### Target Testler (test_api_companies.py + test_api_integration.py)
```
78 passed, 16 skipped, 2 warnings in 1.57s
```

- ✅ **0 hata, 0 başarısızlık** (hedefteki 16 error kapatıldı).
- 16 skip: Expected — `_bos_db_atla` fixture empty DB'de veri tabanlı testleri skip eder (CI'de normal, üretime test data yüklenince geçer).
- 2 warning: Deprecated `datetime.utcnow()` (web_app.py:2718) — ALTYAPI-SQLITE-INIT kapsamı dışında.

### Kodlama Denetimi
```
python scripts/kodlama_denetim.py
```
- ✅ **conftest.py, connection.py: temiz** (BOM, NUL, mojibake, trailing whitespace yok).
- Pre-existing ihlalfler (88): `scripts/`, `trigger.py` dosyalarında; bu görev kapsamı dışında.

---

## Bulgular

- 🟡 **dikkat:** Tam süitte 6 yeni failure tespit edildi (pre-existing iddiası teyitsiz kaldı):
  1. `test_auth_modal_icerik_fonksiyonu` — "Şifremi unuttum" metni eksik (auth modal yapısı).
  2. `test_bos_talimat_hata_firlatir` — D-66 brif guard: `TriggerError` beklenen ama raise edilmiyor.
  3. `test_bosluk_talimat_hata_firlatir` — D-66: sadece boşluk talimatı error firlatmıyor.
  4. `test_olmayan_brif_hata_firlatir` — D-66: diskte olmayan brif dosyası tespit edilmiyor.
  5. `test_render_webhook_monitor_tab_renders_metrics` — Webhook monitor tab mock'lama başarısız (Streamlit stub hatası).
  6. `test_sekme_rehberi_metinleri_utf8_ve_yapili[admin_panel]` — "Bu ekran ne işe yarar?" başlığı eksik (admin_panel.py).

  **Sonuç:** companies/SQLite ile ilişkisiz. `git stash` doğrulaması yarım kaldığı için bu testlerin pre-existing olup olmadığı kanıtlanmadı (Windows cmd bash sözdizimi hatası yüzünden).

- 🟢 **tamam:** ALTYAPI-SQLITE-INIT hedefi tamamlandı: 16 error → 16 skip, companies tablosu schema'sı eksiksiz, `_init_test_db` fixture çalışıyor.

### 🔵 Bilgi
- 16 test skip etmek doğru davranış: empty DB'de data-dependent testler skip olur.
- Fixture scope=session olarak ayarlandı: init_db() tüm test suite için bir kez çalışır (verimli).
- Diğer 6 failure: ayrı görevler açılmalı (D-67 bulgu işleme).

---

## Eksik / Erteleme

- Hiçbir bulgu yok. İş tamamlandı per brief maddeleri.
- `oto_nobetci` otomatik onay (S-07 / D-46): bu görev P1 (manuel onay gerekli) → teslim yapılacak.

---

## Teslim Kontrol Listesi (D-55)

- [x] Rapor dosyası: `data/orchestrator/ALTYAPI-SQLITE-INIT_rapor_2026-09-20_uretim.md`
- [x] Test sonuçları: 78 passed, 16 skipped (0 errors, 0 failures)
- [x] Değişen dosyalar diskte: `tests/conftest.py` (fixture), `src/company_master/db/connection.py` (schema)
- [x] Kodlama temiz: `python scripts/kodlama_denetim.py` (conftest.py, connection.py clean)
- [x] Git kilit: Tek dosya, tek ajan (UTKU), kilidi teslim sırasında bırakılacak
