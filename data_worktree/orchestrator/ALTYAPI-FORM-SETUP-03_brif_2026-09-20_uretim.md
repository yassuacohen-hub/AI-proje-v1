# Brief: ALTYAPI-FORM-SETUP-03 — Form Altyapısı Hazırlığı

**Görev ID:** ALTYAPI-FORM-SETUP-03  
**Sahip:** UTKU (Üretim/Hacim)  
**Öncelik:** P2  
**Tahmini Süre:** 2s  
**Dosyalar:** `src/company_master/ui/forms/__init__.py`, `src/company_master/ui/forms/config.py`

---

## DURUM
Zincir adımı 3 (son). Önceki: **UI-FORM-VALIDATION-02** (tamamlanınca otomatik tetiklenir).

---

## AMAÇ
Form altyapısını standardize et:
- Form konfigürasyonu (field definitions, rules)
- Tema entegrasyonu (tokens, renk paletleri)
- Hata handling (try/catch patterns)
- Logging (form events — submit, error, validate)

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. Form Config
- YAML/JSON tabanlı form tanımı (reusable)
- Örnek: 
  ```yaml
  forms:
    menu:
      fields:
        - name: menu_name
          type: text
          required: true
          max_length: 50
        - name: menu_link
          type: text
          pattern: "^/.*"
  ```
- Python config (`src/company_master/ui/forms/config.py`)

### 2. Form Builder
- `FormBuilder(schema)` — schema'dan form oluştur
- `build()` → Streamlit widgetler
- Auto-validation binding

### 3. Theme Integration
- Form renkleri `token("color", "...")` ile çek
- Input background: `token("color", "surface-1")`
- Error text: `token("color", "text-danger")`
- Border: `token("border-color", "border-subtle")`

### 4. Logging
- Form events:
  - `form:create`, `form:validate`, `form:submit`, `form:error`
- Loglama şeması:
  ```python
  log_form_event(event="form:submit", form_id="menu", user_id=..., timestamp=...)
  ```

### 5. Test Dosyası
- `tests/test_form_setup.py` — 8 test
  - `test_form_builder_olustur` (2 test)
  - `test_form_config_parse` (2 test)
  - `test_form_theme_integration` (2 test)
  - `test_form_logging` (2 test)
- Tüm testler yeşil: `python -X utf8 -m pytest tests/test_form_setup.py -v`

---

## DOSYALAR
- Yaz: `src/company_master/ui/forms/__init__.py`
- Yaz: `src/company_master/ui/forms/config.py`
- Yaz: `src/company_master/ui/forms/builder.py`
- Düzenle: `tests/test_form_setup.py`

---

## DEĞERLENDİRME KRİTERLERİ
✅ Form config (YAML/JSON) kurulu  
✅ FormBuilder sınıfı çalışıyor  
✅ Theme entegrasyonu (token'lar kullanılıyor)  
✅ Logging kurulu (events kaydediliyor)  
✅ Test sayısı: 8 (tümü yeşil)  
✅ UTF-8 temiz

---

## ZINCIR TAMAMLANIŞI
✅ Tüm 3 görev (UI-MENU-FORM-01, UI-FORM-VALIDATION-02, ALTYAPI-FORM-SETUP-03) bitmişse zincir kapanır. UTKU teslim eder.
