# Admin Dashboard Hub

> Konu-bazli hub (PO karari 2026-09-21): Admin/Muninn paneli ile ilgili tum stratejik,
> mimari ve tasarim dokumanlari tek noktada. Yurutme raporlari (data/orchestrator/ADMIN-*_rapor*)
> bu hub'a dahil edilmedi — gurultu onlemek icin yalnizca karar/mimari/tasarim seviyesi belgeler secildi.

Uretim: Sprint Graf Hub'lastirma FAS-2 (2026-09-21). Bagli dokuman: **28** (2026-09-24: gorev taslagi + 10 brief eklendi)

Ana baglam: [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]] · [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]] · [[Huginn Data Insights/hubs/REPORTS_ANALYSIS_HUB]] · [[Huginn Data Insights/hubs/OSINT_INDEX]] · [[Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB]] · [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]] · [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]] · [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]] · [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]] · [[Huginn Data Insights/AGENTS]] · [[Huginn Data Insights/PROJECT_ROADMAP]] · [[Huginn Data Insights/hubs/V10_POC_HUB]]

---
### SCRAPE-004-QWEN-SINIFLANDIRMA — LLM sınıflandırma (yasu, 2026-10-04)

`scripts/kazima_qwen_classify.py`

- Yapısı bilinmeyen sayfaları NACE + unvan için sınıflandırır.
- **D-245 (kritik):** hiçbir model çalışmazsa veya cevap JSON değilse
  **uydurma etiket yazılmaz** → `nace_kodu=None`, `etiket_bos=true`.
- **Model zinciri:** tek model denenmez; sırayla denenir. Sağlayıcı
  anahtarı değişse kod değişmez.
- Canlı ölçüm: `clinepass/cline-pass/mimo-v2.5` → NACE **74.90**
  (İş Güvenliği ve Danışmanlık). Qwen modelleri 503 döndü.
- Metin 3 000 karaktere kirpilir (maliyet + KVKK).
- Test: `tests/test_kazima_qwen_classify.py` — 11 passed.

---
### SCRAPE-003-9ROUTER-JINA-FALLBACK — Jina-Reader fallback (yasu, 2026-10-04)

`scripts/kazima_jina_fallback.py`

- Doğrudan `requests` kilitlenince (DNS, 403, zaman aşımı) 9Router
  `/v1/web/fetch` (Jina-Reader) ile yeniden dener.
- **Vekil koruması:** izin reddi varsa Jina **hiç denenmez** — vekil
  reddedilmiş sayfayı getirirdi. Canlı ölçüm: `baskentosb.org.tr`
  robots.txt çözülemiyor → izin yok → Jina çağrılmadı.
- **D-245:** yapı bilinmiyorsa `kart_tipi=None` yazılır; "0 firma" ile
  aynı değildir.
- **D-288:** `NINEROUTER_KEY` hiçbir çıktı/loga yazılmaz.
- Canlı: `ostim.org.tr/firmalar` → 300 kart / 336 783 bayt, `yazilan=1`;
  2. koşu `yazilan=0` (idempotans kanıtlandı).
- Test: `tests/test_kazima_jina_fallback.py` — 9 passed.

---
## Kapanan işler

### ALTYAPI-AJAN-CAKISMA-01 — Kilit kapısı (yasu, 2026-10-03)

`scripts/ajan_cakisma_kilidi.py`

- **Kök neden:** FAZ-0 sırasında 130 dosya taşınırken kilit sorgulanmadı.
  Panoda görev görünmemesi, dosyanın boşta olduğu anlamına gelmiyor.
- **Var olan ne yapıyordu:** `kilit_zorla.py` kilidi **commit anında** zorlar.
  Zarar commit'ten önce diskte oluşur → kapı geç kalır.
- **Yeni:** sorgu + kapı (`--ajan`, `--kayitli-son`, `--denetle`,
  `--hareket-uyari`); `kapi_gecer()` geri çağrılabilir fonksiyon.
- **Tek kaynak (D-211):** `ajan_kimligi` / `bayat` / `KILIT` `kilit_zorla`dan
  alınır, kopya yoktur.
- **Ölçüm:** `--ajan yasu` → 10 aktif kilit · `tests/conftest.py` → rc=3 red
  (salih) · kendi kilidi → rc=0 · bayat kilit (24 saat) düşer (D-303).
- **Test:** `tests/test_ajan_cakisma_kilidi.py` — 12 passed.

---

## Kaynak / Sistem Referansi

- [[Huginn Data Insights/docs/ADMIN_UI_SISTEMI]] — Ana referans: tum admin sekmelerinin kod haritasi
- `Huginn Data Insights/AI proje v1/V10/wiki/admin_panel_kilavuz` — Kullanim kilavuzu

## Mimari Kararlar

- [[Huginn Data Insights/docs/ARCHITECTURE_DECISION_HYBRID_ADMIN]] — Hybrid Admin Panel karar dokumani
- `Huginn Data Insights/AI proje v1/V10/03_mimari/02_muninn_super_admin_panel_prd_ve_yol_haritasi` — PRD + yol haritasi
- `Huginn Data Insights/AI proje v1/V10/03_mimari/06_muninn_prd_vs_huginn_analiz` — PRD vs mevcut durum analizi
- `Huginn Data Insights/AI proje v1/V10/03_mimari/ADMIN-01-02-03_TASK_BRIEF` — Faz 0 gorev dagitimi

## Plan / Yol Haritasi

