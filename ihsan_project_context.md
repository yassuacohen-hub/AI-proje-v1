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

### 2026-09-26 (devam — auth lockout + ikiz temizliği + tek adres)

**AUTH-LOCKOUT-FIX-01 — bir fonksiyon çiftinde dört ayrı kusur.** Yukarıda "açık kusur" diye raporlanan yer kazılınca hata tek değil dört çıktı; dördü de aynı anda kilidin fiilen hiç çalışmamasına sebep oluyordu:
1. **Bind parametresi SQL metin sabitinin içindeydi.** `INTERVAL ':lockout_minutes minutes'` — `:ad` bir string literal'in *içindeyse* SQLAlchemy yerine koymaz, sürücüye düz metin gider. Kilit bitiş zamanı hiç yazılmıyordu. Düzeltme: zaman damgası Python'da hesaplanıp bind ediliyor (`_kilit_bitisi()`), dialect bağımsız.
2. **`except Exception: return False` → fail-open.** Şema hatası güvenlik kontrolünü *sessizce kapatıyordu*. Admin login hatasını haftalarca gizleyen mekanizmanın aynısı. Düzeltme: `except SQLAlchemyError` + `logger.error(exc_info=True)` + `raise`. Güvenlik kontrolü sessizce atlanamaz.
3. **Süresi dolan kilidi temizleyen UPDATE `engine.connect()` içindeydi**, commit yok → yazma sessizce çöpe gidiyordu. `engine.begin()` yapıldı.
4. **Sıra hatası (kod okunurken bulundu, raporda yoktu):** `api_admin_login_post` içinde kilit kontrolü `_verify_password`'dan **sonra** çalışıyordu. Kilitli hesap yanlış şifreyle 423 değil 401 alıyor, sayaç sonsuza kadar artıyordu — yani kilit hiç uygulanmıyordu. Kontrol şifre doğrulamasının önüne alındı.

**Tip varsayımı tuzağı:** ilk düzeltmede `locked_until` Python'da karşılaştırıldı, test `AttributeError: 'str' object has no attribute 'tzinfo'` ile patladı — kolon Postgres'te `datetime`, SQLite'ta `str` dönüyor. Karşılaştırma bilerek SQL tarafına alındı (`CASE WHEN locked_until > :simdi THEN 1 ELSE 0 END`), Python'da tip varsayımı kalmadı.

**Test:** `tests/test_auth_lockout.py` — 7 test, bellekte SQLite. SQLite kasıtlı seçildi: `NOW()` yok, dolayısıyla bind edilen zaman damgası olmadan test geçmiyor (1. kusur bir daha geri gelemez).

**D-211 İkiz Yapı Yasağı (KAHİN: "sistemde ikiz yapılar olmasın istiyorum"):**
- `web_app.py` içinde `_log_search_event` **birebir iki kez** tanımlıydı (1973 ve 2007); ikinci tanım birinciyi gölgeliyordu. Kopya silindi.
- `original_web_app.py` (~2500 satır) `web_app.py`'nin bayat kopyasıydı ve içinde **hatalı** `_record_failed_login` / `_is_account_locked` aynen duruyordu. Hiçbir yerden import edilmiyordu (tek atıf `logs/git_push.log`). `git rm` edildi. İkizin asıl zararı bu: ajan yanlış kopyayı okuyup düzeltmeyi oraya yazabilirdi.
- Kural yorumla değil testle korunuyor: `test_ikiz_fonksiyon_tanimi_yok` `web_app.py`'yi AST ile parse edip modül düzeyinde mükerrer fonksiyon adı arıyor.

**D-212 Tek Yapı Tek Adres (KAHİN kararı, önceki 8501/8502 planını iptal eder):** Tek panel adresi `http://localhost:8501/`. 8502'deki ikiz Streamlit örneği kapatıldı (PID 26400). Sahte veri ayrı bir sürüm/port değil: verisi gelmemiş kutu tek uygulamanın içinde yer tutucuyla çizilir, altına "⚠️ **SAHTE VERİ**: … — gerçek veri geldiğinde otomatik değişir." uyarısı basılır, gerçek veri gelince `_dolu()` True döner ve kutu kendiliğinden gerçek değere geçer. `ana_kontrol.py`'de `TASLAK` artık **varsayılan açık** (`os.getenv("HUGINN_TASLAK", "1") != "0"`); `HUGINN_TASLAK=0` yalnızca kaçış kapısı. `_test_groq_chat_live.py` 8501'e çevrildi, `streamlit_taslak.txt` silindi.

