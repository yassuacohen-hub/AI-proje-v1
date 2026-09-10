# TODO — Orkestratör Görev Panosu

Bağlantılar: [[00-Home]] · [[project_state]] · [[CHANGELOG]] · [[Orkestrator]] · [[OSINT_Scraper_Motoru]]

> **Kural:** Her görev tek iç ajana aittir. Durum: plan → aktif → review → done veya locked.
> Kaynak: data/orchestrator/task_board.json (otomatik senkron). Geçmiş kayıtlar [[CHANGELOG]]'dadır.

---

## Açık Görevler

| ID | Görev | Sahip | Durum | Not |
|----|-------|-------|-------|-----|
| P0-1 | İstiklal OSB scraper implementasyonu | web_kazima | done | Scraper aktif, 100 test sahendi. |
| P0-2 | Scrape bitince ingest | gelistirici | done | Syntax hatası düzeltildi. Ingest 5485/5485 matched, 0 errors… |
| P0-3 | Kalite skoru 6.53 | kalite | done | Kalite skoru 56.54/100, hedef 50+ BAŞARILI. |
| Y21 | ISKUR kurumsal eslestirme verisi arastirma | arastirmaci | done | Acik API yok, ozel sektor isyeri adlari gizli. |
| APIFY-01 | Apify uygunluk ve entegrasyon mimarisi arastirma | harici_arastirma | aktif | 3 arac kiyaslandi: Apify, Firecrawl, Scrapy. |
| APIFY-02 | Apify REST Adaptoru + Polling Pilotu | web_kazima | done | ApifyJobSource implementasyonu tamamlandi. SourceSpec regist… |
| APIFY-03 | Apify Webhook + Kalici Olay Isleme | web_kazima | plan |  |
| MCP-01 | Kontrollu Apify MCP Erisimi | arastirmaci | plan |  |
| MCP-02 | Huginn MCP Sunucusu + Ters Connector | arastirmaci | plan |  |
| DOC-01 | Kanonik Dokumantasyon: tek V10 kaynagi | koordinator | plan |  |
| OBS-01 | Obsidian vault modernizasyonu | koordinator | done | YAML frontmatter eklendi, encoding düzeltildi, 10_ankara_osb… |

## P7 — Job Intelligence Modülü (İş İlanı Takip Motoru)

| ID | Görev | Sahip | Durum | Not |
|----|-------|-------|-------|-----|
| P7-1 | DB Migration 0007 - Job Intelligence tabloları | gelistirici | plan | job_postings, company_signals, company_intelligence_scores, company_tech_profile, company_aliases |
| P7-2 | Job Intelligence modul yapısı oluşturma | mimar | plan | sources/, pipeline/, storage/, api/ klasörleri |
| P7-3 | Company Matcher (eşleştirme motoru) | gelistirici | plan | Exact + fuzzy + domain + mersis/vkn + alias multi-pass |
| P7-4 | Company Career Pages Scraper | web_kazima | plan | 5000+ website_domain -> /kariyer, /jobs, /career keşif |
| P7-5 | İSKUR Scraper | kazi_scraper | plan | Public metadata only; firma adı gizli. İşveren Kayıt Sorgulama authenticated erişimle SGK/VKN üzerinden firma adı üretebilir; bu yöntem aktif olursa firma-level matching için revize edilecek. |
| P7-6 | Kariyer.net Scraper | web_kazima | blocked | Anti-bot koruması; proxy/headless gerekebilir |
| Y21 | ARASTIRMA: ISKUR kurumsal eşleştirme verisi | arastirmaci | done | Açık API yok, özel sektör işyeri adları gizli; ilan metadata + aggregation intelligence odaklı çalışılacak. Detay: data/orchestrator/y21_result.json |
| P7-7 | Job Postings Ingest Script | gelistirici | plan | JSONL -> job_postings; company_id eşleştirme; deduplication |
| P7-8 | Job Signals Analyzer | arastirmaci | plan | Growth, Risk, Tech, Geo, Org sinyalleri |
| P7-9 | Intelligence Scorer | arastirmaci | plan | growth, expansion, tech_transformation, investment, org_change, risk skorları |
| P7-10 | Intelligence Scores Recalc Script | gelistirici | plan | company_intelligence_scores, company_tech_profile güncelleme |
| P7-11 | Post-scrape workflow entegrasyonu | gelistirici | done | Adım 5, 6, 7 eklendi (post_scrape_workflow.py) |

## Tamamlanan Dönem Özetleri

| Dönem | Kapsam | Detay |
|-------|--------|-------|
| 2026-09-02 | Supabase migration (22 tablo), ETL pipeline, arama motoru, entity resolution | [[CHANGELOG]] |
| 2026-09-03 | OSINT Motoru v1 + NACE + orkestratör (D-1..D-7) | [[CHANGELOG]] |
| 2026-09-08 | Kalite skoru reformu 22.66 → 63.94 | [[CHANGELOG]] |
| 2026-09-09 | P4+P5 metrikleri (→ 76.44), P6 e-posta MX (→ 53.37) | [[CHANGELOG]] |
| 2026-09-09 | P7 Job Intelligence planlaması + altyapı (P0/P1/P2 tabloları done) | [[CHANGELOG]] |

## Not

Her tamamlanan görev için [[CHANGELOG]] güncellenir ve [[project_state]] yenilenir.
