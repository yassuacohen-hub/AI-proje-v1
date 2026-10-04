# utku oturum arsivi — 2026-10 (D-219 rotasyonu)

Tavan 400 satır aşılınca eski oturum blokları buraya taşınır.
§Öz-eleştiri **hiçbir zaman** taşınmaz/silinmez.

## KALDIĞIM YER (önceki blok — 2026-10-02)

- **Konum:** `DOC-GLOBAL-INTEL-ARASTIRMA-01` **teslim edildi → `review`** (2026-10-02 23:50).
  `SCRAPE-002` de `review`'da. Commit `2ae39f8` (45 pre-commit testi geçti).
  Sonraki hedef: D-312 döngüsü — `bak`/`ajan_chat.py oku`; SCRAPE-005 hâlâ **bloke**.
- **Yapılanlar (2026-10-02 23:40 DOC-GLOBAL turu):**
  - `docs/FAZ6_GLOBAL_INTEL_KAPSAM.md` yazıldı (370 satır) + `hubs/PLAN_STRATEGY_HUB.md`
    B-14 kapanış satırı. Kod yazılmadı (brif: dokümantasyon görevi).
  - **Ölçülen toplam:** `osb_veri_denetim.py` → 8987 kayıt / 8296 tekil / 44 mükerrer /
    647 kimliksiz / 0 mojibake. `--self` muhasebe ok, `--kontrol 8987` exit 0.
  - **D-260 tuzağı:** 8987 `data/osb/` ham çıktıdır, **`companies` DEĞİL**
    (9412 = D-263/D-264 tarihli ölçüm, bu turda yeniden ölçülmedi).
  - **Ülke kolonu `companies`'ta YOK.** Ama projede **iki tutarsız ülke geleneği** var:
    `user_activity_log.ulke_kodu CHAR(2)` ISO 3166-1 (0017:20) ·
    `job_postings.location_country TEXT DEFAULT 'Türkiye'` (0013:20). İkisi de taşınmamış.
  - 5 engel: E1 ülke · E2 `tax_number` VKN odaklı · E3 NACE (NAICS 50 migration'da **0**) ·
    E4 `is_ankara` tek soruya cevap veren kolon · E5 Türkçe dil varsayımı.
  - **Öneri: Yol A (ertele)** — E1-E5 veri değil öncelik eksikliği; Yol B'nin bedeli
    ölçülmüş (D-249 / 0024 gocu 8140 sahte 0 buldu).
  - 3 bulgu `bulgu_defteri.md`'ye yazıldı (acil: ülke geleneği çatışması).
- **İki brif sapması (ikisi de neredeyse yanlış karara yol açıyordu):**
  1. Brif E3'te `entity_resolution/` dedi → orada `maketrans` **0 eşleşme**.
     Gerçek yer `api/core/normalize.py:602,681` + `etl/kaynak_bagla.py:22`.
  2. İlk `findstr` **boş** döndü, "ülke kolonu yok" yazmak üzereydim.
     Pozitif kontrol (`vkn` → 12 satır) PowerShell `\"` tırnaklamasının
     bozuk olduğunu gösterdi. **Boş sonuç, sağlam sonuç kadar güvenilir değildir.**
- **KRİTİK — çok ajanlı kirli ağaç:** `git add` sonrası `AGENTS.md` ve
  `scripts/gorev_kutusu.py` **başka ajanların staged** işi olarak geldi.
  `git restore --staged <dosya>` ile stage'ten çıkar, içeriğine dokunma.
  `git add -A` **asla**.
- **Yapılanlar (2026-10-02 SCRAPE-002 turu):**
  - `SCRAPE-002-LEMMLESS-ANKARA-OSB` → **teslim (review)**. 5 yeni dosya:
    `src/company_master/etl/scrape_kayit.py` (0050 tek yazıcı),
    `src/company_master/etl/scrape_kosu.py` (ortak koşu iskeleti),
    `scripts/kazima_{ostim,ivedik,baskent}.py`. Kanonik scraper'lara
    **dokunulmadı** (D-235 `sayfa_dongusu` bozulmadı).
    Canlı ölçüm: `scrape_pages=2`, `scrape_audit_log=5`, `scrape_errors=1`,
    **yinelenen=0**, `cost_usd<>0 → [0,0]`, `llm_used TRUE → [0,0]`.
    İdempotens kanıtlandı: 2. tur `yazilan=0 / atlanan=1` (iki kaynakta da).
  - `SCRAPE-001-DOCKER-SETUP` → teslim (review) öncül görev.
  - `VERI-SCOR-MOTORU-01`, `VERI-TENDER-KOLON-01`, `VERI-RISK-MOTORU-01` → review.
- **Ölçülen çalışma adresleri (brif ile çelişiyor — dosyaya bakmadan yazma):**
  `baskentosb.org.tr` → **DNS çözülmüyor** (Errno 11002), izin reddi → `scrape_errors`.
  `ivedik.org.tr` → DNS çözülmüyor; **çalışan** `www.ivedikosb.org.tr` (200, 15 kart).
  `ostim.org.tr/firmalar` → 200, 334267 bayt, 300 `div.col-lg-4.mb-3`,
  300 `a[href^='/firmalar/']`, **0 `<table>`** (brifin tablo varsayımı yanlış).
- **Kritik bağlam (SADECE bu dosyalara bak):**
  `src/company_master/etl/scrape_kayit.py` · `src/company_master/etl/scrape_kosu.py`
  · `tests/test_scrape_kayit_mandali.py`
  · `scripts/kazima_{ostim,ivedik,baskent}.py` ·
  `src/company_master/schema/migrations/0050_scrape_audit_log.sql` ·
  `src/company_master/utils/scraping_permission_router.py`
- **Sonraki adım:** teslim sonrası `bak --ajan utku` + `ajan_chat.py oku`;
  açık bulgular: (1) baskentosb ölü domain, (2) SKILL.md router imzası yanlış.
  **(3) birim testi ve `audit_kaydet` FK borcu KAPANDI (23:30 turu):**
  `tests/test_scrape_kayit_mandali.py` = 34 test, canlı DB'ye bağlanmaz,
  kırma denemesi kanıtlı. `audit_kaydet()` artık `audit_id` döndürüyor →
  hata kayıtları FK'li (canlı: error_id=2 → audit_id=7, orphan=0).
  İdempotens **3. kez** doğrulandı (hash'ler değişmedi).
- **Öz-eleştiri (KALICI — SİLİNMEZ)** — bu turda *yazılan belgenin yarım
  kalması* önemli bir tuzak: uzun markdown `write` çağrısı sessizce ortada
  kesilebiliyor ve tool "başarılı" diyor. Teslimden önce dosyanın **sonunu
  okumak** zorunlu; `grep` ile son başlığı aramak yetmiyor.
- **Görev:** `DOC-GLOBAL-INTEL-ARASTIRMA-01` (review) · `SCRAPE-002` (review) ·
  `SCRAPE-005-KAZIMA-DOCKER-INTEGRATION` (**bloke**, brif + locked path eksik) ·
  **Son okunan karar:** `D-323`

> **SCRAPE-002'de briften 3 yerde sapıldı — hepsi diskte ölçülerek bulundu.**
> (1) Brif `get_router("ostim.org.tr")` / `can_fetch()` diyor; gerçek API parametresiz
> `get_router()` → `.check(url) -> Decision(url,domain,allowed,reason)`.
> (2) Brif tablo seçicisi varsayıyor; OSTİM'de 0 `<table>`, gerçek yapı
> `div.col-lg-4.mb-3` + detay linkleri.
> (3) Brif `scrape_errors`'a `source_name`/`source_url` yazıyor; 0050 şemasında
> **bu kolonlar yok**, bağ yalnız `audit_id` FK'si. İlk yazım canlıda reddedildi.
> *Ders: kanonik scraper sınıfları ve migration dosyası briften önce okunur;
> brif özetdir, sözleşme değildir (D-224/D-267).*

> **Çalışma ağacı çöp dolu (2026-10-02 ölçümü).** `git status` yüzlerce dosya
> (başka ajanların `??` ve `M` dosyaları) listeliyor. **`git add -A` TEHLİKELİ** —
> başkasının işini commit'ler. Bu turda yalnız kendi 6 dosyam commit edildi;
> ortak dosyalar (`task_board.json`, `hubs/*`, ajan context'leri) elle bırakıldı.

> **Önceki turun notu (SCRAPE-001):** ayrıntı kendi raporunda —
> [[SCRAPE-001-DOCKER-SETUP_rapor_2026-10-02_uretim]].

> **SCRAPE-002 brifi AÇILABİLİR.** Panodaki yol `../.agents/skills/huginn-web-kazima/SKILL.md`
> goreli; vault kökünden çözülünce `C:\Huginn Data Projesi\.agents\...` = 16034 bayt,
> `Test-Path` True. Brif zaten **0050** yazıyor (D-323 düzeltmesi brife de işlemiş).
> **Ben bu turda iki kez aynı hatayı yaptım:** (1) "brif 0046 gösteriyor" → düzeltilmişti,
> (2) "brif yolu geçersiz, dosya yok" → **dosya vardı**. İkisi de diskte ölçülmeden
> söylendi (D-224/D-260). *D-220 kural 2 `.agents/`'i arama kapsamı dışı yapar; bu
> brif yolu, arama değil — brif diskte ve okunabilir.*

> **B-14 kapısı iki yer ister (2026-10-02 ölçümü):** teslim reddi
> "hafıza izi yok" dediğinde tek yazmak yetmiyor — `gorev_kutusu.py:_hafiza_hedefleri()`
> **SSOT hub'ı (`hubs/ADMIN_DASHBOARD_HUB.md`) + brif'te geçen hub'ları** arıyor.
> Konu hub'ı (OSINT) tek başına yetmiyor. Bu turda ilk deneme OSINT'e yazıp
> **reddedildi**, ikinci deneme ADMIN'e de yazınca geçti.

# 2026-10-04 - UI-ADMIN-KAYNAKLAR-SAYFA-34 (teslim)

**Ne yapildi:** web_dashboard/tabs/admin_kaynaklar.py yazildi (374 satir,
render_kaynaklar_tab(), 4 bolum). 0050 kazima tablolarinin **ilk okuyucusu**
(D-236 kapandi). Yazma yok - etl/scrape_kayit.py::KazimaYazici tek yazici.
Nav kaydi web_dashboard/tabs/__init__.py:367-379 (veri_kalite, sira 5,
ikon tekil, min_rol admin).

**Canli olcum (D-238):** scrape_audit_log=36, scrape_errors=2, scrape_pages=3.
Sayfa okuyuculari dogrudan SQL ile birebir **UYUM**. Ozet satiri:
5 kaynak / 36 cekis (12 basarili) / 2 hata / 3 sayfa. Rozetler:
9router-jina 100 (2/2), ivedik 100 (3/3), ostim 57.1 (5/16),
aso 55.5 (2/13), baskentosb 50 (0/2).

**Test:** tests/test_admin_kaynaklar.py 10 passed; nav/IA/iskelet/paket
309 passed 3 skipped. kodlama_denetim.py 43 ihlal - tamami on-mevcut, benim
5 dosyam listede yok. Streamlit 8501 saglik ok ile yeniden basladi.

**Iki tuzak (bulgu_defteri'ye yazildi):**
1. **Olcek tuzagi:** kaynak_guvenilirlik.saglik_rozeti(oran) 0-1 bekliyor,
   KaynakSaglik.skor 0-100. Kopru admin_kaynaklar.py:236 saglik_rozet_metni()
   ile yazildi. Module tasinmasi icin orkestrator karari soruldu
   (chat soru 2026-10-04T01:04).
2. scrape_pages kaynak kolonu tasimiyor; kaynak bazli sayfa adedi
   source_url domaininden turetildi (yaklasim, kesin kaynak degil).

**Ogrenilen:** teslim raporundaki her dosya:satir **yazimdan sonra**
olculmali. Ilk raporda 212/296 yazdim, gercek 236/288 - hub satiri da
367->369 duzeltildi. Yazarken hatirlamak yerine olcup yaz.

**Rapor:** data/orchestrator/UI-ADMIN-KAYNAKLAR-SAYFA-34_rapor_2026-10-04_uretim.md
**Hub:** hubs/ADMIN_DASHBOARD_HUB.md:210 (B-14)
**Sonraki:** UI-ADMIN-CRAWL-TASI-35 (crawl kontrolleri webhook_monitor.py'den
yeni sayfaya). 37/38 __init__.py'ye dokundugu icin 34 kapandiktan sonra.

## UI-ADMIN-CRAWL-TASI-35 — Crawl Kontrolu tasindi (2026-10-04) — ✅ TESLIM

**Ne yapildi:** Crawl baslat/durdur paneli `web_dashboard/tabs/webhook_monitor.py:236-302`den
`web_dashboard/tabs/admin_kaynaklar.py:359`a (`_render_crawl_kontrolu()`) tasindi. Durum sabitleri
`admin_kaynaklar.py:76-89`, `_crawl_is_enabled():91`, `_log_crawl_action():96` — **tek tanim** (D-211).
`webhook_monitor.py`de `import os` + 6 sabit + 2 yardimci + kontrol blogu silindi; yerine
`:218-228`de `st.caption` + `st.link_button(... tab_getir("kaynaklar").url_path ...)` yonlendirmesi.

**Davranis degismedi (7 madde korundu):** 4 durum degeri (`beklemede/calisiyor/basarisiz/durduruldu`),
`CRAWL_DURUM_IKONLARI`, `CRAWL_ENABLED` env kapisi, `admin_email` yetki kapisi, baslat -> `calisiyor`,
iki asamali onayli durdur, `session_state` anahtarlari. Ek: 4 butona `key=` eklendi (DuplicateWidgetID onlemi).

**Yerlesim:** Durum Ozeti'nden sonra, Son Calismalar'dan once. Panel `Section(..., seviye=3)` —
`BOLUMLER` listesine girmiyor, D-213 menu tekligi bozulmadi.

**Test:** `tests/test_admin_kaynaklar.py` 8 yeni test (tek tanim / 0 satir / yonlendirme / sira /
seviye-3 / yetki / baslat+iki asamali durdur / ikon kapsami) -> dosya **18 passed**. Kabul seti
(`test_webhook_monitor_tab` + `test_admin_kaynaklar` + `test_admin_kpi_kart` + `test_sekme_kapsama` +
`test_sayfa_iskeleti`) **213 passed, 2 skipped**. `py_compile` OK. Statik: `findstr "Crawl Kontrol"`
`webhook_monitor.py`de **0 satir** (case-insensitive dahil).

**SSOT v2.8 -> v2.9:** §0 surum/tarih · §7 Veri Ops satiri · §8.1 A8 · §12 (§12 satiri `Kısmi->Tam`,
G8 zincir `34✅→35✅→36`) · §14 changelog. §10 backlog satiri 10 **degistirilmedi** (D-197: durum §7'den okunur).
Hub: `hubs/ADMIN_DASHBOARD_HUB.md:123` (35 satiri oncul) + `:226` (B-14 kapanis satiri).

**Bulgu:** Crawl baslatma **gercek tetikleme yapmiyor** — yalniz `session_state` degisiyor +
log yaziliyor (`etl/scrape_kayit.py::KazimaYazici` cagrilmiyor). Brief kapsami disi oldugu icin
mevcut -19 davranisi korundu; `ihsan`a soruldu.

**Denetim:** `scripts/kodlama_denetim.py` 47 ihlal, **bu gorevin dosyalarinda 0**. Taban 43->47 farki
NACE/QWEN dosyalarina ait (`nace_sozluk_yukle.py`, `sozluk_baslik_duzelt.py`,
`test_mojibake_bariyer.py`, `dosya_sonu` scriptleri) — baska ajanlarin kilidinda, dokunulmadi.

**Rapor:** `data/orchestrator/UI-ADMIN-CRAWL-TASI-35_rapor_2026-10-04_uretim.md`
**Bulgu defteri:** 2 kayit eklendi.
**Streamlit:** PID 24880, `http://127.0.0.1:8501` saglikli.

**Sonraki:** `UI-ADMIN-SON-KAZIMA-KART-36` (Ana Kontrol karti -> kaynaklar sayfasi baglantisi).
36 sonrasi 37 (`ACIKLAMA-METIN`), 38 (`REHBER-ALAN`, 36'ya bagli).

### 2026-10-02 — SCRAPE-001 teslim (review) + teslim döngüsü atlandı

- **Teslim:** `SCRAPE-001-DOCKER-SETUP` → `review`. `0050_scrape_audit_log.sql`
  (+down) canlı; `Diskte 50 goc / defterde 50 kayit`; `scripts/_kazima_dogrula.py` 6/6.
  İki hata düzeltildi: `table_schema='public'` filtresi (D-253/4), yalan
  `veri-gocu:`/`dusen-iz:` beyanları (D-253/2). B-14 ilk denemede reddedildi
  (konu hub'ı yetmiyor, ADMIN hub'ı da gerekiyor), ikinci denemede geçti.
- **Ajan chat:** 17 açık mesaj vardı, **hiç okunmamıştı**. Sonradan okundu;
  D-183 iddiam çekildi, SCRAPE-002 kilidi ihsan'a bildirildi.
- **Düzeltmeler:** geçici betik SHA manifestli arşive; rapor 3→11 wikilink;
  ADMIN+OSINT hub satırlarına rapor/göç wikilink'i; bulgu defterine 3 kayıt.

---

# Arsivlenen oturum blogu (2026-10-04) - UI-ADMIN-REHBER-ALAN-38 teslimi

D-219: 400 satir tavani asildi; bu blok `utku_project_context.md`
uzerinden arsivlendi. §Oz-eleştiri hicbir zaman tasinmaz.

# 2026-10-04 - UI-ADMIN-REHBER-ALAN-38 (teslim)

**Ne yapildi:** Yedi sayfada ic ice gomulu `_hg_rehber` okumasi kaldirildi; metinler
`TabTanimi.rehber` alanina (TEK kaynak: `web_dashboard/tabs/__init__.py`) tasindi ve
`app.py:714-715` tek cizim kancasi eklendi. Bes olculmus kok rehberi yazildi; 37 bolumden
12'si rehberli, yedi kokun tamami rehberli.

**Tuzak (yeni):** Eski mandal `tests/test_admin_export_excel.py::test_sekme_rehberi_...`
modul dosyasini okuyordu; tasima sonrasi **6 kirildi**. Kural govdesi tek kaynaga
baglandi (D-246) ve dort-baslik ratchet'i ayri teste tasindi. D-260: refactor sonrasi
**tum suret** bir kez calistirilir; hedefli yesizlik yeterli degildir.

**Dogrulama:** `tests/test_tabs_ia.py` 8 yeni mandal; kirma denemesi
`data/_tmp/rehber_mandal_kirma.py` kirildi (rc=1) ve kaynak bayt bayt geri kondu.
Kabul seti 220 passed / 3 skipped. Kodlama denetimi: bu gorevin dosyalarinda **0** ihlal
(kalan 4 ihlal `scripts/kazima_*` dosyalarina ait, baska ajanlara ait — dokunulmadi).
Streamlit PID 16112, `http://127.0.0.1:8501` saglikli.

**Rapordan bilinmesi gerekenler:** Denetim paneli `proje_yonetimi.py` icinde satir ici
cagrildigi icin merkezi yaklasimda **denetim rehberi yalniz `denetim` kokunde** gorunur.
`utku_project_context.md` 443 -> 338 satir (D-219 arsiv rotasyonu; oz-eleştiri tasinmadi).

**Rapor:** `data/orchestrator/UI-ADMIN-REHBER-ALAN-38_rapor_2026-10-04_uretim.md`
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` (B-14 kapanis satiri)
**Sonraki:** `VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01`; task 36 cizim kararini bekliyor.