- [[Huginn Data Insights/docs/MUNINN_STREAMLIT_PLAN_2026-09-18]] — Muninn Streamlit plani
- [[Huginn Data Insights/docs/MUNINN_PLAN_UC_TUR_DEGERLENDIRME_2026-09-18]] — Uc tur degerlendirme
- [[Huginn Data Insights/plans/MVP_ADMIN_minimum_canli]] — Minimum canli MVP plani
- `Huginn Data Insights/AI proje v1/V10/13_po_karar_analizi` — PO karar destek analizi (metrik yonetimi)
- `Huginn Data Insights/AI proje v1/V10/14_urun_yuzeyleri_sitemap` — Urun yuzeyleri sitemap (Muninn/Huginn ayrimi)

## UX / Tasarim

- [[Huginn Data Insights/docs/UX_ADMIN_PANEL_REVIEW_2026-09-14]] — UX audit + premium arayuz plani
- [[Huginn Data Insights/docs/UX_ANA_SAYFA_WIREFRAME_2026-09-18]] — Ana sayfa wireframe
- [[Huginn Data Insights/docs/UX_AYARLAR_SAYFA_WIREFRAME_2026-09-18]] — Ayarlar sayfasi wireframe
- [[Huginn Data Insights/docs/UX_MENU_AGACI_WIREFRAME_2026-09-18]] — Menu agaci wireframe
- [[Huginn Data Insights/docs/UI_MODAL_CHART_ARASTIRMA_2026-09-15]] — Modal/chart arastirmasi
- [[Huginn Data Insights/docs/ADMIN_8SAYFA_VIZYON_KAPSAM]] — Vizyon 8 sayfa boslugu (HUGIns.txt §2440-2987 vs kod); KK-12 A′ karari, gorev 34-38 kaynagi (2026-10-03)

## Uygulama Tasarim Zinciri (2026-09-20)

- `Huginn Data Insights/data_worktree/orchestrator/ZINCIR-ADMIN-PANEL-UX-TASARIMI_2026-09-20_orkestrator` — UX zincir tasarimi (menu, profil, logout)

## Gorev Uretim Taslagi (2026-09-24, kalici)

- [[Huginn Data Insights/data/orchestrator/gorev_taslagi]] — **Kalici gorev taslagi**: acik gorev sayaci (P0/P1/P2), ana + yedek gorevler, tur kaydi. Her yeni gorev turunda once bu dosya okunur (tekrar onleme).

## Gorev Brief'leri — Tur 2026-09-24 (ADMIN-KIT · SSOT tabanli)

| # | Brief | Oncelik | SSOT kaynagi |
|---|-------|---------|--------------|
| 13 | [[Huginn Data Insights/plans/brief_utku_VERI-ADMIN-AKTIVITE-LOG-13]] | P0 | §8.4 EK BULGU-8 · §10:366 · §12 G2 |
| 14 | [[Huginn Data Insights/plans/brief_utku_API-ADMIN-AKTIVITE-YAZ-14]] | P0 | §8.4 EK BULGU-8 · §12 G2 |
| 15 | [[Huginn Data Insights/plans/brief_utku_DOC-ADMIN-DURUM-SENKRON-15]] | P1 | §8.4 · §10 · §14 tutarsizligi |
| 16 | [[Huginn Data Insights/plans/brief_utku_API-ADMIN-CHURN-3SINYAL-16]] | P1 | §9 K1 · §10:368 · §12 G2 |
| 17 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-DAU-17]] | P1 | §8.1 A9 · §10:369 · §12 G4 |
| 18 | [[Huginn Data Insights/plans/brief_utku_API-ADMIN-KAYNAK-SAGLIK-18]] | P1 | §9 K4 |
| 19 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-CRAWL-KONTROL-19]] | P1 | §8.1 A8 · §10:373 · §12 G8 |
| 20 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-ARAMA-BOSLUK-20]] | P2 | §9 K9 · §10:375 |
| 21 | [[Huginn Data Insights/plans/brief_utku_API-ADMIN-SUPHELI-AKTIVITE-21]] | P2 | §9 K10 · §10:374 · §12 G9 |
| 22 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-UPSELL-22]] | P2 | §9 K7 |

SSOT: `Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani` (ADMIN-KIT, D-196)

## Gorev Brief'leri — Tur 2026-10-03 (ADMIN-KIT · KK-12 A′ · Veri Kaynaklari sayfasi)

| # | Brief | Oncelik | Oncul | SSOT kaynagi |
|---|-------|---------|-------|--------------|
| 34 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-KAYNAKLAR-SAYFA-34]] | P1 | -18 (kapandi) | §11 KK-12 K1/K6 · §12 G8 · §9 K4 · §7 Kaynak sagligi |
| 35 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-CRAWL-TASI-35]] | P1 | -19 (kapandi), -34 (kapandi) | §11 KK-12 K1b · §12 G8 · §7 Crawl yonetimi |
| 36 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-SON-KAZIMA-KART-36]] | P2 | -34 (kapandi), -35 (kapandi) | §11 KK-12 K1c · §12 G8 · §7 Ana Kontrol giris karti |
| 37 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-ACIKLAMA-METIN-37]] | P2 | — | §11 KK-12 K3 |
| 38 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-REHBER-ALAN-38]] | P2 | 36'nin `ana_kontrol.py` metni bekledi (teslim edildi) | §11 KK-12 K4 |

Zincir: 34 → 35 → 36 (sira zorunlu). 37 → 38 ayri zincir; ikisi de `web_dashboard/tabs/__init__.py` kilidini paylastigi icin 34 teslim edilmeden baslamaz, 38 ayrica `ana_kontrol.py` icin 36'yi bekler. Kaynak belge: [[Huginn Data Insights/docs/ADMIN_8SAYFA_VIZYON_KAPSAM]] §"Bu belgeden cikan ayri gorevler".
Ayni turda acilan bulgu gorevi (ADMIN disi): [[Huginn Data Insights/plans/brief_utku_VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01]] (P2, hub: VERI_KALITESI_HUB).

