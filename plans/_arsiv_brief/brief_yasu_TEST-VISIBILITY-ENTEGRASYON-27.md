# TEST-VISIBILITY-ENTEGRASYON-27 — E2E Senaryo Testi

**Task ID:** TEST-VISIBILITY-ENTEGRASYON-27  
**Sahip:** Yasu  
**Öncelik:** P1  
**Durum:** bekliyor  
**Dependency:** ALTYAPI-VERI-GORUNURLUK-01 (tamamlandı)

---

## Amaç

test_visibility_layer.py gerçek `apply_kvkk_mask()` fonksiyonu çağrısı ile entegre et. 5 senaryo + 4 çelişki karantina testi çalıştır ve her biri geçsin.

---

## Doğrulanacak Varsayım

- normalize.py apply_kvkk_mask() fonksiyonu yazılı ve importable
- test_visibility_layer.py fallback mock ile hazırlandı (real import başarısızsa)
- 5 senaryo (terminal/strategic/strict/lenient/OSINT) mantık testleri
- 4 çelişki (Ç1-Ç4) karantina flag'ları

---

## Adımlar

### 1. Real Import Doğrula

**Dosya:** tests/test_visibility_layer.py (satır 1-50)

```python
try:
    from company_master.api.core.normalize import apply_kvkk_mask
    REAL_FUNC = True
except ImportError:
    REAL_FUNC = False
    def apply_kvkk_mask(...):
        return row
```

Kontrol: REAL_FUNC == True olmalı

### 2. 5 Senaryo Testi Çalıştır

**Komut:**
```bash
cd Huginn\ Data\ Insights
pytest tests/test_visibility_layer.py::TestVisibilityLayer -v
```

**Testler:**
1. test_scenario_1_terminal_match_strict — Terminal tier, strict mode
2. test_scenario_2_strategic_tier — Strategic tier, email domain seçici maskeli
3. test_scenario_3_admin_strict_mode — Yasak alanlar maskeli
4. test_scenario_4_admin_lenient_mode — Kısıtlı açık, yasak maskeli
5. test_scenario_5_osint_visible_fields — Website, nace açık

### 3. 4 Çelişki Testi Çalıştır

**Komut:**
```bash
pytest tests/test_visibility_layer.py::TestConflictResolution -v
```

**Testler:**
1. test_conflict_1_gsm_deletion — Ç1: quarantine_reason="ç1_telefon"
2. test_conflict_2_email_domain — Ç2: email karantina
3. test_conflict_3_personal_name — Ç3: kişi adı karantina
4. test_conflict_4_whatsapp — Ç4: WhatsApp karantina

### 4. Module Cost Testi Çalıştır

**Komut:**
```bash
pytest tests/test_visibility_layer.py::TestModuleCredit -v
```

Kontrol: Terminal/Strategic/Enterprise kontör matrisi doğru

### 5. Full Test

**Komut:**
```bash
pytest tests/test_visibility_layer.py -v --tb=short
```

**Beklenti:** 14 test pass ✅ (5+4+5 module)

---

## Kabul Kriteri

- [x] apply_kvkk_mask real import başarılı (REAL_FUNC=True)
- [x] 5 senaryo testi pass
- [x] 4 çelişki testi pass
- [x] Module cost testi pass
- [x] Pytest toplam 14 test pass
- [x] Hata varsa @pytest.mark.skipif kullan (import başarısızsa)

---

## Kurallar (ADMIN-KİT)

- Test mock değil, **real fonksiyon** çağrı yapmalı
- Fallback mock import başarısızsa devreye gir (test skip değil)
- Assertion: maskeleme kuralları Layer 1 (_KVKK_FIELD_CLASS) ile eşleş

---

## İlgili Nodlar

- [[Huginn Data Insights/tests/test_visibility_layer.py|Test dosyası]]
- [[Huginn Data Insights/src/company_master/api/core/normalize.py#374-475|apply_kvkk_mask()]]
- [[Huginn Data Insights/data/orchestrator/ALTYAPI-VERI-GORUNURLUK-01_TAMAMLANDI_2026-09-24_FINAL.md|Tasarım detayı]]
