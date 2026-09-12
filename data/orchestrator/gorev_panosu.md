# Gorev Panosu — Orkestrator

> Merkezi gorev listesi: herkes herkesin ne yaptigini takip eder.
> Kaynak: `data/orchestrator/task_board.json` — Obsidian okumasi icin disa aktarilir.

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum | Dosyalar |
|-------|--------|-------|---------|-------|----------|
| P7-4 | Company Career Pages Scraper | web_kazima | P1 | plan | - |
| P7-5 | İSKUR Scraper | kazi_scraper | P1 | plan | - |
| P7-6 | Kariyer.net Scraper | web_kazima | P1 | blocked | - |
| P7-22 | Apify Dead-Letter Queue ve Yeniden Deneme Akışı | kilo | P1 | plan | web_app.py, app.py, tests/test_apify_dlq.py |
| P7-23 | Vektör Katmanı Üretim Entegrasyonu | kilo | P1 | plan | src/company_master/vector/, requirements-dev.txt |
| P7-24 | ASO ve OSTİM Veri Kalite Raporu | mimar | P2 | plan | data/aso/, data/ostim/, scripts/quality_report.py |
| DASH-08 | Admin Denetim (Audit) Sekmesi | mimar | P2 | plan | web_dashboard/tabs/admin_audit.py |
| DASH-07 | Admin Kimlik Doğrulama ve Yetkilendirme | mimar | P1 | aktif | web_app.py, app.py, web_dashboard/tabs/admin_auth.py |

## Tamamlananlar

