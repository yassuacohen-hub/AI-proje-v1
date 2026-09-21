# Brief: UI-FORM-VALIDATION-02 — Form Doğrulama Kütüphanesi

**Görev ID:** UI-FORM-VALIDATION-02  
**Sahip:** UTKU (Üretim/Hacim)  
**Öncelik:** P2  
**Tahmini Süre:** 2s  
**Dosyalar:** `src/company_master/ui/forms/validators.py`, `src/company_master/ui/forms/errors.py`

---

## DURUM
Zincir adımı 2. Önceki: **UI-MENU-FORM-01** (tamamlanınca otomatik tetiklenir).

---

## AMAÇ
Form doğrulama kurallarını merkezi kütüphane olarak yap:
- URL validasyonu (başla: `/`, format check)
- E-posta validasyonu (regex + @ check)
- Türkçe karakter validasyonu (mojibake kontrol)
- Uzunluk limitleri (min/max)
- Custom business rules (örn: duplicate ad)

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. Validator Sınıfları
- `UrlValidator` — `/` başlaması, boş olmaması
- `EmailValidator` — RFC 5322 basit (@ var, domain var)
- `TurkishValidator` — Türkçe karakterler bozuk mu (NUL, BOM check)
- `LengthValidator` — min/max uzunluk
- `UniqueValidator` — duplicate check (custom callable)

### 2. Error Sınıfları
- `ValidationError(field, message, code)` — base class
- `URLError`, `EmailError`, `LengthError`, `UniqueError` — spesifik

### 3. Validator Registry
- `register_validator(name, validator_instance)` — pluggable
- `validate(field_name, value, rules_dict)` — merkezi validasyon
- Çoklu hata topla (batch validate)

### 4. Integration
- UI-MENU-FORM-01 bu validatorları import + kullan
- Hata mesajları inline Streamlit `st.error()` ile göster
- Form submit:
  ```python
  errors = validate("menu_name", name, {"type": "string", "length": {"min": 1, "max": 50}})
  if errors:
      st.error(errors[0].message)
  ```

### 5. Test Dosyası
- `tests/test_form_validators.py` — 12 test
  - `test_url_validator_*` (4 test)
  - `test_email_validator_*` (4 test)
  - `test_turkish_validator_*` (2 test)
  - `test_batch_validate` (2 test)
- Tüm testler yeşil: `python -X utf8 -m pytest tests/test_form_validators.py -v`

---

## DOSYALAR
- Yaz: `src/company_master/ui/forms/validators.py`
- Yaz: `src/company_master/ui/forms/errors.py`
- Düzenle: `tests/test_form_validators.py`

---

## DEĞERLENDİRME KRİTERLERİ
✅ 5 validator sınıfı tam  
✅ Error sınıfları ve registry çalışıyor  
✅ UI-MENU-FORM-01 ile entegre  
✅ Test sayısı: 12 (tümü yeşil)  
✅ UTF-8 temiz

---

## SONRAKI GÖREV
ALTYAPI-FORM-SETUP-03 (zincir otomatik tetiklenir)
