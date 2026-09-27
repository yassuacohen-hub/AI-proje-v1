# BRİEF — NAV-FIX-01: Tek tıkta bölüm geçişi + mojibake temizliği

**Ajan:** kilo · **Öncelik:** P0 · **Orkestratör:** roo · **Tarih:** 2026-09-16
**Kaynak plan:** `docs/plans/NAV-PLAN-01_v4.md` §1 (Bulgu 1) + §5 (cline O-1) + §6 sıra 1
**Zincir:** kilo teslim → **cline REV-NAV-FIX-01** (otomatik tetik) → roo onay

## BÖLÜM 1 — Sorun (sahibin gözlemi)
Panelde bölüm değiştirmek için **iki kez tıklamak** gerekiyor. Sebep: sidebar "Hızlı geçiş" selectbox'ı bayat (stale) değer tutuyor; topbar bölüm araması sorgusu sıfırlanmıyor; seçim ile URL/`session_state` bir rerun geç senkronlanıyor.

## BÖLÜM 2 — Kapsam (yalnız bu 4 madde)
| # | Dosya | Yer | İş |
|---|---|---|---|
| 1 | `app.py` | `render_sidebar` L451-462 (Hızlı geçiş selectbox) | Seçim değişince `bolum_sec()` **aynı rerun içinde** çalışsın; selectbox `key` + `on_change` ile, `index` her çizimde aktif bölümden hesaplansın (bayat değer kalmasın). Tek tıkta geçiş. |
| 2 | `app.py` | `render_topbar` L486-531 (bölüm araması) | Sonuç butonuna basınca sorgu `session_state`'ten temizlensin, `bolum_sec()` sonrası `st.rerun()` bir kez; ikinci tık gerekmesin. |
| 3 | `app.py` | L68 `page_icon` | Mojibake'li ikon → doğru emoji (UTF-8). |
| 4 | `web_dashboard/tabs/admin_panel.py` | L250-256 `render_ayarlar_tab` | Mojibake (`Ã¢`, `Ã…Â¡` vb.) → doğru Türkçe. `python scripts/mojibake_onar.py --kontrol` ile doğrula. |

**Dokunma:** `web_dashboard/tabs/__init__.py`, `SECTIONS`, tooltip (`help=`) — bunlar NAV-FIX-02 / NAV-IA-01 kapsamı.

## BÖLÜM 3 — Bitti ölçütü
1. Sidebar grup butonu, Hızlı geçiş ve topbar araması: **tek tıkta** hedef bölüm açılır (URL `/{url_path}` güncel).
2. `python scripts/kodlama_denetim.py` → 0 bulgu (BOM/NUL/mojibake).
3. Testler: `tests/test_dashboard_nav.py`, `tests/test_app_menu_rol.py`, `tests/test_web_dashboard_tabs.py` yeşil + tam regresyon `python -m pytest tests/ -q --continue-on-collection-errors` (sayı özete).
4. Yeni test: `tests/test_app_nav_tek_tik.py` — `bolum_sec` sonrası `session_state["bolum"]` ve URL param aynı rerun'da eşit; selectbox `index` aktif bölümü gösterir.
5. `python scripts/streamlit_restart.py` çalıştırıldı; agent-browser ile 3 geçiş (Ana Kontrol → KPI → Yönetim) tek tıkla doğrulandı, ekran görüntüsü `data/orchestrator/NAV-FIX-01_ss_<tarih>_kilo.png`.

## BÖLÜM 4 — İletişim kuralı (D-30)
- Sessizlik onay **değildir**; iş bitince `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id NAV-FIX-01 --ozet "..."`.
- Özet ilk satırı: **"BÖLÜM 4 okundu; kapsam 4 madde; tooltip/IA'ya dokunulmadı."**
- Kapsam dışı bulgu → `data/orchestrator/NAV-FIX-01_bulgular_<tarih>_kilo.md` (düzeltme yok).
- Proje sınırı: repo kökü dışına dosya yok; geçici dosya `data/_tmp/`.

## BÖLÜM 5 — Sözlük
| Kod | İki kelime | Ne ile ilgili |
|---|---|---|
| NAV-FIX-01 | Tek tık | Panelde bölüm geçişinin iki tık yerine tek tıkla olması. Mojibake temizliği de bu pakette. |
| REV-NAV-FIX-01 | Cline denetimi | Kilo teslim edince cline kodu inceler, roo onaylar. Otomatik tetiklenir. |
| Mojibake | Bozuk harf | UTF-8 metnin yanlış çözülmesiyle çıkan `Ã¶` gibi karakterler. `mojibake_onar.py` düzeltir. |