| Görev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| P0-1 | İstiklal OSB scraper implementasyonu | web_kazima | 2026-09-08T10:00:00Z |
| P0-2 | Scrape bitince ingest - VKN - kalite recalc | gelistirici | 2026-09-12T14:42:53 |
| P0-3 | Kalite skoru 6.53 - 50+ heazine | kalite | 2026-09-06T22:54:31 |
| Y21 | ISKUR kurumsal eslestirme verisi arastirma | arastirmaci | 2026-09-10 |
| APIFY-01 | Apify uygunluk ve entegrasyon mimarisi arastirma | kilo | 2026-09-11T22:14:20 |
| APIFY-02 | Apify REST Adaptoru + Polling Pilotu | web_kazima | 2026-09-10T20:30:00Z |
| APIFY-03 | Apify Webhook + Kalici Olay Isleme | kilo | 2026-09-11T22:14:20 |
| MCP-01 | Kontrollu Apify MCP Erisimi | kilo | 2026-09-11T22:14:20 |
| MCP-02 | Huginn MCP Sunucusu + Ters Connector | kilo | 2026-09-11T22:14:20 |
| DOC-01 | Kanonik Dokumantasyon: tek V10 kaynagi | kilo | 2026-09-11T22:14:20 |
| OBS-01 | Obsidian vault modernizasyonu | koordinator | 2026-09-10T19:29:00Z |
| OSINT-01 | OSINT Scraper Motoru + Quality Gate entegrasyonu | mimar | 2026-09-11T03:26:51 |
| ORCH-01 | Orkestratör senkron yeniden kurulum: pano tamiri, test izolasyonu, DOCS-05/06 | cline | 2026-09-11T21:35:10 |
| P7-12 | Apify Webhook Prod Hardening — Rate limiting, signature validation, Prometheus metrikleri, dead-letter queue, retry/backoff, health endpoint | kilo | 2026-09-11T13:21:19 |
| P7-13 | MCP -> OSINT Motoru Bridge — ApifyAdapter + HuginnMCPServer SourceRegistry ile entegre, SourceSpec apify enabled=true | kilo | 2026-09-11T13:21:19 |
| P7-15 | Signal Dashboard / Aggregation — company_signals + company_intelligence_scores -> Grafana/HTML dashboard | kilo | 2026-09-11T23:57:48 |
| REFACTOR-01 | gorev_guncelle() not keyword argümanını temizle | mimar | 2026-09-11T21:55:00 |
| TEST-01 | Review başarısız senaryo testi ekle | mimar | 2026-09-11T21:55:00 |
| VALIDATE-01 | quick_task.py uçtan uca validasyonu | external_agent | 2026-09-11T21:55:00 |
| DOCS-04 | Brief.package() ile brief.py package_brief birleştirme | mimar | 2026-09-11T21:55:00 |
| DOCS-05 | Dosya Kilitleme Protokolü Dokümanı | mimar | 2026-09-11T21:55:00 |
| DOCS-06 | Görev Panosu Kullanım Kılavuzu | mimar | 2026-09-11T21:55:00 |
| QT-001 | Test research task | claude_code | 2026-09-11T21:49:16 |
| QTK-01 | Quick Task Wrapper + Harici Ajan Gorev S | mimar | 2026-09-11 |
| DOCS-01 | Orchestrator README yaz | mimar | 2026-09-11 |
| DOCS-02 | 07_harici_ajan_protokolu.md guncelle | mimar | 2026-09-11 |
| DOCS-03 | AGENTS.md guncelle | mimar | 2026-09-11 |
| RO-02 | Dispatch + Review otomatik test | cursor_grok | 2026-09-11 |
| LIVE-01 | Canli Test: Dispatch + Review Akisi | cursor_grok | 2026-09-11 |
| ROO-01 | Roo Code - Kod Incelemesi ve Refactoring | roo_code | 2026-09-11 |
| 9R-01 | 9Router AI Gateway entegrasyonu | roo_code | 2026-09-11 |
| MCP-03 | MCP Server Entry + Transport Testleri | kilo | 2026-09-11T14:17:06 |
| ORCH-02 | Pano-disk senkronu: 5 done guncelleme + MCP-03 eklendi | cline | 2026-09-11T22:19:32 |
| P7-14 | E2E Pipeline Test — Webhook -> ingest -> SignalAnalyzer -> IntelligenceScorer tam akış testi (fixture + CI) | kilo | 2026-09-11T22:47:41 |
| CLEANUP-01 | test_job_intelligence_e2e.py temizlik - import time + FakeRow kaldir | kilo | 2026-09-11T23:04:42 |
| GIT-01 | Temiz depo + hibrit push stratejisi devreye alma | cline | 2026-09-12T01:35:49 |
| 9R-02 | Vektor Katmani + Dublikasyon Pilotu - ChromaDB, vector/ paketi, index_companies.py, matcher doldurma (VKN+fuzzy+vektor) | roo_code | 2026-09-12T00:18:01 |
| 9R-03 | Chat Tabanli Ilan Zenginlestirme - analyzer.py'ye 9Router chat ile sektor/pozisyon/skill cikarimi (fallback: regex) | roo_code | 2026-09-12T01:50:13 |
| 9R-04 | Web Fetch/Search Aktivasyonu - Firecrawl+Tavily provider eklendikten sonra web_fetch/web_search canli test + kariyer sayfasi analiz akisi | roo_code | 2026-09-12T03:29:34 |
| P7-16 | Entegrasyon Test Kapsamını Genişletme - Vektör, Varlık Çözümlemesi ve DLQ/Yeniden Deneme Senaryoları | kilo | 2026-09-12T01:57:31 |
| P7-17 | Performans ve Ölçeklenebilirlik Benchmark’i - Webhook alıcısı ve MCP sunucusunun yük altında davranışını ölçme | kilo | 2026-09-12T02:13:32 |
| P7-18 | Observability: Distributed Tracing Entegrasyonu - OpenTelemetry entegrasyonu ile webhook alıcı, MCP sunucusu ve vektör servisleri arasındaki istekleri izleme | kilo | 2026-09-12T04:04:31 |
| TG-01 | Telegram Bot Gonderim ve Komut Aksini Duzelt | kilo | 2026-09-12T15:18:36 |
| P7-19 | P7-19: SSE Gerçek Zamanlı Bildirim Sistemi — Server-Sent Events ile canlı dashboard güncelleme | gelistirici | 2026-09-12T17:25:51 |
| P7-20 | Admin Dashboard — Kullanıcı yönetimi, API key yönetimi, sistem durumu, webhook metrics UI | gelistirici | 2026-09-12T17:25:51 |
| P7-21 | Performans Metrikleri Paneli — Response time, throughput, error rate grafikleri (Chart.js) | gelistirici | 2026-09-12T17:25:51 |
| DOC-02 | Decision Log mekanizmasini kur | mimari | 2026-09-12T21:03:39 |
| DASH-04 | Hybrid Admin Panel - API client + DB fallback | mimar | 2026-09-12T21:12:02 |
| DASH-05 | Admin Panel Karar Defteri sekmesi | mimar | 2026-09-12T21:12:02 |
| DASH-06 | Admin Panel API Yönetimi ve Kullanıcı Yönetimi | kilo | 2026-09-12T22:27:22 |
