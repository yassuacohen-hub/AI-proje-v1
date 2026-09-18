# REV-BATCH-01 — Kapsam Dışı Bulgular (cline — 2026-09-16, düzeltme YOK)

Brief gereği ana rapora girmeyen, gezinti sırasında görülen gözlemler:

1. **web_app.py 2835 satır monolit** — routers/services katmanı yok; ROO_ELESTIRI_NOTLARI.md M-06 (cline, 2026-09-16) olarak defterde.
2. **tabs/__init__.py yenile() streamlit import** — saf veri sözleşmesi bozuk; M-04 defterde (roo). Bu commit''te yenile() __all__''a eklendi ama modül taşıma yapılmadı.
3. **change-password `.strip()`** — web_app.py:2578-2579; ana rapor D-4 (kapsama alındı; burada yalnız not).
4. **`.gitignore`''da `.streamlit/secrets.toml` yok** — dosya şimdilik diskte yok; web_app.py:2506 fallback''i destekliyor. Ana rapor D-1.
5. **Kök dizindeki geçici scriptler** (`fix_*`, `update_*`, `temp_script.py`, `replace_app_functions.ps1`) — S-10 defterde (cline). Bu inceleme sırasında app.py üzerinde eski replace ps1''in docstring''i hâlâ repo kökünde duruyor.
6. **ELESTIRI-01 kilidinin paylaşımlı deftere konması** — D-30 deftere işlendi; kilit bırakıldı (sahip düzeltmesi).
7. **Brand-set versiyon kontrolü dışında** — S-09 defterde (cline).

Bu dosyadaki hiçbir madde REV-BATCH-01 kapsamında DÜZELTİLMEDİ (yalnız oku kuralı).