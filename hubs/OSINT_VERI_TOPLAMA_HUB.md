# OSINT / Veri Toplama Hub

> Konu-bazli hub (PO karari 2026-09-21): Veri kaynagi kesfi, scraping motoru, OSINT
> arastirmalari ve toplama politikalari tek noktada. Yurutme raporlari dahil degildir —
> yalnizca kaynak/mimari/arastirma/politika seviyesi belgeler secildi.

Uretim: Sprint Graf Hub'lastirma FAS-2 (2026-09-21). Bagli dokuman: **18**

Ana baglam: [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]] · [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]] · [[Huginn Data Insights/hubs/REPORTS_ANALYSIS_HUB]] · [[Huginn Data Insights/hubs/OSINT_INDEX]] · [[Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB]] · [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] · [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]] · [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]] · [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]] · [[Huginn Data Insights/PROJECT_ROADMAP]] · [[Huginn Data Insights/hubs/V10_POC_HUB]]

---

## Motor / Sistem Referansi
- [[Huginn Data Insights/docs/OSINT_SCRAPER_MOTORU]] — Ana referans: scraper motoru mimarisi
- `Huginn Data Insights/AI proje v1/V10/11_osint_motoru/OSINT_Scraper_Motoru` — V10 motor tasarimi
- `Huginn Data Insights/AI proje v1/V10/11_osint_motoru/Orkestrator` — OSINT orkestratoru
- [[Huginn Data Insights/docs/v10_OSINT_YETENEK_KATALOGU]] — Yetenek katalogu

## Veri Kaynaklari / Envanter
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/01_veri_kaynagi_envanteri` — Kaynak envanteri
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/04_web_kazima_kaynak_arastirmasi` — Web kazima kaynaklari
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/08_gib_vergino_sorgu_stratejisi` — GIB vergi no sorgu stratejisi
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/vkn_bulma_stratejisi` — VKN bulma stratejisi
- [[Huginn Data Insights/docs/P7-6_kariyernet_arastirma]] — Kariyer.net kaynak arastirmasi

## OSB / Saha Arastirmalari
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/02_ankara_osb_ekosistemi_arastirma_notu` — Ankara OSB ekosistemi
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/02_ankara_osb_erisim_planlari` — OSB erisim planlari
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/03_osb_masa_basi_analizi` — OSB masa basi analizi

## Entegrasyon / Arac Arastirmalari
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/10_apify_entegrasyon_arastirmasi_20260910` — Apify entegrasyonu
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/11_apify_mcp_entegrasyon` — Apify MCP entegrasyonu
- [[Huginn Data Insights/docs/P2-3_zamanli_scrape]] — Zamanli scrape tasarimi

## Politika / Rol / Kalite
- `Huginn Data Insights/AI proje v1/V10/09_kurallar_ve_promptlar/05_acik_veri_ve_kazina_politikasi` — Acik veri ve kazima politikasi
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/09_osint_rol_tanimi` — OSINT rol tanimi
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/06_web_kazima_uzmani` — Web kazima uzmani ajani
- `Huginn Data Insights/AI proje v1/V10/12_kalite_metrikleri/01_kalite_skoru_ek_metrikleri` — Kalite skoru metrikleri

---

## Ticaret Sicili / Kanit Katmani
- `Huginn Data Insights/plans/rapor_yasu_BROWSERUSE-TICARET-SICIL-01.md` — TOBB kanit arastirmasi (EK-1 §16-23 canli dogrulama, EK-2 §24-28 Duzey_3)
- `Huginn Data Insights/skills/services/ticaret_sicili_kanit.py` — IlanKaniti kanit kapisi (MERSIS->VKN tek kapı: `kimlik_no.py`)
- `Huginn Data Insights/scripts/tobb_oturum.py` — Dogrudan TOBB oturumu (e-Devlet yok, multipart login D-276)
- `Huginn Data Insights/scripts/pdf_kanit_analiz.py` — PDF scan mı metin katmanı mı ayırt eder (D-277/D-278)
- `Huginn Data Insights/scripts/gazete_ocr.py` — **PASIF** (D-278): vision-LLM OCR, silinmedi, `--aktif` ile açılır
- `Huginn Data Insights/data/pdf_analiz.json` — Ölçüm kanıtı (font=0, Tj=0, 3 gorsel XObject)

**Kaynak farkı (ölçülmüş):** TOBB *ücretsiz üye PDF'i* taranmış görsel (OCR şart);
*abonelik verisi* (Düzey_2/3) **WEB SERVİS / TSM-XML** makine-okunur (OCR gerekmez).
Düzey_3 = 1.427.688 TL/yıl; NACE + Vergi No + Ortaklar + Temsilciler kapsar.

## Ilgili Nodlar (Ust Hub)
- [[Huginn Data Insights/hubs/OSINT_INDEX]]
- [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]]
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[Huginn Data Insights/PROJECT_ROADMAP]]
