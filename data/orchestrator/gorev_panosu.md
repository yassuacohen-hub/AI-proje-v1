# Gorev Panosu — Orkestrator

> Merkezi gorev listesi: herkes herkesin ne yaptigini takip eder.
> Kaynak: `data/orchestrator/task_board.json` — Obsidian okumasi icin disa aktarilir.

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum | Dosyalar |
|-------|--------|-------|---------|-------|----------|
| P7-6 | Kariyer.net Scraper | web_kazima | P1 | blocked | - |
| ORCH-09 | Otomatik tetikleme nobetcisi: Gorev Zamanlayici poll (1dk deneme -> 10dk hedef, kaldirilabilir) | orkestrator | P1 | aktif | src/company_master/orchestrator/nobetci.py, scripts/gorev_nobetci.py, scripts/gorev_nobetci.bat |
| P7-44 | Dashboard UX redesign: Modern navigation | roo | P0 | aktif | app.py, web_dashboard/tabs/__init__.py |
| P7-45 | Canli veri akisi: Server-Sent Events | kilo | P1 | bekliyor | - |
| P7-46 | Kullanici ayarlar paneli | copilot | P1 | bekliyor | - |

## Tamamlananlar

| Görev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| P0-1 | İstiklal OSB scraper implementasyonu | web_kazima | 2026-09-08T10:00:00Z |
| P0-2 | Scrape bitince ingest - VKN - kalite recalc | gelistirici | 2026-09-13T23:38:19 |
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
| TG-01 | Telegram Bot Gonderim ve Komut Aksini Duzelt | kilo | 2026-09-13T19:05:45 |
| P7-19 | P7-19: SSE Gerçek Zamanlı Bildirim Sistemi — Server-Sent Events ile canlı dashboard güncelleme | gelistirici | 2026-09-12T17:25:51 |
| P7-20 | Admin Dashboard — Kullanıcı yönetimi, API key yönetimi, sistem durumu, webhook metrics UI | gelistirici | 2026-09-12T17:25:51 |
| P7-21 | Performans Metrikleri Paneli — Response time, throughput, error rate grafikleri (Chart.js) | gelistirici | 2026-09-12T17:25:51 |
| DOC-02 | Decision Log mekanizmasini kur | mimari | 2026-09-12T21:03:39 |
| DASH-04 | Hybrid Admin Panel - API client + DB fallback | mimar | 2026-09-12T21:12:02 |
| DASH-05 | Admin Panel Karar Defteri sekmesi | mimar | 2026-09-12T21:12:02 |
| DASH-06 | Admin Panel API Yönetimi ve Kullanıcı Yönetimi | kilo | 2026-09-12T22:27:22 |
| P7-4 | Company Career Pages Scraper | kilo | 2026-09-13T08:30:00 |
| P7-5 | İSKUR Scraper | roo | 2026-09-13T08:25:11 |
| P7-22 | Apify Dead-Letter Queue ve Yeniden Deneme Akışı | kilo | 2026-09-13T07:29:52 |
| P7-23 | Vektör Katmanı Üretim Entegrasyonu | kilo | 2026-09-13T08:15:00 |
| P7-24 | ASO ve OSTİM Veri Kalite Raporu | roo | 2026-09-13T21:44:10 |
| DASH-08 | Admin Denetim (Audit) Sekmesi | kilo | 2026-09-13T08:40:00 |
| DASH-07 | Admin Panel JWT Auth & Rol Yönetimi | mimar | 2026-09-13T00:09:05 |
| ORCH-07 | Obsidian vault git entegrasyonu (kurumsal hafiza) | cline | 2026-09-13T02:01:29 |
| ORCH-08 | Gorev tetikleme + onay kuyrugu: orkestrator atar, ajan otomatik fark eder, teslim kontrol onayi olmadan done OLMaz | orkestrator | 2026-09-13T06:51:01 |
| simple_1 | Basit Test Görevi | roo | 2026-09-13T09:37:01 |
| TEST-02 | Test Görevi 2 | roo | 2026-09-13T06:41:29 |
| ORCH-10 | Telegram Orkestrator Entegrasyonu (ORCH-10) | kilo | 2026-09-13T07:24:53 |
| P7-25 | Admin Dashboard KPI Kartlari — musteri sayisi, API cagrilari, sinyal, sistem sagligi | roo | 2026-09-13T07:19:27 |
| P7-26 | Webhook Monitor sekmesi — endpoint, latency, status dagilimi, hata loglari | kilo | 2026-09-13T07:39:40 |
| YENI-1 | Veri Temizleme Scripti | kilo | 2026-09-13T06:15:00 |
| YENI-2 | API Rate Limiting Optimizasyonu | roo | 2026-09-13T09:50:00 |
| YENI-3 | Supabase companies tablosu olusturma | kilo | 2026-09-13T09:30:16 |
| YENI-4 | Dashboard veri akisi duzelt | roo | 2026-09-13T09:55:00 |
| YENI-5 | Apify webhook DLQ monitor | kilo | 2026-09-13T09:32:40 |
| YENI-6 | Telegram komut test suite | roo | 2026-09-13T09:40:00 |
| CO-01 | CoPlot Arastirmasi: CoPlot nedir, ozellikleri, fiyatlandirmasi, rakip analizi | roo | 2026-09-13T17:32:13 |
| CO-02 | CoPlot Entegrasyon Analizi: API, SDK, webhook destegi | roo | 2026-09-13T17:32:13 |
| NOB-01 | Nobetci Alarm Sistemi: Zincir devami + teslim onayi ses cal | kilo | 2026-09-13T12:15:00 |
| COP-01 | VS Code Copilot Test: src/company_master/utils/telegram_bot.py dosyasindaki send_message fonksiyonunun unit testini yaz. | copilot | 2026-09-13T15:34:27 |
| COP-02 | VS Code Copilot Test: web_dashboard/tabs/admin_kpi.py icindeki render_kpi_tab fonksiyonunu refactor et. KPI kartlarini daha moduler yap. | copilot | 2026-09-13T15:34:27 |
| P7-28 | LinkedIn + Indeed + ISKUR is ilanlari. LinkedIn icin Apify actor kullan. | kilo | 2026-09-13T11:00:00 |
| P7-29 | Google Dorking + Wayback Machine: site:kariyer.net cache verisi topla. | roo | 2026-09-13T12:30:00 |
| P7-30 | Selenium + Rotating Proxy: Kariyer.net icin anti-bot asma scraper. | kilo | 2026-09-13T12:45:00 |
| COP-03 | Copilot Test: src/company_master/orchestrator/trigger.py teslim_et() fonksiyonunun edge-case testleri. | copilot | 2026-09-13T15:34:27 |
| COP-04 | Copilot Test: scripts/gorev_kutusu.py icin CLI testi. | copilot | 2026-09-13T15:34:27 |
| COP-05 | Copilot Test: src/company_master/orchestrator/nobetci.py nobet_tut fonksiyonu test. | copilot | 2026-09-13T15:34:27 |
| P7-27 | AI Cost Dashboard: 9router provider bazli gunluk/aylik maliyet, model breakdown, anomali tespiti. 9router_optimizer.py ciktilarindan veri, Plotly charts. | roo | 2026-09-13T18:52:15 |
| P7-31 | Veri Kalitesi Ozeti: company_quality_scores aggregation, 8313 firma kalite skoru dagilimi, eksik alan analizi, iyilestirme onerileri. Kalite riski (QS<30) filtreleme. | roo | 2026-09-13T19:25:46 |
| COP-11 | Copilot: web_dashboard/tabs/admin_performance.py icin render_performance_tab fonksiyonunun unit testi. | copilot | 2026-09-13T17:20:00 |
| P7-33 | Sistem Performansi: Query latency, cache hit ratio, slow query tespiti, OpenTelemetry trace linking. /api/performance aggregation, Prometheus metrikleri. | kilo | 2026-09-13T17:10:00 |
| COP-06 | Copilot: scripts/decision_log.py icin log_decision fonksiyonunun unit testi yaz. | copilot | 2026-09-13T17:04:09 |
| COP-07 | Copilot: src/company_master/utils/telegram_bot.py icin html_escape fonksiyonunun unit testi. | copilot | 2026-09-13T17:04:40 |
| COP-08 | Sistem-Maliyet testi (retarget: admin_sistem.py) | copilot | 2026-09-13T21:54:20 |
| COP-09 | Sistem-Kalite testi (retarget: admin_sistem.py) | copilot | 2026-09-13T21:59:50 |
| COP-10 | Sistem-Analitik testi (retarget: admin_sistem.py) | copilot | 2026-09-13T22:16:20 |
| COP-12 | Copilot: README.md guncelleme - Admin Panel Faz 2 gelismelerini dokumante et. | copilot | 2026-09-13T17:16:11 |
| P7-34 | Veri Kalitesi iyilestirme scripti: QS<30 firmalar icin otomatik duzeltme gorevleri olustur. | kilo | 2026-09-13T17:15:00 |
| P7-35 | API Rate Limiting iyilestirme: user bazli limit esnekligi, burst mode, whitelist destegi. | kilo | 2026-09-13T17:16:00 |
| P7-36 | Cache stratejisi: Redis cache layer, query result caching, TTL yonetimi. | kilo | 2026-09-13T17:17:00 |
| P7-37 | Log aggregation: Loguru + PostgreSQL audit, structured logging, log rotation. | kilo | 2026-09-13T17:18:00 |
| P7-38 | Webhook DLQ dashboard: Apify webhook hata kuyrugu izleme, retry istatistikleri. | kilo | 2026-09-13T17:19:00 |
| COP-13 | Copilot: web_dashboard/tabs/admin_performance.py render_performance_tab fonksiyonunun unit testi. | copilot | 2026-09-13T18:24:11 |
| COP-14 | Copilot: web_dashboard/tabs/admin_dlq.py render_dlq_tab fonksiyonunun unit testi. | copilot | 2026-09-13T18:27:07 |
| COP-15 | Copilot: web_dashboard/tabs/webhook_monitor.py render_webhook_monitor_tab fonksiyonunun unit testi. | copilot | 2026-09-13T18:30:25 |
| COP-16 | Copilot: web_dashboard/css/style.css icin CSS lint ve optimizasyon kontrolu. | copilot | 2026-09-13T18:57:46 |
| COP-17 | Copilot: web_dashboard/js/app.js icin JavaScript fonksiyon testi. | copilot | 2026-09-13T21:14:18 |
| P7-39 | Dashboard veri yenileme optimizasyonu: Streamlit auto-refresh, session state yonetimi, gereksiz yenilemeleri eleme. | kilo | 2026-09-13T17:30:00 |
| P7-40 | Export fonksiyonu: KPI ve veri tablolarindan CSV/Excel indirme. streamlit export butonu + pandas DataFrame export. | kilo | 2026-09-13T17:30:00 |
| P7-41 | Arama ve filtreleme: Tum sekmelerde global arama, filtreleri kaydetme, favori filtreler. | kilo | 2026-09-13T17:30:00 |
| P7-42 | Loading states: Skeleton screens, progress indicators, spinner componentleri. | kilo | 2026-09-13T17:30:00 |
| P7-43 | Hata sayfalari: 404, 500, baglanti hatasi icin kullanici dostu hata mesajleri. | kilo | 2026-09-13T17:30:00 |
| COP-18 | KPI bos-veri placeholder: web_dashboard/tabs/admin_kpi.py - veri yoksa st.spinner + 'Veri yukleniyor...' skeleton goster; yuklenince kartlar gorunsun. Kucuk diff, tek dosya. | copilot | 2026-09-13T18:24:11 |
| COP-19 | Login hata UX: web_dashboard/tabs/admin_auth.py - hatali giriste anlasilir st.error mesaji + hata temizleme; tests/test_admin_auth_login.py unit test ekle. | copilot | 2026-09-13T18:55:15 |
| COP-20 | DLQ sekmesi testi: tests/test_admin_dlq_tab.py - admin_dlq.py render_dlq_tab icin bos jsonl / dolu jsonl / bozuk satir senaryolari. | copilot | 2026-09-13T18:30:25 |
| COP-21 | Audit sekmesi testi: tests/test_admin_audit_tab.py - admin_audit.py render_audit_tab icin lock yok / lock var / bozuk json senaryolari. | copilot | 2026-09-13T18:40:44 |
| COP-22 | Karar defteri testi: tests/test_admin_panel_tab.py - admin_panel.py icin bos log / dolu log / bozuk jsonl senaryolari. | copilot | 2026-09-13T18:48:15 |
| P7-32 | API Analytics: endpoint bazli kullanim istatistikleri (cagri sayisi, response time, hata orani, rate-limit tetiklenmesi), en cok kullanilan endpointler, tier bazli kullanim dagilimi. Admin sekmesi. | roo | 2026-09-13T19:53:47 |
| ORCH-12-K | [ORCH-12] Isbirligi: CLI + test + dokumantasyon + nobetci bayragi (kilo yarisi) | kilo | 2026-09-13T20:11:58 |
| BRIF-01 | [BRIF] roo brifi: 03_mimari kararlari okunup oneri/kritik/ekleme yazilsin | roo | 2026-09-13T21:14:18 |
| BRIF-02 | [BRIF] kilo brifi: 03_mimari kararlari okunup oneri/kritik/ekleme yazilsin | kilo | 2026-09-13T21:16:48 |
| BRIF-03 | [BRIF] copilot brifi: 03_mimari kararlari okunup oneri/kritik/ekleme yazilsin | copilot | 2026-09-13T21:16:18 |
| SENTEZ-01 | [SENTEZ] 3 brifi oku -> 00_sentez.md: kabul / ret+gerekce / bekleyen kararlar | orkestrator | 2026-09-13T21:29:21 |
| DASH-UX-02a | [DASH-UX] DASH-UX-02a: 5 sistem sekmesini tek 'admin_sistem.py' icinde birlest | copilot | 2026-09-13T21:34:19 |
| DASH-UX-02b | [DASH-UX] DASH-UX-02b: 4 sekmeyi tek 'admin_yonetim.py' icinde birlestir: extr | copilot | 2026-09-13T21:46:49 |
| DASH-UX-03 | [DASH-UX] DASH-UX-03: Paket + Cagraz Satis backend: paketler.py (paket CRUD + | kilo | 2026-09-13T21:57:20 |
| AI-CHAT-01 | [DASH-UX] AI-CHAT-01: Abrakadabra: tabs/abrakadabra.py (st.chat_message) + sr | kilo | 2026-09-13T22:00:00 |
| DASH-UX-01 | [DASH-UX] DASH-UX-01: ANA TASARIM: app.py (7 sekmeli yeni yapi, koyu tema CSS | roo | 2026-09-13T21:37:19 |
| DASH-UX-04 | [DASH-UX] DASH-UX-04: Paketler + Pazarlama UI: tabs/paketler.py + pazarlama.p | roo | 2026-09-13T22:58:52 |
| COP-23 | [COP-TASARIM] TASARIM-1: Bosta-veri bilgi kutusu tutarliligi (ro... | copilot | 2026-09-13T22:31:51 |
| COP-24 | [COP-TASARIM] TASARIM-2: Son-guncelleme + yenile kalibi (roo 4.1... | copilot | 2026-09-13T22:43:21 |
| COP-25 | [COP-TASARIM] TASARIM-3: Sidebar yardim satirlari. app.py icinde... | copilot | 2026-09-13T22:48:51 |
| COP-26 | MUSTERILER ekrani: firma listesi+filtre+bildirim blogu (roo uyarisi) | copilot | 2026-09-13T22:57:21 |