## Kapanan isler (B-14 · hafiza izi)

> Kapanan her gorev buraya bir satir birakir. `gorev_kutusu.py teslim` bu bolumde
> task_id gormezse teslimi reddeder (`--zorla` ile gecilebilir, panoya `hafiza_izi=atlandi` islenir).
> Asagidaki satirlar TUR-B2 (2026-09-24) ile geriye donuk yazildi — denetim B-14 borcu.
> Kapi `HAFIZA_KAPISI_YURURLUK = 2026-09-24` esiginden once kapanan isleri tek tek
> aramaz; onlarin karsiligi asagidaki ceyreklik arsiv baglantisidir (D-186, D-198).

| task_id | Ne kapandi | Bitis |
|---------|------------|-------|
| ALTYAPI-ODIN-MASKE-V3-01 | `maskeleme_odin()`e **kaynak (surum) parametresi** eklendi: `sunum.py:339` imzasi, `sunum.py:304-310` `ODIN_KAYNAK_MUSTERI`/`ODIN_KAYNAKLAR`/`ODIN_KAYNAK_TANIM`, `sunum.py:314` `odin_kaynak_dogrula()` (bilinmeyen kaynak **fail-closed** -> `v3`), `sunum.py:375` **V3 musteri cikis kapisi** `odin_musteri_cikis_kapisi()` (maske + K4 olcumu ayni yanitta; FastAPI route degil — modul bagimlilik yasak, route bu fonksiyonu cagirir). OLCUM: V1/V2/V3 ayrimi repo'da **tanimli degil** (`git grep -E '\bV[123]\b' -- '*.py'` → 0; tek gectigi yer `docs/ODIN_DEPLOYMENT_ARCHITECTURE.md:78-82`) — bu yuzden V1/V2'ye **gevsek alt kume ATANMADI** (D-224), fail-closed uygulandi; `sunum.py:313-333` ozel bolumu. HTTP route kapsami KAHIN'e ajan chat ile soruldu (2026-10-04T18:43Z). Test: `tests/test_odin_kapi_olcumu.py` 20 -> **28 passed** (+8 yeni kaynak/V3 kapisi testi); tam paket HEAD'de **25 failed / 5411 passed**, degisiklik sonrasi **23 failed / 5421 passed** → **regresyon yok** (fark +/-2 `test_mcp.py::TestApifyAdapter` flaky testi). | 2026-10-04 |
| VERI-INGEST-ASO-GLOB-01 | ASO ingest iki kok neden duzeltildi. (1) `glob(*.csv)+glob(*.json)` yalniz kendi urettigi `aso_full_clean_report.json` rapor dosyasini buluyordu; ham `aso_full.jsonl` (1091 satir) HICBIR ZAMAN okunmamisti -> `KAYNAK_DOSYA` sabiti + `unvan->legal_name` + `ON CONFLICT DO NOTHING` + `tax_number` yazilmiyor (D-246). (2) `refresh_pipeline.py:85` modulu `src.` onekle ice aktarirken mutlak `company_master.*` importlari `ModuleNotFoundError` veriyordu -> kardes modul `normalize.py` ile birebir ayni goreli desen; import yolu 3/4 -> 4/4. Canli Supabase: 1091 okundu -> 722 yazilabilir -> 2 kosuda 0 eklendi (idempotens), companies 10123 sabit, bos unvan 0, Ankara OSB uye 10120. 69 test yesil; `TestImportKoku` mandali kirilarak dogrulandi (2 failed -> 16 passed). 722/722 ASO unvani DB'de ZATEN var -> gorev yeni firma eklemedi, [3/4] yesil + idempotent deger uretti. ACIK: data/aso/ uc varyant ikizi + scripts/ingest_aso_data.py ile ikiz ingest yolu (D-211, ayri gorev); scripts/ninerouter_anahtar_guncelle.py:60 soz dizimi hatasi (9Router yasagi nedeniyle dokunulmadi). | 2026-10-03 |
| VERI-OSTIM-TAM-TARAMA-01 | 3.338 kayit tarandi (1 x 404 atlandi). 0 hata, 0 mukerrer slug, 0 K-2 kacisi. Adres %97,2 / telefon %91,6 / e-posta %91,4. Kaynak SHA-256 ayni, companies 8.313 sabit. D-296 surucu + D-298 asili istek duzeltmesi. Test 115 passed, commit 8cfbd9f. | 2026-09-29 |
| ALTYAPI-SKILL-YAPISI-01 | Skill sistemi tek havuzda birlestirildi: `skills/{tools,services,utils,prompts}` + `.agents/skills` (33 SKILL.md); kırık paket imzalari duzeltildi, `devops_agent` 9Router'a gecirildi (anthropic SDK hic eklenmedi), kopya/boş ajan dizinleri junction yapildi, `.kilo/skills` kaldirildi → `tests/test_skill_havuzu.py` 13 passed | 2026-09-29 |
| UI-ADMIN-SAHTE-KPI-01 | Sahte API KPI karti duzeltildi → `web_dashboard/tabs/admin_kpi.py` gercek rozet | 2026-09-24 |
| UI-ADMIN-SAHTE-EXEC-02 | Sahte gelir kartlari duzeltildi → `web_dashboard/tabs/admin_executive.py` | 2026-09-24 |
| UI-ADMIN-SSE-IHLAL-03 | SSE mimari ihlali giderildi → `web_dashboard/tabs/admin_realtime.py` polling | 2026-09-24 |
| VERI-ADMIN-LASTLOGIN-MIGRATION-04 | `users.last_login` kolonu → schema migration | 2026-09-24 |
| API-ADMIN-LASTLOGIN-YAZ-05 | Giris aninda `last_login` yazimi → auth akisi | 2026-09-24 |
| API-ADMIN-CHURN-FONKSIYON-06 | Churn risk saf fonksiyonu → `churn.py` | 2026-09-24 |
| UI-ADMIN-CHURN-KOLON-07 | Churn risk kolonu → `web_dashboard/tabs/musteri_yonetimi.py` | 2026-09-24 |
| UI-ADMIN-MAU-08 | Yanlis DAU etiketi MAU olarak duzeltildi → `admin_kpi.py` | 2026-09-24 |
| UI-ADMIN-KULLANICI-BIRLESTIR-09 | Uc kopya kullanici yonetimi tek modulde birlestirildi | 2026-09-24 |
| UI-ADMIN-GUNCELLIK-KOVA-10 | Veri guncellik kovalari → `web_dashboard/tabs/admin_quality.py` | 2026-09-24 |
| UI-ADMIN-MALIYET-ANOMALI-11 | AI maliyet anomali blogu (z-skor) → `web_dashboard/tabs/admin_cost.py` | 2026-09-24 |
| DOC-ADMIN-ARSIV-12 | Bayat analiz dokumani arsive tasindi + SSOT §0.1 guncellendi | 2026-09-24 |
| ORKESTRA-AI-CHAT-KOORDINASYON-01 | SISTEM_PROMPT + ajan_chat_koordinasyon.py library + testler + AJAN_ARASI_ILETISIM.md dok | 2026-09-24 |
| ALTYAPI-SECRETS-SETUP-01 | Credential vault kuruldu: .env.example, .env.vault, rotate_secrets.py, config_test.py | 2026-09-24 |
| ALTYAPI-DB-MIGRATION-01 | Migration altyapisi: db_migrate.py, 0017.down.sql, db_migrate_prod.sh, AlertManager kuralari | 2026-09-24 |
| ALTYAPI-ADMIN-PANO-01 | Task board guncel gorunum: render_task_board_tab, 4 bolum, filtreleme, testler, dok | 2026-09-24 |
| API-ADMIN-AKTIVITE-YAZ-14 | Giris/arama/AI olaylari loglandi: aktivite_yaz, web_app.py, 5 test | 2026-09-24 |
| API-ADMIN-CHURN-3SINYAL-16 | Churn 3 sinyalli formulu: risk_etiketi_3sinyal, musteri_yonetimi.py SQL guncellendi | 2026-09-24 |
| UI-ADMIN-ARAMA-BOSLUK-20 | Icerik bosluk raporu: admin_quality.py, normalize+frekans+eskik, rozet, testler | 2026-09-24 |
| API-ADMIN-SUPHELI-AKTIVITE-21 | Supheli aktivite 3 kural: admin_audit.py, skor+etiket, doctest+pytest gecti | 2026-09-24 |
| UI-ADMIN-UPSELL-22 | Upsell aday listesi: musteri_yonetimi.py, 3 kosul (doygunluk+churn+buyume), testler | 2026-09-24 |
| DOC-ADMIN-V9-KUTUCUK-24 | V9 §16.5 kutucuclari: 6 madde bullet listesi, format temizlendi | 2026-09-25 |
| UI-ADMIN-KVKK-MODU-26 | KVKK Mode sekmesi: render_kvkk_mode_tab, strict/lenient toggle, API POST, testler | 2026-09-25 |
| UI-ADMIN-KVKK-RAPOR-28 | KVKK Raporu sekmesi: render_kvkk_rapor_tab, admin_kvkk_mode, KPI, trend, testler | 2026-09-25 |
| DOC-VISIBILITY-KATMANI-29 | Visibility katmani dokumani: VISIBILITY_LAYER_GUIDE.md, Layer 1/2, modul kontor, karantina | 2026-09-25 |
| YASU-01 | React 18+ TypeScript Frontend Bileşen Kütüphanesi (base_ui.tsx): Button, Input, TextArea, Select, Card, Badge, Avatar, Modal (8 bileşen), TypeScript tipli, ARIA destekli, barrel export + Storybook config | 2026-09-26 |
| YASU-04 | Redux Toolkit store: redux_store.ts + 5 reducer (authSlice, uiSlice, dataSlice, settingsSlice, notificationsSlice), DevTools entegrasyonu | 2026-09-26 |
| YASU-02 | Responsive CSS: 4 breakpoint (320/768/1024/1280px), mobile-first, Grid/Flexbox, touch-friendly (min 44px), reduced-motion + dark mode | 2026-09-26 |
| YASU-03 | Dashboard görselleştirme: 6 grafik türü (Bar, Line, Area, Pie, Radar, Scatter) Recharts ile, responsive grid layout | 2026-09-26 |
| YASU-05 | WCAG 2.1 AA uyumu: wcag_compliance.md (16 kriter), audit_report.json (skor 97), 11/11 erişilebilirlik testi, Modal Escape+focus trap+aria-modal | 2026-09-26 |
| UTKU-03 | Hata loglama sistemi: error_handling.py (JSONFormatter, mask_sensitive, LogContext, handle_exception), web_app.py entegrasyonu (startup + global handler + middleware), 30/30 test, 5 gercek hata duzeltildi | 2026-09-26 |
| ALTYAPI-DB-MIGRATION-01 | Reddedilen 4 eksik kapatildi: (1) 0016/0017/0018 down.sql'lar ust seviyeye tasindi, (2) db_migrate.py'ye get_db_url/read_migration_file/migrate/verify_table_exists eklendi + psycopg2 opsiyonel, (3) db_migrate_prod.sh'de PROD_DATABASE_URL + pg_isready + dosya kontrolu, (4) 3 AlertManager kurali eklendi. 6/6 test | 2026-09-26 |
| DOKUMAN-KVKK-FAQ-33 | KVKK FAQ dokumani: docs/KVKK_FAQ.md, 7 SSS + 3 troubleshooting + 3 kod ornegi | 2026-09-25 |
| UI-ADMIN-FEATURE-FLAG-25 | Feature Flag sekmesi: render_feature_flags_tab, 4 flag, audit trail, testler | 2026-09-25 |
| COP-26 | MUSTERILER ekrani: firma listesi + filtre + bildirim blogu | 2026-09-24 |
| UI-SUBHEADER-MUSTERI-01 | `musteri_yonetimi.py` subheader temizligi (sayfa iskeleti sozlesmesi) | 2026-09-24 |
| TEST-ADMIN-PERF-01 | `admin_performance` kpi_karti gecis testi | 2026-09-24 |
| TEST-WEBHOOK-KPI-01 | `tests/test_webhook_monitor_tab.py` mock hedefi duzeltildi | 2026-09-24 |
| TEST-BLOKE-FAKTOR-ARASTIRMA-01 | Test hazırlık araştırma ve test skeletleri oluşturuldu | 2026-09-24 |
| API-ADMIN-KAYNAK-SAGLIK-18 | Kaynak sağlık skorunu ölç → 3 kovalı rozet + DLQ birikme hızı | 2026-09-24 |
| UI-ADMIN-CRAWL-KONTROL-19 | Crawl tetikle/durdur aksiyonunu yaz → operatör kontrol paneli | 2026-09-24 |
| TEST-ADMIN-K2-AGIRLIK-23 | K2 ağırlık şemasını denetle → test + SSOT kanıt | 2026-09-24 |
| DOC-ADMIN-DURUM-SENKRON-15 | Bayat durum satırlarını düzelt → §8.4/§10 kanıtlı (SSOT senkronize) | 2026-09-24 |
| ALTYAPI-VERI-GORUNURLUK-01 | Katmanlı görünürlük & kontör sistemi: 0018 migration (3 tablo), normalize.py dict, web_app.py SELECT düzelt, test 5+4 | 2026-09-24 |
| API-ADMIN-AKTIVITE-YAZ-14 | Giris/arama/AI olaylari loglandi: aktivite_yaz, web_app.py, 5 test | 2026-09-24 |
| API-ADMIN-CHURN-3SINYAL-16 | Churn 3 sinyalli formulu: risk_etiketi_3sinyal, musteri_yonetimi.py SQL guncellendi | 2026-09-24 |
| UI-ADMIN-ARAMA-BOSLUK-20 | Icerik bosluk raporu: admin_quality.py, normalize+frekans+eskik, rozet, testler | 2026-09-24 |
| API-ADMIN-SUPHELI-AKTIVITE-21 | Supheli aktivite 3 kural: admin_audit.py, skor+etiket, doctest+pytest gecti | 2026-09-24 |
| UI-ADMIN-UPSELL-22 | Upsell aday listesi: musteri_yonetimi.py, 3 kosul (doygunluk+churn+buyume), testler | 2026-09-24 |
| DOC-ADMIN-V9-KUTUCUK-24 | V9 §16.5 kutucuclari: 6 madde bullet listesi, format temizlendi | 2026-09-24 |
| ALTYAPI-SECRETS-SETUP-01 | Credential vault kuruldu: .env.example, .env.vault, rotate_secrets.py, config_test.py | 2026-09-24 |
| ALTYAPI-DB-MIGRATION-01 | Migration altyapisi: db_migrate.py, 0017.down.sql, db_migrate_prod.sh, AlertManager kuralari | 2026-09-24 |
| UI-ADMIN-FEATURE-FLAG-25 | Feature Flag sekmesi: render_feature_flags_tab, 4 flag, audit trail, testler | 2026-09-25 |
| UI-ADMIN-LTV-CAC-27 | LTV/CAC analiz sekmesi: render_ltv_cac_tab, KPI + trend + tier breakdown, testler | 2026-09-25 |
| DOC-ADMIN-MULTITENANT-KARAR-28 | Multi-tenant karar belgesi: MULTITENANT_ARCHITECTURE_DECISION.md, 3 model karsilastirmasi, migration path, security checklist | 2026-09-25 |
| ADMIN-UX-GELIR-GRUP-01 | Gelir grubu: GRUP_GELIR + executive+maliyet sekmeleri (ust=gelir, sira=1/2) | 2026-09-25 |
| UI-ADMIN-FEATURE-FLAG-25 | Feature Flag sekmesi: render_feature_flags_tab, 4 flag, audit trail, testler | 2026-09-25 |
| UI-ADMIN-LTV-CAC-27 | LTV/CAC analiz sekmesi: render_ltv_cac_tab, KPI + trend + tier breakdown, testler | 2026-09-25 |
| DOC-ADMIN-MULTITENANT-KARAR-28 | Multi-tenant karar belgesi: MULTITENANT_ARCHITECTURE_DECISION.md, 3 model karsilastirmasi, migration path, security checklist | 2026-09-25 |
| VERI-NACE-KOLON-01 | nace_validity kolonu duzeltme: 86 satir duzeltme, nace_validity gecerlilik etiketi (unknown/medium/fallback) | 2026-09-27 |
| VERI-NACE-TEMIZ-01 | Sektor sayaci kirlenmesi temizlendi: 13 gecersiz kod (1163, 410, 780, 794, 757, 110, 114, 127, 192, 339, 380, 390, 410, 752, 757, 780, 794, 757, 339, 410), 555 firma NULL'a cekildi, invalid_cleared isaretlendi | 2026-09-27 |
| VERI-NACE-KOLON-01 | nace_validity kolonu duzeltme: 86 satir duzeltme, nace_validity gecerlilik etiketi (unknown/medium/fallback) | 2026-09-27 |
| VERI-HAYALET-TEMIZ-01 | 4591 hayalet kayit temizlendi, UNIQUE kisit kuruldu. Kusur: silme yedeksiz yapildi (D-244). vergi_no 774->761 farki kayip degil, mukerrer sayim erimesi. Detay: hubs/VERI_KALITESI_HUB.md | 2026-09-27 |
| TEST-BACKLOG-20 | Tam suite 20 failed -> 0: A=9 migration down, B=3 sayfa iskeleti, C=3 log, D=2 API rota, E=2 denetim, F=1 ayar; 6 faz, tek brif | 2026-09-27 |
| ADMIN-UX-GELIR-GRUP-01 | Gelir grubu: GRUP_GELIR + executive+maliyet sekmeleri (ust=gelir, sira=1/2) | 2026-09-25 |
| UI-ADMIN-FEATURE-FLAG-25 | Feature Flag sekmesi: render_feature_flags_tab, 4 flag, audit trail, testler | 2026-09-25 |
| UI-ADMIN-LTV-CAC-27 | LTV/CAC analiz sekmesi: render_ltv_cac_tab, KPI + trend + tier breakdown, testler | 2026-09-25 |
| DOC-ADMIN-MULTITENANT-KARAR-28 | Multi-tenant karar belgesi: MULTITENANT_ARCHITECTURE_DECISION.md, 3 model karsilastirmasi, migration path, security checklist | 2026-09-25 |
| VERI-NACE-KOLON-01 | nace_validity kolonu duzeltme: 86 satir duzeltme, nace_validity gecerlilik etiketi (unknown/medium/fallback) | 2026-09-27 |
| ADMIN-UX-GELIR-GRUP-01 | Gelir grubu: GRUP_GELIR + executive+maliyet sekmeleri (ust=gelir, sira=1/2) | 2026-09-25 |

