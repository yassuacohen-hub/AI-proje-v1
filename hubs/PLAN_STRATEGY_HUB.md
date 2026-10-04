# Plan & Strategy Hub

> Yol haritasi, sprint planlari, gorev panolari ve stratejik kararlar.

Uretim: `GRAPH-HUB-EXPAND` (2026-09-21). Bagli dokuman: **48**

Ana baglam: [[Huginn Data Insights/AGENTS]] · [[Huginn Data Insights/PROJECT_ROADMAP]] · [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]] · [[Huginn Data Insights/hubs/REPORTS_ANALYSIS_HUB]] · [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]] · [[Huginn Data Insights/hubs/OSINT_INDEX]] · [[Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB]] · [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] · [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]] · [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]] · [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]] · [[Huginn Data Insights/hubs/V10_POC_HUB]]

---
---

### VERI-PAKET-FIYAT-SENKRON-01 — Fiyat kataloğu senkronu (yasu, 2026-10-04)

- **Ölçüm sonucu: script hiç çalışmamış.** `ROOT = parent.parent.parent`
  bir seviye fazla gidip `c:\Huginn Data Projesi` (repo **dışı**) veriyordu;
  `sys.path` yanış yöne baktığı için `ModuleNotFoundError: company_master`.
  `paketler.py` aynı ifadeyi kullanır ama 3 seviye derin olduğu için
  doğru — bu yüzden gözden kaçmış.
- Düzeltme: sabit seviye yerine **işaretçi ile repo kökü araması**
  (`src/company_master` bulunan dizin) → konum değişse de çalışır.
- Canlı: `--check` yeşil, JSON yazıldı, tekrar `--check` yeşil.
- Katalog: 4 tier · 499 / 2999 / 7999 / 19999.
- Test: `tests/test_paket_fiyat_senkron.py` — 5 passed.

---
### ALTYAPI-OPENROUTER-ARAC-01 — OpenRouter araçları kalıcı (yasu, 2026-10-04)

- 6 betiğe docstring + utf-8 stdout sarmalı (5/5 `or_*.py` + `continue_`).
- **Kritik düzeltme:** `or_seckin.py` ve `or_kod_liste.py` veri alışverişini
  `%TEMP%` üzerinden yapıyordu — Windows Temp temizlenince sessizce dosya
  hatası veriyordu. Artık `docs/raporlar/openrouter/` altında; katalog yoksa
  `or_seckin.py` üreticiyi kendisi çalıştırır.
- Canlı ölçüm: 278 model katalog + 80 satırlık seçkin raporu.
- Zamanlanmış görev: `\Huginn_Continue_Haftalik` · sonraki **5.10.2026 09:00**
  · Ready/Enabled. Kurulum: `scripts/zamanli_gorev_kur.py` (schtasks tırnak
  sorunu için Python installer).
- **Bilinen sınır:** görev `No Start On Batteries` + `Interactive only` —
  pildeyken veya giriş yapılmamış oturumda çalışmaz.
- D-288: anahtar değerleri çıktıda veya yazılan dosyada **yok**.

---
## 2026-10-03 — ALTYAPI-9ROUTER-ANAHTAR-01 (yasu)

- Betik: `scripts/ninerouter_anahtar_guncelle.py` — `.env` icindeki
  `NINEROUTER_KEY` satirini atomik degistirir (yedek → tmp → `os.replace`).
- Guvenlik (D-288): anahtar degeri **hicbir cikti/log/commit**e yazilmaz;
  yalniz ilk 4 karakter gosterilir.
- `--kuru` modu hicbir dosyaya yazmaz, yalniz plani gosterir.
- Cift satir tespit edilirse (rc=3) degistirme yapilmaz.
- Yazma sonrasi dogrulama: satir sayisi 1 degilse yedek geri yuklenir (rc=1).
- D-66 varsayimi dogrulandi: `.env` icinde `NINEROUTER_KEY` **tek** satir.
- Test: `tests/test_ninerouter_anahtar_guncelle.py` — 10 test.
- Kanit: yedek yazma **oncesi** alinir, dolayisiyla eski degeri icerir.

