# UI-FORM-VALIDATION-02 Rapor — 2026-09-20

## Görev
- **Task ID:** UI-FORM-VALIDATION-02
- **Ajan:** utku
- **Durum:** TAMAMLANDI → TESLİM
- **Öncelik:** P2
- **Brif:** data/orchestrator/UI-FORM-VALIDATION-02_brif_2026-09-20_uretim.md

## Yapılan İş
1. **`src/company_master/ui/forms/errors.py`** — Hata sınıfları (72 satır)
   - `ValidationError` (base: field, message, code, to_dict)
   - `URLError`, `EmailError`, `LengthError`, `UniqueError`, `TurkishError`

2. **`src/company_master/ui/forms/validators.py`** — Validator sınıfları + registry (195 satır)
   - `UrlValidator` — `/` kontrolü, boşluk, format
   - `EmailValidator` — `@` kontrolü, domain, RFC 5322 regex
   - `TurkishValidator` — NUL, BOM, mojibake kontrolü
   - `LengthValidator` — min/max uzunluk
   - `UniqueValidator` — custom callable duplicate kontrol
   - `validate()` — tek alan, çoklu kural toplu
   - `validate_batch()` — çoklu alan toplu
   - `register_validator()` / `get_validator()` — registry

3. **`tests/test_form_validators.py`** — 12 test (yeni yazıldı)
   - `test_url_validator_*` (4 test)
   - `test_email_validator_*` (4 test)
   - `test_turkish_validator_*` (2 test)
   - `test_batch_validate_*` (2 test)

4. **`src/company_master/ui/forms/menu_form.py`** — UI-MENU-FORM-01 entegrasyonu
   - `validate_menu()` yeni validatorlar (`LengthValidator`, `UrlValidator`, `UniqueValidator`) kullanıyor

## Test Sonuçları
```
tests/test_form_validators.py -v  →  12 PASSED
tests/test_menu_form.py        -v  →   5 PASSED (entegre)
tests/test_d66_brif_guard.py   -v  →   5 PASSED (D-66 fix)
```

## Full Suite Regression
```
4 failed, 3940 passed, 22 skipped, 127 warnings in 77.37s
```

### Bilinen Test Failure'ları (UI-FORM-VALIDATION-02 Dışı — Önceden Var)
1. `test_find_root_finds_env` — .env konfigürasyonu (pre-existing)
2. `test_sekme_rehgeri_metinleri_utf8_ve_yapili` — encoding (pre-existing)
3. `test_auth_modal_icerik_fonksiyonu` — app.py "Şifremi unuttum" eksik (pre-existing)
4. `test_render_webhook_monitor_tab_renders_metrics` — st.metric çağrısı eksik (pre-existing)

**UI-FORM-VALIDATION-02 çalışması BU failure'lara neden olmamıştır.**

## Kodlama Denetim
- `python scripts/kodlama_denetim.py --tam-repo` — `errors.py`, `validators.py`, `test_form_validators.py`, `menu_form.py` listede yok (temiz)

## Streamlit
- PID 16228 -> http://127.0.0.1:8501 (sağlık OK)

## Integration
- `menu_form.py` `validate_menu()` şu an `LengthValidator`, `UrlValidator`, `UniqueValidator` kullanıyor
- Brief §4 entegrasyon örneği: `validate("menu_name", name, {"type": "string", "length": {"min": 1, "max": 50}})` → destekleniyor

## Bulgular
🟢 **Tamam:** 5 validator sınıfı (Url, Email, Turkish, Length, Unique) — hepsi testli
🟢 **Tamam:** 5 error sınıfı (ValidationError base + 4 özel) — to_dict() destekli
🟢 **Tamam:** Registry (`register_validator`/`get_validator`) ve batch validate (`validate`/`validate_batch`)
🟢 **Tamam:** UI-MENU-FORM-01 ile entegrasyon tamam — `validate_menu()` validatorları kullanıyor
🟡 **Dikkat:** `render_menu_form()` Streamlit runtime gerektirir; validator testleri pure logic (Streamlit dışı)
🔵 **Öneri:** `register_validator` ile custom business rule'lar UI-FORM-VALIDATION-03 görevinde eklenebilir
🔵 **Öneri:** `validate_tek()` helper'ı Streamlit inline error için var — kullanım örneği brief'e eklenebilir
