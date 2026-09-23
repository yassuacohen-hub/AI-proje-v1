# ALTYAPI-FORM-SETUP-03 Briefi

## GÖREV TANIMI
Form altyapısı standardizasyonu (zincir adımı 3/3, önceki: UI-FORM-VALIDATION-02). Form konfigürasyonu (YAML/JSON), FormBuilder, tema token entegrasyonu ve form event logging. Detaylı brif: `data_worktree/orchestrator/ALTYAPI-FORM-SETUP-03_brif_2026-09-20_uretim.md`.

## İŞ MADDELERİ
1. `src/company_master/ui/forms/__init__.py`, `config.py`, `builder.py` yaz
2. FormBuilder(schema) → Streamlit widget'ları, auto-validation binding
3. Tema entegrasyonu: `token("color", ...)` kullanımı
4. Logging: `form:create`, `form:validate`, `form:submit`, `form:error`
5. `tests/test_form_setup.py` — 8 test (`python -X utf8 -m pytest tests/test_form_setup.py -v`)

## KENDİ-KONTROL
- [ ] İş tamamlandı
- [ ] 8/8 test yeşil
- [ ] UTF-8 temiz