## Huginn Data Insights/AI proje v1

- [[PLAN_gorev_panosu]]

## Huginn Data Insights/AI proje v1/V10/wiki/tasks

- `Huginn Data Insights/AI proje v1/V10/wiki/tasks/code`
- `Huginn Data Insights/AI proje v1/V10/wiki/tasks/entity`
- `Huginn Data Insights/AI proje v1/V10/wiki/tasks/etl`
- `Huginn Data Insights/AI proje v1/V10/wiki/tasks/normalize`
- `Huginn Data Insights/AI proje v1/V10/wiki/tasks/sector`

## Huginn Data Insights/AI proje v1/scripts

- [[multi_osb_merger_plan]]

## Huginn Data Insights/AI proje v1/workspace/external

- [[BRIEF_2026-09-06]]
- [[BRIEF_Y10]]
- [[BRIEF_Y14]]
- [[BRIEF_Y16_sektor_zekasi]]
- [[BRIEF_Y17_veri_kaynaklari]]
- [[BRIEF_Y18_abonelik_plan]]
- [[BRIEF_Y2]]
- [[BRIEF_Y21_iskur]]

## Huginn Data Insights/AI proje v1/workspace/external/claude_code

- `Huginn Data Insights/AI proje v1/workspace/external/claude_code/brief`

## Huginn Data Insights/AI proje v1/workspace/external/copilot

- `Huginn Data Insights/AI proje v1/workspace/external/copilot/brief`

## Huginn Data Insights/AI proje v1/workspace/external/cursor_grok

- `Huginn Data Insights/AI proje v1/workspace/external/cursor_grok/brief`

## Huginn Data Insights/data/orchestrator

- [[Huginn Data Insights/data/orchestrator/P7-6_brif_2026-09-15_roo]]
- [[Huginn Data Insights/data/orchestrator/VAULT-BIRLESTIME-PLAN-01_strateji_2026-09-20_orkestrator]]

## Huginn Data Insights/data_worktree/orchestrator

