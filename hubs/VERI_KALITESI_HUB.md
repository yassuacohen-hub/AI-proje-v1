# Veri Kalitesi Hub

> Konu-bazli hub (PO karari 2026-09-21): Veri dogrulama, kalite metrikleri, test suitleri,
> ve kalite yonelmesi stratejileri tek noktada. Yurutme raporlari (data/orchestrator/TEST-*, BATCH-*_rapor*)
> dahil degildir — yalnizca strateji/metrik/politika seviyesi belgeler secildi.

Uretim: Sprint Graf Hub'lastirma FAS-2 (2026-09-21). Bagli dokuman: **16**

Ana baglam: [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]] · [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]] · [[Huginn Data Insights/hubs/REPORTS_ANALYSIS_HUB]] · [[Huginn Data Insights/hubs/OSINT_INDEX]] · [[Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB]] · [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] · [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]] · [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]] · [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]] · [[Huginn Data Insights/PROJECT_ROADMAP]] · [[Huginn Data Insights/hubs/V10_POC_HUB]]

---

## Kalite Metrikleri / Puanlama
- `Huginn Data Insights/AI proje v1/V10/12_kalite_metrikleri/01_kalite_skoru_ek_metrikleri` — Kalite skoru ve ek metrikler
- [[Huginn Data Insights/docs/PERF_TEMIZLIK_NOTLARI_2026-09-15]] — Performance ve temizlik notlari

## Test Suitleri / Stratejileri
- [[Huginn Data Insights/docs/plans/TEST-ISO-02_brief]] — Test isolasyon stratejisi
- [[Huginn Data Insights/docs/plans/TEST-CI-01_brief]] — CI/CD test pipeline
- [[Huginn Data Insights/docs/API_TESHIS_PLAYBOOK]] — API test playbook

## Batch / Toplu Islem
- [[Huginn Data Insights/docs/plans/BATCH-01_brief]] — Batch islem tasarimi 01
- [[Huginn Data Insights/docs/plans/BATCH-02_brief]] — Batch islem tasarimi 02

## Deployment / Guvenlik Testi
- [[Huginn Data Insights/docs/DEPLOYMENT]] — Deployment kilavuzu
- [[Huginn Data Insights/docs/plans/SEC-BANDIT-01_brief]] — Bandit (statik guvenlik analizi)
- [[Huginn Data Insights/docs/plans/SEC-AUTH-01_brief]] — Yetkilendirme testi