**Doğrulama:** `pytest tests/test_taslak_sahte_veri.py tests/test_auth_lockout.py -q` → **14 passed**.

**D-213 Menü Ağacı + Veri Etiketi + Marka Başlığı (KAHİN kararı 2026-09-26):**

- **NAV-AGAC-01** (KAHİN: *"oluşturulmuş bir sayfa navigatör menü ağacında gözükmeli"*, *"her sayfa menüde gözüksün sonra ilgili ve alakalı olanları birleştirelim"*): menü üyeliğini **tek alan** belirler — `TabTanimi.ust`. `ust is None` → kök, değilse o kökün altı. `ust_sayfalar()` içindeki 14 sayfayı gizleyen frozenset silindi; öksüz sayfalar ilgili başlıklara bağlandı. **UX-MENU-04'ün "taşan sekmeyi menüden çıkar" kuralı geçersiz**: sınır gizlemeyle değil **birleştirmeyle** korunur. Gizlenecek sayfa listesi tutmak D-211 ikiz yasağının UI hâliydi — iki doğruluk kaynağı (`ust` + gizli liste).
- **İkon çakışması (gizlemenin sakladığı gerçek kusur):** `executive` 📈 taşıyordu, `veri_kalite` de 📈. Sayfa menüde görünmediği için `test_ikon_benzersiz` bunu yakalamıyordu. `executive` → 💹.
- **Bayat testler yenilendi:** `tests/test_tabs_ia.py` içindeki 13 kayıtlık `MENUSUZ` demeti + `test_menuden_cikanlarin_adresi_kirilmadi` silindi; yerine `test_her_sayfa_menu_agacinda` (öksüz sayfa yok) ve `test_her_sayfanin_adresi_cozulur` geldi. Üst başına alt sekme sınırı **geçici olarak 12** (birleştirme sonrası düşürülecek).
- **VERI-ETIKET-01** (KAHİN: *"sahte veri ve gerçek veri ayırt etmek için ikon kullan altına sahte/gerçek diye yaz"*): tek yardımcı `ana_kontrol._veri_etiketi(gercek, sahte)`, veri bloğunun altına 🟢 GERÇEK / 🔴 SAHTE serilerini adıyla basar. 7 çağrı yeri.
- **MARKA-BASLIK-01** (KAHİN: *"logo biraz küçük olmuş büyüt ve sağ kısmına Admin Insights kelimesini yaz aynı renk gradeninde olsun"*, *"marka rengi logo renkleri ile aynı"*): tek kaynak `app.py::MARKA_RENK` — `#22D3EE / #3B82F6 / #4F46E5 / #8B5CF6`, `linear-gradient(135deg, … 0%/35%/65%/100%)`. `st.logo(size="large")` Streamlit'in üst sınırı olduğu için büyütme CSS ile (`max-height: 3.4rem`). "Admin Insights" ayrı bir marka bileşeni değil, `[data-testid="stSidebarHeader"]::after` — D-211 ikiz yasağı gereği.
  - Kendi hatam: ilk denemede gradyanı `docs/brand/assets/LOGO.md` design-token'larından (3 durak, 90deg) kurdum; KAHİN gerçek logo gradyanını verdi, birebir uygulandı. Ders: marka rengi *üretim varlığından* okunur, dokümandaki öneriden değil.