Kapanan is sayisi bu hub'da: **34**. Tam liste ceyreklik arsivde:
`data/orchestrator/task_board_arsiv_2026-Q3.json`

---


| VERI-OSB-Tazelik-01 | [VERI] 13 Ankara OSB icin ayri veri seti uretildi: 8.987 kayit (data/osb/). Polatli Ticaret tarandi (+8 firma, tekil %100). Supabase YAZILMADI - orkestrator onayi bekliyor. 3 site DNS cozulmuyor, Sereflikochisar liste yayinlamiyor. Rapor: data/orchestrator/osb_rapor_2026-09-29.md | 2026-09-29 |
| SCRAPE-005-KAZIMA-DOCKER-INTEGRATION | [DOCKER] Kazıma servisi `jobs` profiline eklendi: yeni `src/company_master/scrapers/Dockerfile` (python:3.12-slim + psycopg healthcheck + CMD `scripts/refresh_pipeline.py`), compose'ta `depends_on db → service_healthy`, `CRAWL_ENABLED=1`, `deploy.resources.limits` (2 cpu / 2G). Briefin `curl localhost:5000/health` healthcheck'i ölçümle uydurma çıktı (0 referans) — uygulanmadı, PostgreSQL erişimi denetleniyor. Dosyadaki `scraper` servisi ikiz olduğu için yeni kopya yazılmadı, oneklendi (D-211). `docker compose config` exit 0, kodlama denetimi temiz, 15 test yeşil. **Canlı `up` doğrulaması yapılmadı: Docker daemon kapalı.** Rapor: data/orchestrator/SCRAPE-005-KAZIMA-DOCKER-INTEGRATION_rapor_2026-10-02_uretim.md | 2026-10-02 |
| SCRAPE-001-DOCKER-SETUP | Kazima denetim semasi canli: `scrape_audit_log` + `scrape_pages` + `scrape_errors`, migration **0050** (plandin 0046'si degil - 0046 `risk_skorlari` alinmisti, bos olan 0050'ye tasindi). `Diskte 50 goc / defterde 50 kayit`, 0050 TAM. Iki hata duzeltildi: (1) uc `information_schema` sorgusu `table_schema='public'` filtresizdi (D-253/4); (2) `veri-gocu:` + `dusen-iz:` beyanlari yalandi, kaldirildi (D-253/2). Idempotlik ham baglantiyla iki kosu kanitlandi, iz degismedi. D-261 `UNIQUE(source_url, content_hash)` + `CHECK(cost_usd=0)` yerinde. Docker canli: `db` healthy `postgres:16-alpine` 5433, API HTTP 200, Streamlit 8501 HTTP 200, psql 16.15, kodlama denetimi temiz. Brifin dogrulama komutu `scripts/_kazima_dogrula.py` 6/6 gecti. Eksik: telegram botu baslatilmadi (getUpdates yan etki), yerel konteyner DB bayat (14000 firma, 9/50 goc), SCRAPE-002 brif yolu gecersiz. Rapor: [[Huginn Data Insights/data/orchestrator/SCRAPE-001-DOCKER-SETUP_rapor_2026-10-02_uretim]] . Goc: [[src/company_master/schema/migrations/0050_scrape_audit_log]] | 2026-10-02 |
| SCRAPE-002-LEMMLESS-ANKARA-OSB | LLM-less kayıt katmanı canlı: 5 yeni dosya — [[src/company_master/etl/scrape_kayit]] (0050 tek yazıcısı), [[src/company_master/etl/scrape_kosu]] (ortak koşu iskeleti), [[scripts/kazima_ostim]], [[scripts/kazima_ivedik]], [[scripts/kazima_baskent]]. Kanonik scraper'lara **DOKUNULMADI** (D-235 sayfa_dongusu bozulmadı); kayıt katmanı **firma çıkarımı yapmaz** (D-211). **Canlı ölçüm (D-238):** scrape_pages=2, scrape_audit_log=5, scrape_errors=1, **yinelenen=0**, cost_usd sıfır dışı=0, llm_used TRUE=0. **İdempotens kanıtlandı:** 2. tur yazilan=0 / atlanan=1 (iki kaynakta da), aynı SHA256. **Ölçülen gerçek:** OSTİM 300 kart / 334267 bayt; İvedik 15 kart / 162159 bayt; **baskentosb.org.tr DNS'ten çözülmüyor** (Errno 11002) → izin reddi → scrape_errors kaydı, sessizce geçmedi. **Brif 3 yerde sapmış:** router imzası (get_router parametresiz, .check(url)→Decision), tablo seçicisi (OSTİM'de 0 table etiketi), scrape_errors kolonları (0050'da kaynak kolonu YOK, bağ yalnız audit_id FK). **Birim mandalı yazıldı:** `tests/test_scrape_kayit_mandali.py` 34 test (canlı DB'ye bağlanmaz). Kırırma denemesi yapıldı: `scrape_errors`'a 0050'da olmayan `source_name` kolonu geri konunca mandal kırmızı verdi. `audit_kaydet()` artık `audit_id` döndürüyor → hata kayıtları FK'siz kalmıyor (canlı: error_id=2 → audit_id=7, orphan=0). Idempotens **3. kez** doğrulandı: OSTİM+İvedik `yazilan=0/atlanan=1`, hash'ler değişmedi. Kalan borç: (a) çift HTTP okuma — tek çekim için kanonik scraper'a ham içerik kancası gerekir, kanonik dosyalara dokunulmadığı için açık; (b) yalnız liste sayfası arşivleniyor, 300 detay sayfası `scrape_pages`'te değil. Rapor: [[Huginn Data Insights/data/orchestrator/SCRAPE-002-LEMMLESS-ANKARA-OSB_rapor_2026-10-02_uretim]] | 2026-10-02 |
| UI-ADMIN-KAYNAKLAR-SAYFA-34 | "Veri Kaynakları" sayfası yazıldı: [[web_dashboard/tabs/admin_kaynaklar]] `render_kaynaklar_tab()`, 4 bölüm (Durum Özeti / Son Çalışmalar / Hatalar / Toplanan Sayfalar). 0050'nin **ilk okuyucusu** (D-236: `scrape_audit_log`/`scrape_errors`/`scrape_pages` yazılıyordu, hiç okunmuyordu). SECTIONS kaydı `__init__.py:369` → `ust="veri_kalite", sira=5, ikon=🕷️ (tekil), min_rol=admin`. **Yazma yok** — `etl/scrape_kayit.py::KazimaYazici` tek yazıcı kalır (mandal bunu metin taramasıyla korur). K4 rozeti canlı: `kaynak_guvenilirlik.hesapla()` + `saglik_rozeti()`. **Ölçüm (D-238, canlı Supabase):** `scrape_audit_log` **36**, `scrape_errors` **2**, `scrape_pages` **3** — sayfa okuyucularıyla birebir doğrulandı (5 kaynak · 36 çekiş · 12 başarılı · 2 hata · 3 sayfa). Brief varsayımları tuttu; **ölçek tuzağı** bulundu: `saglik_rozeti()` 0-1 bekler, `KaynakSaglik.skor` 0-100 → köprü `saglik_rozet_metni()`. Test: [[tests/test_admin_kaynaklar]] 10 passed + `test_dashboard_nav/test_tabs_ia/test_sekme_kapsama/test_sayfa_iskeleti` 309 passed. SSOT §7 satır 231 `Kısmi→Var`, §9 K4 satır 353 güncel. Rapor: [[Huginn Data Insights/data/orchestrator/UI-ADMIN-KAYNAKLAR-SAYFA-34_rapor_2026-10-04_uretim]] | 2026-10-04 |
| UI-ADMIN-CRAWL-TASI-35 | Crawl tetikle/durdur paneli [[web_dashboard/tabs/webhook_monitor]] `:236-302`den **[[web_dashboard/tabs/admin_kaynaklar]] `:359`**a tasindi: `_render_crawl_kontrolu()` — durum sabitleri (`CRAWL_STATUS_*`, `CRAWL_ENABLED`), `_crawl_is_enabled`, `_log_crawl_action` **tek tanim** (D-211 ikiz yasagi). Eski yerde yalniz `st.link_button` + `tab_getir("kaynaklar")` yonlendirmesi kaldi; `import os` cikarildi. Panel `Section(..., seviye=3)` alt basligi → D-213 menu tekligi korunur (BOLUMLER listesine girmez). Davranis degismedi: 4 durum ikonu, `crawl_enabled` kapisi, iki asamali onayli durdur, `admin_email` yetki kapisi, session_state anahtarlari ayni. SSOT §7 Veri Ops + §8.1 A8 `✅`, §12 `Kısmi→Tam`, §12 G8 `34✅→35✅→36`, surum v2.9. Test: [[tests/test_admin_kaynaklar]] 18 passed (8 yeni), kabul seti **213 passed / 2 skipped**; `findstr /C:"Crawl Kontrolü" webhook_monitor.py` = **0 satir**. Rapor: [[Huginn Data Insights/data/orchestrator/UI-ADMIN-CRAWL-TASI-35_rapor_2026-10-04_uretim]] | 2026-10-04 |
| UI-ADMIN-SON-KAZIMA-KART-36 | **KISMİ teslim.** [[web_dashboard/tabs/ana_kontrol]] `:85` `GIRIS_KARTLARI`'a `("🕷️","Veri Kaynakları","kaynaklar")` eklendi (5 kart); [[tests/test_ana_kontrol_overview]] `test_giris_kartlari_bes_kart_ve_veri_kaynaklari_var` eklendi. **Çizim yapılmadı — ölçüm:** `GIRIS_KARTLARI` repo genelinde yalnız tanım `:78` + test `:28` ile okunuyor, hiçbir fonksiyon onu render etmiyor; `render_ana_kontrol()` içindeki tek `st.link_button` = aksiyon şeridi b1 "Firmalar" (`:490`, K3-10f kararı). Bu yüzden "5. kart ekranda görünür" kriteri karşılanmadı; 3 seçenek ihsan'a açıldı (`ajan_chat` 2026-10-04T01:24) — (a) 5 kartlı satır → "Firmalar" ikizi (D-211), (b) aksiyon şeridine 6. link_button → 4 buton/4 renk tasarımı bozulur, (c) tuple'ı sil. **İkinci sapma:** brif `MAX(created_at)` diyor; ölçülen şema `0050_scrape_audit_log.sql:20` `timestamp` (çekiş zamanı) + `:32` `created_at` (satır ekleme) → doğrusu `timestamp`, `admin_kaynaklar.py:142` zaten onu kullanıyor. Caption + `son_kazima_zamani()` kararı bekliyor. SSOT §7 yeni satır + §12 G8 `34✅→35✅→36🟡`, sürüm v2.10. Test: kabul seti **204 passed / 3 skipped** (+130 ilgili). **D-210 teslim kapısı kendi kaydını saydı** (`kimden=utku` olmasına rağmen "açık sorun var" reddi) — D-321/2 ölçümüyle çelişen davranış; kayıt `cokundurmus` yapılınca teslim geçti (bulgu defteri). Rapor: [[Huginn Data Insights/data/orchestrator/UI-ADMIN-SON-KAZIMA-KART-36_rapor_2026-10-04_uretim]] | 2026-10-04 |
| UI-ADMIN-ACIKLAMA-METIN-37 | Menü ipuçları admin diline çevrildi: [[web_dashboard/tabs/__init__]] içindeki **37** `aciklama`'dan **24'ü** yeniden yazıldı (yalnız `aciklama=` string'leri — `anahtar`/`url_path`/`sira`/`ust` dokunulmadı, `ESLI_URL` bozulmadı). `KPI→ana göstergeler`, `DLQ→takılan işler`, `webhook→dış sistemden gelen haberler`, `ETL→veri yükleme`, `latency→gecikme süresi`, `ticket→destek talebi`, `churn/tenant→müşteri kaybı`, `tier→paket`, `feature flag→özellik anahtarı`. Hepsi ≤60 karakter (ölçüldü: 60+ = 0). **Mandal kelime sınırlı (`\b`) — düz alt-dize kontrolü meşru Türkçeyi jargon sayıyordu:** "Pak**etl**er" → "ETL" (ölçüldü, 1 yanlış pozitif). **Kırma kanıtı:** geçici "DLQ kuyrugu ve KPI dağılımı" → kırmızı, geri alındı → yeşil. Tüketici `app.py::render_topbar` `:616-618` `st.caption` değişmedi. SSOT §7 yeni satır, sürüm v2.11. Test: kabul seti **208 passed / 3 skipped**. Rapor: [[Huginn Data Insights/data/orchestrator/UI-ADMIN-ACIKLAMA-METIN-37_rapor_2026-10-04_uretim]] | 2026-10-04 |
| UI-ADMIN-REHBER-ALAN-38 | Sekme rehberi **tek kapıya** taşındı: `TabTanimi.rehber` alanı eklendi ([[web_dashboard/tabs/__init__]]), çizim tek noktada — [[app]] `:714-715` `st.info(tanim.rehber)`. Yedi sayfadaki gömülü `_hg_rehber` okuması **0**; metinler `kaynaklar`/`musteriler`/`ayarlar`/`canli_veri`/`ana_kontrol`/`musteri_onizleme`/`pazarlama` kayıtlarına taşındı. Beş **ölçülmüş** kök rehberi yazıldı (`sistem`, `denetim`, `musteri_yonetimi`, `proje_yonetimi`, `veri_kalite`) → **37 bölümün 12'si rehberli, yedi kökün tamamı rehberli**. Toggle (`app.py:758` `REHBER_KEY`) ve 7 metnin içeriği korundu (brifin sayıları teyit edildi). **Ölçülen yan etki:** `tests/test_admin_export_excel.py::test_sekme_rehberi_...` modül dosyasını okuduğu için taşıma sonrası **6 kırıldı** → kural gövdesi tek kaynağa bağlandı, dört-başık ratchet'i ayrı teste taşındı (D-246/D-260: refactor sonrası tam süreç bir kez çalıştırılır). **Mandal kırılarak doğrulandı** (`data/_tmp/rehber_mandal_kirma.py` rc=1, kaynak bayt bayt geri kondu). Test: [[tests/test_tabs_ia]] **7 yeni mandal** (11 -> 18), kabul seti **220 passed / 3 skipped**. Kodlama denetimi: bu görev dosyalarında **0** ihlal. **Davranış farkı:** denetim paneli `proje_yonetimi.py` içinde satır içi çağrıldığı için merkezî yaklaşımda **denetim rehberi yalnız `denetim` kökünde** görünür. SSOT §7 yeni satır, sürüm v2.12. Rapor: [[Huginn Data Insights/data/orchestrator/UI-ADMIN-REHBER-ALAN-38_rapor_2026-10-04_uretim]] | 2026-10-04 |
## İlgili Nodlar

- [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]]
- [[Huginn Data Insights/PROJECT_ROADMAP]]
- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]] — Kardes hub: Musteri/Huginn paneli (ayni urun, ayri kullanici kitlesi; kimlik dogrulama + kullanici yonetimi ortak)
