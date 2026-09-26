> **YENİ OTURUMDA İLK OKUNACAK DOSYA** — orkestratör kimliği ve kalıcı hafıza. Her oturum başında önce bunu oku.

## Kimlik
- Rol: Huginn Data Insights projesi orkestratörü.
- Sorumluluk alanı: admin panel / dashboard (Streamlit `app.py` + `web_dashboard/`), test sağlığı, ajan görev teslim kabulü, görev planlama.
- Karar yetkisi: kod düzeyinde uygulama serbest. Mimari/ürün kararı KAHİN onayı ister. Yeni bağımlılık ekleme yasak (stdlib/mevcut kütüphane önceliği).

## Proje Temel Bilgileri
- Giriş noktası: `app.py` — sidebar, topbar, footer, routing, session state anahtarları.
- Sekme modülleri: `web_dashboard/tabs/*.py` (`ana_kontrol`, `admin_panel`, `admin_realtime`, `admin_musteriler`, `pazarlama`, `paketler`, `admin_quality`, `admin_auth`, `__init__.py` = `TabTanimi`/`SECTIONS`/rol yardımcıları).
- Görsel reçeteler: `web_dashboard/charts.py` (`kpi_karti_html`, `tema_paleti`, `kategori_rengi`, `sparkline_fig`, `donut_fig`, `alan_grafigi_fig`).
- Global CSS: `src/company_master/ui/styles.py` — `_BLOKLAR` tuple (bileşen CSS blokları) → `bilesen_css()` → `tum_css()` (root token'ları ekler) → `stil_etiketi()` (`<style>` sarar). `stil_enjekte(tema=aktif_tema())` `app.py::main()` içinde bir kez çağrılır (satır 758), tema değişmedikçe tekrar enjekte etmez (`_hg_stil_tema` session guard).
- Testler: `tests/` (pytest; `test_charts.py`, `test_sekme_kapsama.py`, `test_taslak_sahte_veri.py`, `test_admin_export_excel.py`, `test_ui_modal_stil.py`...).
- API: `web_app.py` (FastAPI; `/api/kpi`, `/api/companies`, `/api/admin/*`, `/api/buyer/*`).

## Sabitler ve Sözleşmeler
- `REHBER_KEY = "_hg_rehber"` (`app.py`) — TEK merkezi "Sekme rehberi" toggle anahtarı, footer'da (`render_footer`) çizilir. Sekme modülleri kendi toggle'ını çizmez, bu anahtarı `st.session_state`'ten okur. **Doğrulandı (2026-09-26)**: 6 sekme (`ana_kontrol`, `admin_panel`, `admin_realtime`, `admin_musteriler`, `pazarlama`, `paketler`) hepsi `_hg_rehber` okuyor, yerel toggle YOK — önceki "açık kusur" notu hatalıydı, kaldırıldı.
- `LOGO_YOLU = ROOT / "assets" / "huginn_logo.png"` (`app.py`) — `st.logo` ile sol üst logo; dosya yoksa metin başlığa düşer (fallback zaten kodlu, `render_sidebar`). PNG dosyası henüz sağlanmadı (owner'dan beklenen, madde 7 açık).
- `ROL_KEY = "_hg_rol"` (`app.py`) — U-10 oturum rolü override anahtarı (gelecek RBAC). `aktif_rol()` ile çapraz kontrolü henüz yapılmadı.
- **K3-10h kart kenar reçetesi** (KPI-RENK-05, `tests/test_charts.py`): `kpi_karti_html` çıktısı `background:{surface}; border:1px solid {border}; border-left:3px solid {kategori_rengi}`. Gradient/box-shadow/renk dolgusu yasak — kategori rengi yalnız sol şerit + 6px nokta (`count == 2`). **Doğrulandı**: `pytest tests/test_charts.py -q` → 47 passed.
- **K3-10h madde 4 (tüm container çerçeveleri)** — ÇÖZÜLDÜ. `_AKSIYON_CSS` (`ana_kontrol.py`, 5 aksiyon butonuna özel) genişletilmedi; onun yerine `styles.py`'e yeni global blok eklendi: `_CONTAINER_CSS` → `div[data-testid="stVerticalBlockBorderWrapper"]{border:2px solid var(--hg-color-border-strong)!important}`, `_BLOKLAR` tuple'ına eklendi (tüm `st.container(border=True)` çerçevelerini kapsar, tüm sayfalarda tek kural). Kategori rengi YOK, sadece `border-strong` token'ı (nötr, tema-duyarlı). Test: `tests/test_ui_modal_stil.py::test_container_cerceve_kategori_rengi_yok`.
- `_kart_izgara` (`ana_kontrol.py:165-196`) — sparkline yükseklik eşitleme kuralı: satırdaki tüm kartların serisi yoksa hiçbirinde çizilmez (`hepsinde_seri`).

## Bilinen Ön-Mevcut Test Açıkları (bu oturumun kapsamı DIŞINDA, madde 12 backlog'u)
`pytest tests/ -q` tam koşumda (2026-09-26) **22 failed, 4218 passed, 12 skipped** — hepsi bu oturumdaki değişikliklerden (styles.py/_CONTAINER_CSS/container border) bağımsız, önceden var olan hatalar: naming-audit ihlalleri, DB migration dosya kontrolleri, `test_sayfa_iskeleti.py` (admin_mfa/ana_kontrol iskelet), `test_sekme_kapsama.py` render-fonksiyonu öksüz kontrolü, `test_pano_denetim.py`, `test_musteri_yonetimi.py`, `test_marka_denetim_muafiyet.py`, API route-inventory testleri, chat-table-stil testi, user-settings schema testi. Kasıtlı olarak dokunulmadı (scope creep önleme) — madde 12'ye devredildi.

## Oturum Günlüğü

### 2026-09-26
**Yapılanlar:**
- K3-10h madde 1 (sparkline kart yüksekliği eşitleme), madde 2 (ikinci panel), madde 3 (border-left kategori rengi) kodda zaten mevcut bulundu (`_kart_izgara`, `kpi_karti_html`).
- `tests/test_charts.py` içindeki eski KPI-RENK-04 sözleşmesi (border-left yasaktı) → yeni **KPI-RENK-05** ile değiştirildi (border-left zorunlu, `count==2`). Doğrulandı: 47 passed.
- Footer (`render_footer`) `REHBER_KEY`/`KOMPAKT_KEY`/`IPUCU_KEY` toggle'larıyla yeniden düzenlendi: `Aktif Bölüm | toggle'lar | Cache+Yükleme`.
- Rehber merkezileştirme doğrulandı: 6 sekmede yerel toggle yok (kod okuma + regex taramasıyla kanıtlandı) — önceki "açık kusur" notu hatalıymış, düzeltildi.
- `test_admin_export_excel.py -q` → 9 passed, rehber metinleri sözleşmesi bozulmamış.
- **K3-10h madde 4 tamamlandı**: `_CONTAINER_CSS` bloğu `styles.py`'nin global `_BLOKLAR`/`stil_enjekte()` boru hattına eklendi (tüm `st.container(border=True)` çerçeveleri, kategori rengi yok, sadece `border-strong` token'ı, `border:2px solid`). `tests/test_ui_modal_stil.py`'e kalıcı sözleşme testi eklendi (`test_container_cerceve_kategori_rengi_yok`, 5 passed). Hedefli testler (theme_system, ui_kontrast, ui_components, ui_modal_stil, ui_tipografi) hepsi geçti; tam suite koşumunda (`pytest tests/ -q`) 22 önceden var olan/ilgisiz hata dışında regresyon yok.
- Bu kalıcı hafıza dosyası (`ihsan_project_context.md`) düzeltildi: yanlış rehber-kusur notu kaldırıldı, madde 4 tamamlandı olarak işaretlendi, pytest-çalıştırılmadı notu güncellendi.

**Son bırakılan iş:**
- Madde 7 hâlâ blokta (logo dosyası owner'dan bekleniyor) — dokunulmadı.
- Genel temizlik (22 ön-mevcut test hatası, madde 12) — başlanmadı.

**Sıradaki adım:**
1. Madde 12 (genel temizlik, 22 ön-mevcut hata) önceliklendirilip başlanabilir, veya yeni görev planlamasına geçilebilir.
2. Ajan görev teslimlerini kabul kriterine karşı periyodik doğrulamaya devam et.
3. Her aşama sonunda bu dosyayı güncelle.

### 2026-09-26 (devam — madde 6)
**Yapılanlar:**
- Backlog kontrolü tamamlandı: `task_board.json` ↔ `onay_kuyrugu.json` senkron doğrulandı; 18 bekliyor kayıt çözümlendi (17 onay, 1 red).
- **K3-10h madde 6 (sayfa yükleme/cache hızı) tamamlandı** — iki somut fix, `admin_panel.py`:
  1. `_gorev_panou_yukle()` her Streamlit rerun'da `task_board.json`'ı diskten okuyordu, cache yoktu → `@st.cache_data(ttl=30)` eklendi.
  2. `render_chat_summary()` aynı `ajan-chat.jsonl` dosyasını tek render'da 4 kez okuyordu (3x `ozet()` + 1x `oku()`, `ozet()` içeride `oku()`'yu tekrar çağırıyor) → tek `oku()` çağrısı + bellekte 3 liste comprehension filtreye indirgendi, ikinci `oku()` çağrısı silinip aynı `tum_sorunlar` değişkeni tekrar kullanıldı.
- Doğrulama: `pytest tests/test_sekme_kapsama.py tests/test_charts.py -q` → 1 failed (`render_task_board_tab` reachability, ön-mevcut/ilgisiz), 127 passed, 2 skipped — fix'ler öncesi/sonrası aynı tek hata, regresyon yok.
- `render_task_board_tab` öksüz-sekme kusuru madde 12 (22 ön-mevcut hata) kapsamına devredildi, kasıtlı dokunulmadı.
