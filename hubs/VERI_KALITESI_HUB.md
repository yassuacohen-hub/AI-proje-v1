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

## Ilgili Nodlar (Ust Hub)
- [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]]
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[Huginn Data Insights/PROJECT_ROADMAP]]

## Kapanan isler
| VERI-HAYALET-TEMIZ-01 | 4591 hayalet kayit silindi: 9412 satir, fazlalik 0, uq_companies_legal_name mevcut. vergi_no 774->761 farki KAYIP DEGIL — 774 kirli tabloda sayilmisti, tekillesmede mukerrer sayim eridi (D-244/4). KUSUR: silme yedeksiz yapilmis; yedek sonradan alindi (D-244) | 2026-09-27 |
| VERI-NACE-SOZLUK-01 | 3319 NACE kodu yuklendi (4 kaynak birlesimi), seviye korundu, eslesme %92.9 | 2026-09-27 |
| VERI-KAYNAK-BAG-01 | source_records.company_id kolonu eklendi, 5252 eslesme (37.5%), FK dogrulandi | 2026-09-27 |
| VERI-NACE-TEMIZ-01 | 7614 NN.NN format duzeltildi (raw_nace'ten turetildi), 675 altı haneli kırpildi, 25 iki haneli NULL'a cekildi, 1 yetim kod duzeltildi | 2026-09-27 |
