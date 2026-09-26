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
- `LOGO_YOLU = ROOT / "docs" / "brand" / "assets" / "Muninn_logo_transparent.png"` (`app.py:100`) — `st.logo` ile sol üst logo; dosya yoksa metin başlığa düşer (`render_sidebar`). **MARKA-LOGO-01 (2026-09-26, ÇÖZÜLDÜ)**: eski değer `ROOT / "assets" / "huginn_logo.png"` idi, `assets/` klasörü hiç üretilmemişti → `.exists()` daima False → marka başlığı hep metin (`## 🏢 Huginn` + caption) olarak kalıyordu. KAHİN onaylı Muninn varyantına çevrildi; artık yazı yok, sadece logo.
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

### 2026-09-26 (devam — admin login + şema denetimi)
**MASTER KÖK NEDEN — `migrate.py` SQL'i hiç çalıştırmıyordu (MIGRATE-EXEC):**
`run_migrations()` yalnızca `f"APPLY: {mig['file']}"` metinlerini bir listeye ekliyor ve `schema_versions.json`'a `current_version` yazıyordu. DB bağlantısı YOK. 0016'dan beri her migration "uygulandı" olarak deftere işlendi, veritabanı hiç değişmedi. Admin login hatası bunun türevi: eksik kolon/tablo → `try/except Exception` yutması → yanlış "şifre hatalı" algısı. **Şifre (`556233`) baştan beri doğruydu.**
- Düzeltme: `apply_sql()` artık `conn.connection.cursor().execute(sql)` (raw DBAPI cursor) kullanıyor. Neden: `text()` → `:s` bind param sanıyor; `exec_driver_sql` → `%` psycopg format placeholder sanıyor. Ham DDL için tek güvenli yol raw cursor.
- `tests/test_data_log.py:184-197` AST ile `run_migrations` içinde `"15"` literalini arıyor → `target: int = 15` varsayılanı korundu (17 passed).

**SEMA-DENETIM-01 — kod ↔ DB kayması:**
Tarama tekniği: `\b(?:FROM|JOIN|INTO|UPDATE)\s+([a-z_][a-z0-9_]{2,})` regexi, `SELECT|INSERT INTO|UPDATE|DELETE FROM|JOIN` içeren satırdan sonraki 40 satırlık pencerede; `from `/`import ` ile başlayan satırlar atlandı (yanlış pozitif 129 → 49).
- 5 bozuk migration onarıldı: `0015_data_log.sql` (`AUTOINCREMENT` → `SERIAL`, SQLite sözdizimi PostgreSQL'de patlıyordu), `0018_visibility_layer.sql` (`REFERENCES admin_users(admin_id)` → `users(user_id)`, olmayan tablo), `0003_intelligence.sql` (FK `DO $$ ... pg_constraint IF NOT EXISTS` ile sarıldı).
- 5 hiç oluşturulmamış tablo: `0021_missing_tables.sql` → `audit_logs`, `admin_audit_log`, `entity_matches`, `campaign_packages`, `api_usage_daily`. Hepsi `IF NOT EXISTS`, her DDL'de çağrı yerini adlandıran provenance yorumu var.
- `0020_login_lockout.sql`: `users.failed_login_attempts`, `users.locked_until`.
- Sonuç: DB 44 → 54 tablo/view. `python -m src.company_master.schema.migrations.migrate --apply` → **21/21 OK**, idempotent.
- Kalan 49 "eksik" ad tamamen gürültü: CTE alias (`scored`, `base`, `batch`), sistem katalogu (`pg_indexes`, `information_schema`), SQL anahtar kelimesi (`join`, `using`, `end`), Türkçe log metni (`isleme`, `sayisi`). Gerçek eksik tablo YOK.

**Ajan chat kapsam açığı (KAHİN uyarısının somut karşılığı):**
`tests/test_chat_table_stil.py` eski kolon şemasında (`"Ajan"`/`"Hangi Ajana?"` + `_ajan_ham`) kalmıştı; üretim kodu `_sohbet_tablo_stil` ise `"Gönderen"`/`"Alıcı"` + `_ajan_gonderici`/`_ajan_alici` okuyor. Sonuç: ajan renklendirmesi aylarca **hiç test edilmedi**. Test güncel şemaya çekildi, alıcı rengi için ek assert konuldu → 89 passed.

**Diğer:** giriş ekranındaki mükerrer "Şifremi unuttum" butonu kaldırıldı (19/19). 8501 ve 8502 aynı komutu çalıştıran iki özdeş dev örneği (staging/prod ayrımı yok) — PID 17812 / 26400.

**Açık kusur (raporlandı, düzeltilmedi):** `web_app.py:2044-2084` `_record_failed_login()` / `_is_account_locked()` her istisnayı `try/except Exception` ile yutuyor. Eksik-kolon hatasının haftalarca saklanmasının sebebi tam olarak bu. Hedefli `except` + log önerilir.

**Commit:** `bb40ffc` (şema + marka + test), ardından admin_auth mükerrer buton commit'i. `origin/chore/monorepo-merge` push edildi.
