# NAV-FIX-02 — Menü açıklamaları menü dışında (sağda) gösterilsin

**Sahip:** kilo · **Öncelik:** P1 · **Orkestratör:** roo · **Tarih:** 2026-09-16

## BÖLÜM 1 — Sorun (sahip bulgusu, ekran görüntülü)
- NAV-FIX-03 ile sidebar buton tooltip'leri varsayılan KAPALI oldu (`IPUCU_KEY` toggle, `app.py`).
- Toggle **AÇIK** iken Streamlit'in native `help=` balonu hâlâ menü butonlarının üstüne biniyor.
- Sahip emri: *"bilgi yazıları menü dışında sağda gösterilsin; böylece menüyü kapatmaz."*

## BÖLÜM 2 — İş (minimal, kapsam dışına çıkma)
1. `app.py` → `_nav_ipucu()` **her durumda `None`** döndürsün (native tooltip tamamen kalkar). Fonksiyon imzasını koru; docstring'e NAV-FIX-02 notu.
2. `app.py` → `render_topbar()` içinde, toggle (`st.session_state[IPUCU_KEY]`) **açıkken** seçili bölümün açıklamasını **sağ kolonda (`sag`)**, arama kutusunun altında `st.caption(...)` ile göster:
   - Metin: `f"ℹ️ {tanim.aciklama}"` + hazır değilse `" · ⏳ yapım aşamasında"`.
   - Toggle kapalıyken hiçbir şey çizilmez (mevcut davranış korunur).
3. Sidebar toggle etiketi: `"Menü ipuçlarını göster"` → `"Bölüm açıklamasını göster"`; `help=` metnini kısalt: `"Seçili bölümün açıklaması sağ üstte, arama kutusunun altında görünür."`
4. `render_topbar` çoklu eşleşme butonlarındaki `help=aday.aciklama` **kaldırılsın** (aynı binme sorunu).
5. Test: `tests/test_app_nav_tek_tik.py` içine 2 test — (a) `_nav_ipucu` toggle açık/kapalı her iki durumda `None` döner; (b) toggle açıkken topbar açıklama caption'ı çağrılır, kapalıyken çağrılmaz (mevcut `sahte_st`/monkeypatch kalıbını kullan).
6. `python -m pytest tests/test_dashboard_nav.py tests/test_app_menu_rol.py tests/test_app_nav_tek_tik.py -q` yeşil + tam regresyon sayısı özete.
7. `python scripts/streamlit_restart.py` çalıştır (UI dosyası değişti).
8. Kodlama: UTF-8, BOM yok; PowerShell `Out-File` yasak.

## BÖLÜM 3 — Kilit
- `app.py`, `tests/test_app_nav_tek_tik.py`. Başka dosyaya dokunma.

## BÖLÜM 4 — İletişim Protokolü (ZORUNLU)
- Teslim: `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id NAV-FIX-02 --ozet "..."`
- Özette **ilk satır**: `BÖLÜM 4 okundu`. Bu satır yoksa teslim reddedilir.
- Sessizlik onay değildir; `done` yalnız roo onayıyla.