## Ajan Kalite / Rol Tanimi
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/05_kalite_ajan` — Kalite ajan rol tanimi
- `Huginn Data Insights/AI proje v1/V10/wiki/agents/kalite` — Kalite ajan wiki

## Versiyon Baglami
- `Huginn Data Insights/AI proje v1/V10/05_versiyonlar/01_versiyon_8_baglam_dokumani` — V8 baglam dokumani (kalite baglaminda)
- `Huginn Data Insights/AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani` — V9 baglam dokumani

## Tenant / Ortam Hazirligi
- [[Huginn Data Insights/docs/TENANT_HAZIRLIK]] — Tenant hazirlik belgesi

## Aktif isler
- [[Huginn Data Insights/plans/brief_utku_VERI-KOLON-IKIZ-01]] — **P0** kolon ikizi: `vergi_no`/`tax_number` + `web_sitesi`/`website_domain`. Eslestirme motoru 730 firmanin vergi numarasini gormuyor. FAZ 2 on kosulu.

---

## Acik Brief'ler (2026-10-03)
- [[Huginn Data Insights/plans/brief_utku_VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01]] — ASO ikiz ingest yolu birlestirme (P2, utku; kaynak bulgu `bulgu_defteri.md:134`, D-211)
- [[Huginn Data Insights/plans/brief_utku_VERI-WEB-SITESI-ZENGINLESTIR-01]] — website_domain zenginlestirme: 7343 bos alana gercek site + siteden telefon/eposta/adres (P2, utku; kaynak: VERI-OSTIM-HREF-FILTRE-01 raporu §10.1; sizinti goc 0052 ile kapandi, bkz. Kapanan isler; D-245/D-246)

## Ilgili Nodlar (Ust Hub)
- [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]]
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[Huginn Data Insights/PROJECT_ROADMAP]]

## Kapanan isler
| BORC-SITE-COP-01 (goc 0052) | website_domain sablon sizintisi DB trigger'iyla kapandi: [[Huginn Data Insights/src/company_master/schema/migrations/0052_website_sablon_kisiti.sql]] `companies_website_sablon` BEFORE INSERT/UPDATE, desen [[Huginn Data Insights/src/company_master/db/yazma_kapisi.py]] `SABLON_WEB_DESEN` ile birebir (mandal [[Huginn Data Insights/tests/test_website_sablon_kisiti.py]], kirilarak dogrulandi D-256/4). Yedek [[Huginn Data Insights/scripts/website_sablon_yedek.py]] (2666 satir, D-244). Sonra: 0 sablon / 7343 bos / 2780 gercek, 4 gercek alt-alan korundu (sinir regex). KOK NEDEN: `kabul()` hicbir uretim yolundan cagrilmiyordu (D-266) — hâlâ oyle, `primary_email` vb. kapisiz: [[Huginn Data Insights/docs/BORC_DEFTERI]] BORC-YAZMA-KAPISI-01 | 2026-10-04 |
| VERI-HAYALET-TEMIZ-01 | 4591 hayalet kayit silindi: 9412 satir, fazlalik 0, uq_companies_legal_name mevcut. vergi_no 774->761 farki KAYIP DEGIL — 774 kirli tabloda sayilmisti, tekillesmede mukerrer sayim eridi (D-244/4). KUSUR: silme yedeksiz yapilmis; yedek sonradan alindi (D-244) | 2026-09-27 |
| VERI-NACE-SOZLUK-01 | 3319 NACE kodu yuklendi (4 kaynak birlesimi), seviye korundu, eslesme %92.9 | 2026-09-27 |
| VERI-KAYNAK-BAG-01 | source_records.company_id kolonu eklendi, 5252 eslesme (37.5%), FK dogrulandi | 2026-09-27 |
| VERI-NACE-TEMIZ-01 | 7614 NN.NN format duzeltildi (raw_nace'ten turetildi), 675 altı haneli kırpildi, 25 iki haneli NULL'a cekildi, 1 yetim kod duzeltildi | 2026-09-27 |
| VERI-NACE-KOLON-01 | nace_validity duzeltildi: 0 NACE pattern kalan, 21 title_default -> medium, tum degerler valid etiket setinde (medium, unknown, fallback) | 2026-09-27 |
| VERI-SKOR-MOTORU-01 | Firsat motoru K4 resmi skor seti: migration 0049 + `company_opportunity_scores` (need/fit/timing/ensemble, 0.0-1.0 CHECK korumali, varsayilan NULL) + `intelligence/skor_motoru.py` (tek yazma kapisi `firsat_recalc()`). 35/35 mandal, 3/3 kirma kaniti. KISIT: `fit_score` F3 ETL'i gelene kadar `None` -> ensemble de `None` (BORC-F3-FIT-BOS-01); `evidence_strength` tabloda kolon degil, ensemble tabloyu yeniden uretemez (BORC-SKOR-EVIDENCE-01) | 2026-10-02 |
| VERI-RISK-MOTORU-01 | Risk motoru sekiz skorlu `company_risk_scores`: migration 0046 + `risk/skorlar.py` (tek yazma kapisi `risk_recalc()`), skor kolonlarinda `DEFAULT 0` yok (D-249), 11 COMMENT SSOT satiriyla, `recommendation_tier` turetilmis. 19/19 test yesil, D-249 mandali kirilarak dogrulandi (kirmizi cikti raporda). KISIT: skor hesabi calistirilmadi (D-238 ayri gorev); `schema_versions.json` 23'te donmus oldugu icin guncellenmedi (D-265+D-319 #22) | 2026-10-02 |
| VERI-INGEST-ASO-GLOB-01 | ASO ingest iki bagimsiz kok neden duzeltildi: (1) `glob(*.csv)+glob(*.json)` yalniz kendi urettigi `aso_full_clean_report.json` dosyasini buluyordu, ham `aso_full.jsonl` (1091 satir) HICBIR ZAMAN okunmamisti -> `KAYNAK_DOSYA` sabiti + `unvan->legal_name` + `ON CONFLICT DO NOTHING`; (2) `refresh_pipeline.py:85` modulu `src.` onekiyle ice aktarirken mutlak `company_master.*` importlari `ModuleNotFoundError` veriyordu -> kardes modul `normalize.py` ile birebir ayni goreli desen. import yolu 3/4 -> **4/4**. Canli Supabase: 1091 okundu -> 722 yazilabilir -> 2 kosuda **0 eklendi** (idempotens), companies 10123 sabit, bos unvan 0. 69 test yesil, `TestImportKoku` mandali kirilarak dogrulandi. **722/722 ASO unvani DB'de ZATEN var** -> gorev yeni firma eklemedi, `[3/4]` yesil + idempotent deger uretti. ACIK: `data/aso/` uc varyant ikizi + `scripts/ingest_aso_data.py` ile ikiz ingest yolu (D-211, ayri gorev); `scripts/ninerouter_anahtar_guncelle.py:60` soz dizimi hatasi (9Router yasagi nedeniyle dokunulmadi) | 2026-10-03 |