**Doğrulama:** tam takım `26 failed, 4258 passed, 12 skipped` (255 s). 26'nın **4'ü benim** (hepsi `test_tabs_ia.py`, NAV-AGAC-01'in su yüzüne çıkardığı) → düzeltildi: `pytest tests/test_tabs_ia.py tests/test_dashboard_nav.py tests/test_sekme_kapsama.py -q` → **206 passed, 3 skipped**. Kalan **22 hata bu çalışmadan önce de vardı** (`git show HEAD:` ile kanıtlandı): `test_api_integration` 2 (`web_app.py:1298` `tier = user.get(...)` None üzerinde), `test_error_handling` 3, `test_migration_0017` 5, `test_schema_validation` 4, `test_sayfa_iskeleti` 3, `test_musteri_yonetimi` 1 (`musteri_yonetimi.py:79 IndexError`), `test_marka_denetim_muafiyet` / `test_naming_audit` / `test_pano_denetim` / `test_user_settings` 1'er. Ayrı backlog kalemi.

**Sıradaki iş (KAHİN):** *"sonra ilgili ve alakalı olanları birleştirelim yani admin tek sayfada ilgili ve alakalı konuları görebilecek şekilde optimize ediyoruz sonra her sayfayı ayrıca tasarlarız vektör çartlar ve grafikler kullanırız"* → (1) ilgili sayfaları birleştir (mevcut alt sekme sayıları: `ana_kontrol 0, musteri_yonetimi 4, proje_yonetimi 8, veri_kalite 5, musteri_onizleme 4, sistem 11`), sonra 12 sınırını düşür; (2) sayfa başına vektör grafik tasarımı.

### 2026-09-26 (devam — D-214 menü temizliği + KVKK birleştirme)

KAHİN onayı: *"onaylıyorum kvkk birleştir zaten en faydalı konu buydu"*. PRD (`AI proje v1/V10/07_referanslar/Muninn SUPER ADMIN PANEL PRD V1.txt`) mevcut ağaçla kıyaslandı — ilham, zorunluluk değil.

**Yapılanlar (kod önceki oturumdan uygulanmış bulundu, bu oturumda doğrulandı):**
1. **SECTIONS temizliği** — `kpi` (ust=veri_kalite) ve `paketler` (ust=musteri_onizleme) çocuk kayıtları silindi: kökle birebir aynı `modul.fonksiyon` çiftini render eden ikiz girişlerdi (D-211 UI hâli). `sira` boşlukları kapatıldı. `ESKI_URL["kpi"]` → `veri_kalite`, `ESKI_URL["paketler"]` → `musteri_onizleme`. `yukleme` sekmesi (Sistem altı, geliştirici demo) menüde **kaldı** — devir notunun açık talebiydi.
2. **Yalan yorum temizliği** — "hatalar+dlq+webhook birleşti" ve "teknik_altyapi+performans birleşti" yorumları koddan silindi (gerçekleşmemiş plan anlatıyorlardı, ikisi de hâlâ ayrı sekme).
3. **D-214 testleri** (`tests/test_tabs_ia.py`): `test_d214_kok_cocuk_ayni_renderer_yasak` (kök↔çocuk aynı renderer kalıcı yasak) + `test_ust_basina_alt_sekme_siniri` ratchet'e çevrildi (sabit sayı yerine mevcut maksimum `sistem=11` tavan).
4. **KVKK birleştirme** — `render_kvkk_mode_tab` (`admin_panel.py`) kendi formunun altında `render_kvkk_rapor_tab()`'ı çağırıyor; ikinci fonksiyon SECTIONS'tan çıkarıldı, navigasyondan bağımsız yardımcı hâline geldi (öksüz değil — `test_sekme_kapsama.py` çağrı-grafiği taramasında `render_kvkk_mode_tab` içinden çağrıldığı görülüyor, MUAF gerekmedi). Menüde tek giriş: `kvkk_mode` (ust=proje_yonetimi). `ESKI_URL["kvkk-rapor"]` → `(proje_yonetimi, kvkk_mode)`.
5. **Test güncellemeleri** doğrulandı: `test_tabs_ia.py::test_birlestirilen_sekme_basliklari`, `test_dashboard_nav.py::test_alt_sekmeler_sira_sirali` (proje_yonetimi listesi artık `kvkk_mode` içeriyor, ayrı `kvkk_rapor` yok).

**Doğrulama:** `pytest tests/test_tabs_ia.py tests/test_dashboard_nav.py tests/test_sekme_kapsama.py -q` → **198 passed, 3 skipped**.

**Bekleyen (uygulama yok, KAHİN kararı bekliyor):**
- Faz 3: çıplak `st.*_chart` çağrılarının `charts.py`'ye taşınması (8 sayfa, P2).
- Güvenlik çatısı: denetim+mfa+kvkk tek kök altında toplansın mı? 7. kök, D-213'ün "≤6 kök" sınırıyla çelişir — KAHİN onayı şart.
- `sistem` kökünün (11 çocuk, en kalabalık) bölünmesi.
- `musteri_onizleme` grubunun "Gelir" adlandırması gözden geçirilecek.
- Temizlik: `tests/_tmp_onem_test/` + `_test_groq_chat_live.py` → `.gitignore`.
- Backlog: 22 ön-mevcut test hatası (madde 24, D-214 kapsamının dışında).