- `Huginn Data Insights/data_worktree/orchestrator/ADMIN-UX-LOGOUT-01_brif_2026-09-20_uretim`
- `Huginn Data Insights/data_worktree/orchestrator/D72-SPRINT-BASLANGIC-TABLOSU_2026-09-20_orkestrator`
- `Huginn Data Insights/data_worktree/orchestrator/DOC-V10-AUDIT-01_brif_2026-09-20_orkestrator`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-BACKLOG-KANIT-01_brif_2026-09-20_orkestrator`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-BASLIK-D57-FIX-01_brif_2026-09-20_orkestrator`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-BRIEF-KALITE-01_brif_2026-09-20_denetim`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-BRIEF-KALITE-01_rapor_2026-09-20_denetim`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-BRIEF-TALIMAT-01_brif_2026-09-20_denetim`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-DECISION-LOG-03_brif_2026-09-20_orkestrator`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-DECISION-LOG-FORMAT-01_brif_2026-09-20_orkestrator`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-DUPLIK-KAPAYANIM-01_brif_2026-09-20_denetim`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-KARAR-DEFTERI-AUDIT-01_brif_2026-09-20_denetim`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-KARAR-DEFTERI-AUDIT-01_rapor_2026-09-20_denetim`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-KARAR-DEFTERI-FIX-01_brif_2026-09-20_orkestrator`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-KARAR-DEFTERI-FIX-01_rapor_2026-09-20_orkestrator`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-NAMING-AUDIT-02_brif_2026-09-20_orkestrator`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-STALE-TEMIZLIK-01_brif_2026-09-20_denetim`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-VAULT-TEKRAR-01_brif_2026-09-20_orkestrator`
- `Huginn Data Insights/data_worktree/orchestrator/ORKESTRA-ZINCIR-PLAN-01_analiz_2026-09-20_orkestrator`
- `Huginn Data Insights/data_worktree/orchestrator/OZEL-GOREV-DELEGASYON_2026-09-20_orkestrator`
- [[P7-6_brif_2026-09-15_roo]]
- `Huginn Data Insights/data_worktree/orchestrator/brief_UI-MENUTREE-02_utku`
- `Huginn Data Insights/data_worktree/orchestrator/brief_UI-PROFILMENU-POPOVER-02_utku`
- `Huginn Data Insights/data_worktree/orchestrator/operator_briefing`

## data/orchestrator

- [[data/orchestrator/GRAPH-SPRINT-OZET_2026-09-21]]
- [[data/orchestrator/SPRINT-FINAL-METRIK-2026-09-21]]
- [[data/orchestrator/SPRINT-FINAL-OZET-2026-09-21]]
- [[data/orchestrator/SPRINT2-SYNC-01_rapor_2026-09-21]]

---

## Not

- Baglantilar tam yol + uzantisiz yazilir; vault genelinde 156 ikiz dosya adi
  oldugu icin kisa ad kullanimi yanlis hedefe cozulur.
- Ters baglanti (backlink) Obsidian tarafindan otomatik uretilir; elle yazilmaz.
- Arsiv/yedek/gecici dosyalar bilerek disarida birakildi.

---

| DOC-VENDOR-DD-ARASTIRMA-01 | **Faz 5 "Vendor Due Diligence" kapsami arastirildi - KOD YAZILMADI (brif: kapsam disi).** SSOT'ta Faz 5'in tum icerigi **3 satir** (HUGIns.txt:867-869); tablo/kolon/akis **hicbiri yok** - kod brifi yazmak uydurma olurdu (D-260), tanim SSOT'un var olan parcalarindan turetildi. **KOK BULGU: 7 musteri sorusunun 4'une cevap veremiyoruz** ve eksik olan ekran degil **kaynakta veri**. Olculenler: `annual_turnover` semada **kolon degil** (sadece 0018:18 yorumu); `companies.employee_count` var ama 0024:22 "0 dolu -> hepsi NULL"; vergi/SGK borcu tutan **hicbir tablo yok**; ortaklik bilgisi yok. `company_risk_scores`'in 8 kolonu semada VAR (0046) ama **hesabi yok** (D-238) -> NULL = "olculmedi", 0 degil (D-249). **D-245 curutme:** brif ornegi `companies.vkn` yaziyordu, diskte oyle kolon **YOK**; kanonik ad `companies.tax_number` (0001_core.sql:39). Cikti: **8 denetim sorusu** (S1-S8), **8 eksik veri kaynagi** (Engel kolonunda bos hucre YOK; 6'si "bilmiyorum"), **3 yol** + **<- ONERIM: Yol B** (Yol A bos tablo uretir = D-249 sessiz yalani; Yol C hukuki karar gerektirir D-257), **3 oz-eleştiri maddesi**. **Faz B kapisi GECTI:** 19 kolon + 9 tablo adi `migrations/*.sql` icinde grep ile dogrulandi. SSOT satir sayisi olculdu: 1687 (brif varsayimi dogru). Sonraki gorev: **Faz 2 hesaplama** (Yol B on kosulu). Belge: `docs/FAZ5_VENDOR_DUE_DILIGENCE_KAPSAM.md` | 2026-10-02 |
| DOC-GLOBAL-INTEL-ARASTIRMA-01 | **Faz 6 "kuresel" hedefi arastirildi - KOD YAZILMADI (brif: kapsam disi).** SSOT'ta Faz 6'nin tum icerigi **3 satir** (`HUGIns.txt:871-873`); Nihai Misyon 3 soru (`875-885`). **D-66 kapisi 5/5 tuttu:** SSOT **1687 satir** (brif ~1687 dogru), 871-873 + 875-885 + 11-17 (7 soru) + 25-32 (8 kitle) teyit edildi. **FAZ A olculdu:** `osb_veri_denetim.py` -> **8987 kayit / 8296 tekil / 44 mukerrer / 647 kimliksiz / 0 mojibake**; `--self` muhasebe ok (8296+44+647=8987), `--kontrol 8987` **exit 0**. **D-260 tuzagi:** 8987 `data/osb/` ham kazimadir, **`companies` degildir** (9412, D-263/D-267 - bu turda YENIDEN olculmedi, tarihli kaynak). **KOK BULGU: `companies` tablosunda ulke kolonu YOK** (0001_core.sql:34-62, 26 kolon tamami acildi) - "hangi ulkeyi kapsiyoruz" sorusu **sorguyla degil tahminle** cevaplaniyor. Uc bagimsiz kanit: 12 kaynagin **12'si de Turk OSB'si**, `is_ankara BOOLEAN` (0001:49), `is_osb_member`/`osb_id` (0001:50-51). **Beklenmedik bulgu:** ulke kolonu yok ama projede **zaten iki tutarsiz ulke gelenegi var** - `job_postings.location_country TEXT DEFAULT 'Turkiye'` (0013:20) ile `user_activity_log.ulke_kodu CHAR(2) NULL` ISO 3166-1 alpha-2 (0017:20). Dogru bicim var, yanlis bicim var, ikisi de `companies`'a **tasinmamis** -> "ulke kolonu ekle" ucuncu gelenek olurdu (D-211). **5 engel:** E1 ulke kolonu yok + iki celisan gelenek · E2 `tax_number TEXT UNIQUE` VKN varsayiyor (9412 firmada **5** gecerli VKN, D-257) ama `company_identifiers` **cok bicimli ve genellenebilir bir defter zaten var** (0002:22-30) - genislemenin yeri `tax_number` degil · E3 NACE Avrupa'ya ozgu, **`naics` 50 migration'da 0 eslesme** (pozitif kontrol `nace`/`vkn` ile dogrulandi) · E4 `is_ankara` bir **soruya cevap veren kolon**; genel konum sorgusu `company_locations`'ta zaten var (0002:36-53) · E5 dil varsayimi Turkce: `normalize.py:602,681` + `kaynak_bagla.py:22` (8 Turk harfi). **2. cok onemli sapma:** (1) brifin E3 dizini **yanlisti** - `entity_resolution/*.py` icinde `maketrans` **0 eslesme**; gercek yer `api/core/normalize.py`. Bu turda "engel yok" yazsaydim D-266 hatasi olurdu. (2) Ilk `findstr` **bos** dondu ve "ulk kolonu yok" yazilmak uzereydi; **pozitif kontrol** (`vkn` -> 12 satir) PowerShell `\"` tirnaklama hatasini ortaya cikardi - **bos sonuc, saglam sonuc kadar guvenilir degildir**. **Faz B:** 3 olcek, her biri 5 madde; kaynak adlari **uydurulmadi** - D-257'nin olcumu MERSIS'in sorgu ekrani **yok**, TOBB API **401**, TSG captcha, GIB yonu **ters**; bu yuzden "kaynak adi arastirilmadi" yazildi (D-260). `companies.nace_code` yapisi genisletilmeden once NACE dogrulama borcu cozulmeli (D-252: kodlarin **%100'u tahmin**, gercek kod **0**). **Faz D:** 3 yol + **<- ONERIM: Yol A (ertele)**. Gerekce: E1-E5 veri eksikligi degil **oncelik** eksikligi; Yol B'nin bedeli zaten **olculmus** - D-249 / 0024 gocu 8140 sahte 0 buldu. Faz 5'in "Yol B" onerisiyle **celismiyor**: Faz 5 veriden cikan hesaplama, Faz 6 yeni ulke kapsami - ayni karar degil. **Faz E:** 4 oz-eleştiri; en zayif nokta **hukuki engeller olculmedi** (KVKK->GDPR, sinir otesi yeniden kullanim hakki). **6 ayri gorev** tablo halinde listelendi (acilmadi - pano baktimi orkestratorun, D-77). Belge: `docs/FAZ6_GLOBAL_INTEL_KAPSAM.md` | 2026-10-02 |
| TEST-SIMULASYON-B17-KIRIK-01 | **D-318 bulgu kapisi 3 testi kiritti; 1'i YANLIS SEBEPLE yesildi.** 	ests/test_gorev_kutusu_cli.py::test_cmd_teslim_basarili bulgu yazmadan teslim edemedigi icin kirmiziydi (1 failed / 16 passed) -> gk.bulgu.task_var_mi -> True monkeypatch. **Asil bulgu:** 	est_cmd_teslim_hata da ayni kapidan gecip yesildi, ama D-318 kapisi onden 
c=1 dondurdugu icin **cift teslim reddi hic denenmiyordu** - test hicbir sey olcuyordu. Kapik atlatmak kapiyi sessizce kapatabilir (D-309/3 + D-265/2 deseni). Cozum: kapinin kendisi icin 	est_cmd_teslim_bulgu_kapisi_reddeder eklendi; kapik kirlarsa iki test kirmizi yanar. Kanit: cli **18 passed**, simulasyon 4 passed -> **22 passed**. gorev_kutusu.py simulasyon cikis **1** (uyari: 37 gorev hafiza izsiz; hata degil, D-198). Kilitli olmayan 	ests/test_gorev_kutusu_hafiza.py ayni kok nedenle 2 kirmizi - dokunulmadi, TEST-GOREV-KUTUSU-HAFIZA-D318-01 olarak kayit altina alindi. Rapor: data/orchestrator/TEST-SIMULASYON-B17-KIRIK-01_rapor_2026-10-03_uretim.md | 2026-10-03 |
| VERI-OSTIM-HREF-FILTRE-01 | **OSTİM `web_sitesi` alanı kaynakta YOK; 1555 dolu kaydın 1555'i OSB portal adresi (yanlış-pozitif %100).** **KÖK BULGU 1 — ölçüm aracı kural kopyası taşıyordu:** `scripts/ostim_href_olc.py` üreticiden ayrı `KOTU_DESEN` regex'ini taşıyordu (D-211 ikiz yapı) ve **kendi hatasını gizledi**: brief regex'inde `nsosyal.com` yok, ölçüm 140 (%9) dedi, gerçek 1555 (%100). **KÖK BULGU 2 — pilot seçimi de kırıktı:** tek seferlik `python -c` + ASCII regex; Python `re.IGNORECASE` U+0130 (İ)↔ASCII I eşleşir ama U+015E (Ş)↔ASCII S **eşleşmez** → ölçüm eski 385 vs normalize 991, **606 A.Ş. firma sessizce elendi**. **DÜZELTME:** `WEB_BLOCKLIST` 9→36; etiket-ankrajı (`_etiketten_site`) — etiket yoksa NULL, tahmin yok; kök URL kabul, `/index.htm` red; ölçüm aracı artık **üreticiden ithal** ediyor; `scripts/ostim_pilot_firma_sec.py` (Unicode normalize + şube elemesi) ve `scripts/ostim_pilot_denetim.py` (D-292 canlı denetim) kalıcı araçlar. **KANIIT:** hedefli pytest **24 passed**; kırma denemesi `nsosyal.com` bloklistten çıkarıldı → **4 kırmızı** (mandal gerçekten kırılıyor); 10/10 canlı sayfa HTTP 200, **0/10** `Web Sitesi` etiketi, sayfa başına 33-34 portal adresi (`nsosyal.com/ostim_osb` 1415, `ostimonline.com/Home/OstimMain` 140); 969 uygun A.Ş. → 100 pilot → 0 dolu, 0 yanlış-pozitif. **KAHİN KARARI: kanonik 1555 satıra DOKUNULMADI** (hazır araç `scripts/ostim_websitesi_temizle.py --yaz`, yedekli). **AÇIK KAPI:** `run_scraper()` slug'ı `completed_slugs`'te gördüğü için bozuk satırlar **asla** yeniden çekilmez — filtre düzeltmesi tek başına diskteki değerleri düzeltmez. **ÖNERİ:** (1) alan bu kaynak için kapansın/ayrı zenginleştirmeye bağlansın (MERSIS kapalı, TOBB 401 — D-257); (2) "ilk `http` adresi" deseni **tüm OSB kazıyıcılarında** aranmalı; (3) `scripts/` altındaki diğer ölçüm betikleri kural taşıyor mu denetlensin. **KAHİN KARARI (2026-10-03, ÖLÇÜM DAYALI — tahmin değil):** canlı Supabase 10123 firma ölçüldü: dolu 5446 (%53,8) ama **2666'sı kaynak sızıntısı** (`isim.org.tr` 2142, `ostimistihdam.com` 474, `ostimonline.com` 50) → gerçek olabilir **2780 (%27,5)**, boş **4677 (%46,2)**; boşluğun sebebi ölçüldü: ASO/OSTİM/İvedik/Baskent üye listeleri web sitesi alanı **yayınlamıyor**. Seçilen karar: **(a) alan global kapanmaz** (2780 gerçek site de giderdi) → **kaynak bazlı kapatma** (OSB/oda portal domain'i `website_domain`'e yazılmaz, ham değer `source_records.raw_payload`'de kalır — D-246/4) + **alan açık kalır** + **ayrı zenginleştirme görevi**. **Puan etkisi ölçüldü:** `website_domain` ağırlığı **0,3/10 = %3**; tam kapsama ortalama 3,71 → ~3,85 (**+%3,8**) → görev **P2**; karşılaştırma `tax_number` 1,5 → **15177 puan**, `address` 5424, `primary_email` 3770 → VKN kaynağı (+%40) 5 kat daha büyük. Yan ölçüm: sahteleri temizlemek ortalamayı **düşürür** (3,71→3,63), 2666 firma haksız 0,3 puan alıyor — D-245 düzeltmesi. **AÇILAN GÖREV:** `VERI-WEB-SITESI-ZENGINLESTIR-01` (unvan → arama → canlı HTTP 200 + içerik doğrulama → kaydet), brif `plans/brief_utku_VERI-WEB-SITESI-ZENGINLESTIR-01.md`, D-66 kabul kriterleri + 5 sabit varsayım; **utku D-58 kapısıyla açamadı** (`aktif: ihsan, cagiran: utku` reddi) → kopyala-yapıştır komutu `ajan_chat.py` ile ihsan'a iletildi. Rapor: data/orchestrator/VERI-OSTIM-HREF-FILTRE-01_rapor_2026-10-03_uretim.md | 2026-10-03 |
| VERI-APIFY-BUTCE-01 | **Apify aylık kullanımı ÖLÇÜLDÜ: 0.0000148799 USD / 10 USD tavan (%0.0001); konsol tavanı API'den geri okundu ve **zaten 10 USD** — brifin 'ayarla' varsayımı yanlıştı, konsola dokunulmadı (D-66/D-260).** Ölçüm aracı `scripts/apify_butce_olc.py` (GET-only, token stdout'a sızmaz, bilinmeyen değer `0` yazılmaz → `rc=3`; tavan aşımı **ve** platform tavanı > yerel tavan → `rc=2`). **ÖLÇÜLEN ALAN ADLARI tahmin değil canlı yanıttan:** `users/me/limits` → `data.current.monthlyUsageUsd` + `data.limits.maxMonthlyUsageUsd`; yedek `users/me/usage/monthly` → `totalUsageCreditsUsdAfterVolumeDiscount`. **2 HATA YOLDA YAKALANDI:** (1) `.env` `APIFY_API_BASE_URL` `/v2` ile bittiği için eklenen `/v2` `/v2/v2` yapıp **404** döndürdü — 'ölçülemedi' görünüyordu ama sebep yol hatasıydı, yani kırmızı sonuç yanıltıcıydı (D-309/3); `api_kok()` ile düzeltildi. (2) float repr değeri `1.41192e-05` basıyordu, test yakaladı → Decimal sabit nokta. **GERÇEK FATURA RİSKİ 0 USD:** plan `FREE`, `isPaying=false`, taban ücret 0, aylık kredi 5 USD; 10 USD tavanı **yükseltme sonrası** güvenlik sınırı (ücretsiz planda platform kredi bitiminde durur). `actorCount=0` → henüz hiç Actor çalışmamış, tek harcama dış veri transferi 0.00007 GB. Fatura döngüsü takvim ayı değil hesap açılışına sabit (2026-09-10 → 2026-10-09). **KAPI:** 17/17 test yeşil, kodlama denetimi temiz (yalnız önceden var olan mojibake/9Router ihlalleri kaldı, dokunulmadı). Belge: `docs/APIFY_BUTCE.md` | {TARIH} |
