# Gorev Panosu — Orkestrator

> Merkezi gorev listesi: herkes herkesin ne yaptigini takip eder.
> Kaynak: `data/orchestrator/task_board.json` — Obsidian okumasi icin disa aktarilir.

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum | Dosyalar |
|-------|--------|-------|---------|-------|----------|
| ADMIN-UX-PROFILMENU-01 | Sag-alt admin profil popover (ProfileMenu) + monokrom ikon + deep-link | salih | P0 | iptal | - |
| RESEARCH-PONYTALE | Ponytail vs Caveman derinlemesine arastirma | ihsan | P0 | review | - |
| ADMIN-UX-MENUTREE-01 | Sol menu agaci yeniden gruplama; Ayarlar sekmesi menuden kalkar | ihsan | P1 | iptal | web_dashboard/tabs/__init__.py |
| V10-BELGE-01 | 6 curutulen iddiaya K1/K3/K4 duzeltme notu | ihsan | P1 | plan | AI proje v1/V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md |
| WK-02 | OSB Tender Monitor Ã¢â‚¬â€ Real-time Tracking | - | P1 | plan | - |
| AGN-CREWAI-PILOT-01 | crewAI hibrit worker pilotu (metin-üretimi deneyi, scripts/deney/) | ihsan | P2 | aktif | scripts/deney/crewai_arastirma_deneyi.py |
| WK-03 | Proxy Rotation and IP Management | - | P2 | plan | - |
| ADLANDIRMA-GERIYE-01 | D-55 geriye donuk: 55 rapor dosyasindan ajan adini kaldir, rol bazli son eke cevir | ihsan | P3 | plan | - |
| REVIEW-ONAY-KUYRUGU-01 | Onay kuyrugundaki 2 teslimi denetle (ADMIN-LOGIN-FIX-01, ADMIN-MODAL-STIL-01) | yasu | P1 | plan | data/orchestrator/REVIEW-ONAY-KUYRUGU-01_rapor_2026-09-18_denetim.md |
| TEST-AYARLAR-KAPSAM-01 | [TEST] Kullanici Ayarlari sayfasi icin test iskeleti yaz (tests/ altinda) | yasu | P2 | aktif | tests/test_admin_kullanici_ayarlari.py |
| DOC-SIRKET-MASTER-01 | [DOC] Ã…Âirket Master ana belgesi dÃƒÂ¼zelt Ã¢â€ â€™ 01_sirket_master_ana_belgesi.md (3s) | utku | P1 | plan | AI proje v1/V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md |
| ALTYAPI-KILIT-TEMIZLE-01 | [ALTYAPI] Duzelt kilitleri â†’ file_locks.json (1s) | yasu | P2 | aktif | data/orchestrator/file_locks.json |
| ORKESTRA-NAMING-AUDIT-02 | [ORKESTRA] D-55/D-57 adlandırma kuralları denetimi → data/orchestrator/ORKESTRA-NAMING-AUDIT-02_rapor_2026-09-20_orkestrator.md (2s) | ihsan | P1 | plan | data/orchestrator/task_board.json, tests/test_naming_audit.py |
| ORKESTRA-DECISION-LOG-03 | [ORKESTRA] Karar defteri düzenleme ve validasyon → data/orchestrator/ORKESTRA-DECISION-LOG-03_rapor_2026-09-20_orkestrator.md (2s) | ihsan | P1 | plan | data/orchestrator/decision_log.jsonl, data/orchestrator/bulgu_defteri.md, tests/test_decision_log.py |
| ORKESTRA-VAULT-TEKRAR-01 | [ORKESTRA] denetle vault isim tekrarlari â†’ ORKESTRA-VAULT-TEKRAR-01_rapor.md (2s) | ihsan | P2 | plan | - |
| ALTYAPI-KILIT-TEMIZLIK-V10-01 | [ALTYAPI] V10-HIJYEN dosyaları kilit sil → file_locks.json (1s) | cline | P2 | iptal | - |
| ORKESTRA-BRIEF-TALIMAT-01 | [ORKESTRA] 4 brife talimat dosyası yaz → data/orchestrator/*.md (1s) | yasu | P2 | plan | - |
| ALTYAPI-TEST-FAILURE-FIX-02 | [ALTYAPI] Test hatasi duzelt â†’ tests/test_mcp.py (2s) | utku | P1 | review | - |

## Tamamlananlar

| Görev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| ADMIN-UX-LOGOUT-01 | [UI] Yönetici çıkış uygulaması yaz → web_dashboard/tabs/admin_auth.py (1s) | ihsan | 2026-09-19T16:22:23 |
| ADMIN-UX-AYARLAR-SAYFA-01 | Kullanici Ayarlari tek sayfa: profil + sifre degistir/sifirla | utku | 2026-09-19T16:49:34 |
| WK-01 | Career Pages Scraper Ã¢â‚¬â€ Enhanced Data Extraction | salih | 2026-09-19T16:59:51 |
| ADMIN-HATA-01 | Hata Yonetimi sekmesi: sahte istatistik/demo raise kaldir, gercek kaynak + rapor kaydi | utku | 2026-09-18T21:55:21 |
| ADMIN-HATA-02 | Admin sekmelerinde 16 sessiz except:pass -> log/hata_kutusu + AST testi | utku | 2026-09-18T21:55:21 |
| ADMIN-KPI-KART-02 | Kalan st.metric -> kpi_karti (webhook_monitor, tenant_health) + AST testi | utku | 2026-09-19T11:37:27 |
| ADMIN-MUSTERI-02 | Musteri Yonetimi: placeholder alt sekmeler gercek icerik (kullanicilar_onay + paket_kredi) | utku | 2026-09-19T11:37:28 |
| FMT-01 | ruff format/lint standardizasyonu (web_app/app/web_dashboard haric) | utku | 2026-09-19T12:23:56 |
| GUARD-ENC-02 | kodlama_denetim genisletme (CRLF/bosluk/tab/EOF + fix) | utku | 2026-09-19T12:24:41 |
| SEC-BANDIT-01 | Bandit statik guvenlik taramasi + HIGH bulgular | utku | 2026-09-19T12:25:44 |
| V10-HIJYEN-02 | search/fulltext.py olu kod silinmesi (B-15) | ihsan | 2026-09-18T21:07:00 |
| P0-1 | İstiklal OSB scraper implementasyonu | web_kazima | 2026-09-08T10:00:00Z |
| P0-2 | Scrape bitince ingest - VKN - kalite recalc | gelistirici | 2026-09-03T14:18:36 |
| P0-3 | Kalite skoru 6.53 - 50+ heazine | kalite | 2026-09-06T22:54:31 |
| Y21 | ISKUR kurumsal eslestirme verisi arastirma | arastirmaci | 2026-09-10 |
| APIFY-01 | Apify uygunluk ve entegrasyon mimarisi arastirma | utku | 2026-09-11T22:14:20 |
| APIFY-02 | Apify REST Adaptoru + Polling Pilotu | web_kazima | 2026-09-10T20:30:00Z |
| APIFY-03 | Apify Webhook + Kalici Olay Isleme | utku | 2026-09-11T22:14:20 |
| MCP-01 | Kontrollu Apify MCP Erisimi | utku | 2026-09-11T22:14:20 |
| MCP-02 | Huginn MCP Sunucusu + Ters Connector | utku | 2026-09-11T22:14:20 |
| DOC-01 | [DOC] Kanonik Dokumantasyon: tek V10 kaynagi | utku | 2026-09-11T22:14:20 |
| OBS-01 | Obsidian vault modernizasyonu | koordinator | 2026-09-10T19:29:00Z |
| OSINT-01 | OSINT Scraper Motoru + Quality Gate entegrasyonu | mimar | 2026-09-11T03:26:51 |
| ORCH-01 | Orkestratör senkron yeniden kurulum: pano tamiri, test izolasyonu, DOCS-05/06 | yasu | 2026-09-11T21:35:10 |
| P7-12 | Apify Webhook Prod Hardening Ã¢â‚¬â€ Rate limiting, signature validation, Prometheus metrikleri, dead-letter queue, retry/backoff, health endpoint | utku | 2026-09-11T13:21:19 |
| P7-13 | MCP -> OSINT Motoru Bridge Ã¢â‚¬â€ ApifyAdapter + HuginnMCPServer SourceRegistry ile entegre, SourceSpec apify enabled=true | utku | 2026-09-11T13:21:19 |
| P7-15 | Signal Dashboard / Aggregation Ã¢â‚¬â€ company_signals + company_intelligence_scores -> Grafana/HTML dashboard | utku | 2026-09-11T23:57:48 |
| REFACTOR-01 | gorev_guncelle() not keyword argümanını temizle | mimar | 2026-09-11T21:55:00 |
| TEST-01 | [TEST] Review başarısız senaryo testi ekle | mimar | 2026-09-11T21:55:00 |
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
| ROO-01 | Roo Code - Kod Incelemesi ve Refactoring | ihsan | 2026-09-11 |
| 9R-01 | 9Router AI Gateway entegrasyonu | ihsan | 2026-09-11 |
| MCP-03 | MCP Server Entry + Transport Testleri | utku | 2026-09-11T14:17:06 |
| ORCH-02 | Pano-disk senkronu: 5 done guncelleme + MCP-03 eklendi | yasu | 2026-09-11T22:19:32 |
| P7-14 | E2E Pipeline Test Ã¢â‚¬â€ Webhook -> ingest -> SignalAnalyzer -> IntelligenceScorer tam akÃ„Â±Ã…Å¸ testi (fixture + CI) | utku | 2026-09-11T22:47:41 |
| CLEANUP-01 | test_job_intelligence_e2e.py temizlik - import time + FakeRow kaldir | utku | 2026-09-11T23:04:42 |
| GIT-01 | Temiz depo + hibrit push stratejisi devreye alma | yasu | 2026-09-12T01:35:49 |
| 9R-02 | Vektor Katmani + Dublikasyon Pilotu - ChromaDB, vector/ paketi, index_companies.py, matcher doldurma (VKN+fuzzy+vektor) | ihsan | 2026-09-12T00:18:01 |
| 9R-03 | Chat Tabanli Ilan Zenginlestirme - analyzer.py'ye 9Router chat ile sektor/pozisyon/skill cikarimi (fallback: regex) | ihsan | 2026-09-12T01:50:13 |
| 9R-04 | Web Fetch/Search Aktivasyonu - Firecrawl+Tavily provider eklendikten sonra web_fetch/web_search canli test + kariyer sayfasi analiz akisi | ihsan | 2026-09-12T03:29:34 |
| P7-16 | Entegrasyon Test Kapsamını Genişletme - Vektör, Varlık Çözümlemesi ve DLQ/Yeniden Deneme Senaryoları | utku | 2026-09-12T01:57:31 |
| P7-17 | Performans ve Ölçeklenebilirlik Benchmark’i - Webhook alıcısı ve MCP sunucusunun yük altında davranışını ölçme | utku | 2026-09-12T02:13:32 |
| P7-18 | Observability: Distributed Tracing Entegrasyonu - OpenTelemetry entegrasyonu ile webhook alıcı, MCP sunucusu ve vektör servisleri arasındaki istekleri izleme | utku | 2026-09-12T04:04:31 |
| TG-01 | Telegram Bot Gonderim ve Komut Aksini Duzelt | utku | 2026-09-18T04:55:50 |
| P7-19 | P7-19: SSE GerÃƒÂ§ek ZamanlÃ„Â± Bildirim Sistemi Ã¢â‚¬â€ Server-Sent Events ile canlÃ„Â± dashboard gÃƒÂ¼ncelleme | gelistirici | 2026-09-12T17:25:51 |
| P7-20 | Admin Dashboard Ã¢â‚¬â€ KullanÃ„Â±cÃ„Â± yÃƒÂ¶netimi, API key yÃƒÂ¶netimi, sistem durumu, webhook metrics UI | gelistirici | 2026-09-12T17:25:51 |
| P7-21 | Performans Metrikleri Paneli Ã¢â‚¬â€ Response time, throughput, error rate grafikleri (Chart.js) | gelistirici | 2026-09-12T17:25:51 |
| DOC-02 | [DOC] Decision Log mekanizmasini kur | mimari | 2026-09-12T21:03:39 |
| DASH-04 | Hybrid Admin Panel - API client + DB fallback | mimar | 2026-09-12T21:12:02 |
| DASH-05 | Admin Panel Karar Defteri sekmesi | mimar | 2026-09-12T21:12:02 |
| DASH-06 | Admin Panel API Yönetimi ve Kullanıcı Yönetimi | utku | 2026-09-12T22:27:22 |
| P7-4 | Company Career Pages Scraper | utku | 2026-09-13T08:30:00 |
| P7-5 | İSKUR Scraper | ihsan | 2026-09-13T08:25:11 |
| P7-6 | Kariyer.net Scraper (Hizli MVP) | utku | 2026-09-15T18:02:53 |
| P7-22 | Apify Dead-Letter Queue ve Yeniden Deneme Akışı | utku | 2026-09-13T07:29:52 |
| P7-23 | Vektör Katmanı Üretim Entegrasyonu | utku | 2026-09-13T08:15:00 |
| P7-24 | ASO ve OSTİM Veri Kalite Raporu | ihsan | 2026-09-13T21:44:10 |
| DASH-08 | Admin Denetim (Audit) Sekmesi | utku | 2026-09-13T08:40:00 |
| DASH-07 | Admin Panel JWT Auth & Rol Yönetimi | mimar | 2026-09-13T00:09:05 |
| ORCH-07 | Obsidian vault git entegrasyonu (kurumsal hafiza) | yasu | 2026-09-13T02:01:29 |
| ORCH-08 | Gorev tetikleme + onay kuyrugu: orkestrator atar, ajan otomatik fark eder, teslim kontrol onayi olmadan done OLMaz | ihsan | 2026-09-13T06:51:01 |
| ORCH-09 | Otomatik tetikleme nobetcisi: Gorev Zamanlayici poll (1dk deneme -> 10dk hedef, kaldirilabilir) | utku | 2026-09-14T03:36:37 |
| simple_1 | Basit Test Görevi | ihsan | 2026-09-13T09:37:01 |
| TEST-02 | [TEST] Test Görevi 2 | ihsan | 2026-09-13T06:41:29 |
| ORCH-10 | Telegram Orkestrator Entegrasyonu (ORCH-10) | utku | 2026-09-13T07:24:53 |
| P7-25 | Admin Dashboard KPI Kartlari Ã¢â‚¬â€ musteri sayisi, API cagrilari, sinyal, sistem sagligi | ihsan | 2026-09-13T07:19:27 |
| P7-26 | Webhook Monitor sekmesi Ã¢â‚¬â€ endpoint, latency, status dagilimi, hata loglari | utku | 2026-09-13T07:39:40 |
| YENI-1 | Veri Temizleme Scripti | utku | 2026-09-13T06:15:00 |
| YENI-2 | API Rate Limiting Optimizasyonu | ihsan | 2026-09-13T09:50:00 |
| YENI-3 | Supabase companies tablosu olusturma | utku | 2026-09-13T09:30:16 |
| YENI-4 | Dashboard veri akisi duzelt | ihsan | 2026-09-13T09:55:00 |
| YENI-5 | Apify webhook DLQ monitor | utku | 2026-09-13T09:32:40 |
| YENI-6 | Telegram komut test suite | ihsan | 2026-09-13T09:40:00 |
| CO-01 | CoPlot Arastirmasi: CoPlot nedir, ozellikleri, fiyatlandirmasi, rakip analizi | ihsan | 2026-09-13T17:32:13 |
| CO-02 | CoPlot Entegrasyon Analizi: API, SDK, webhook destegi | ihsan | 2026-09-13T17:32:13 |
| NOB-01 | Nobetci Alarm Sistemi: Zincir devami + teslim onayi ses cal | utku | 2026-09-13T12:15:00 |
| COP-01 | VS Code Copilot Test: src/company_master/utils/telegram_bot.py dosyasindaki send_message fonksiyonunun unit testini yaz. | copilot | 2026-09-13T15:34:27 |
| COP-02 | VS Code Copilot Test: web_dashboard/tabs/admin_kpi.py icindeki render_kpi_tab fonksiyonunu refactor et. KPI kartlarini daha moduler yap. | copilot | 2026-09-13T15:34:27 |
| P7-28 | LinkedIn + Indeed + ISKUR is ilanlari. LinkedIn icin Apify actor kullan. | utku | 2026-09-13T11:00:00 |
| P7-29 | Google Dorking + Wayback Machine: site:kariyer.net cache verisi topla. | ihsan | 2026-09-13T12:30:00 |
| P7-30 | Selenium + Rotating Proxy: Kariyer.net icin anti-bot asma scraper. | utku | 2026-09-13T12:45:00 |
| COP-03 | Copilot Test: src/company_master/orchestrator/trigger.py teslim_et() fonksiyonunun edge-case testleri. | copilot | 2026-09-13T15:34:27 |
| COP-04 | Copilot Test: scripts/gorev_kutusu.py icin CLI testi. | copilot | 2026-09-13T15:34:27 |
| COP-05 | Copilot Test: src/company_master/orchestrator/nobetci.py nobet_tut fonksiyonu test. | copilot | 2026-09-13T15:34:27 |
| P7-27 | AI Cost Dashboard: 9router provider bazli gunluk/aylik maliyet, model breakdown, anomali tespiti. 9router_optimizer.py ciktilarindan veri, Plotly charts. | ihsan | 2026-09-13T18:52:15 |
| P7-31 | Veri Kalitesi Ozeti: company_quality_scores aggregation, 8313 firma kalite skoru dagilimi, eksik alan analizi, iyilestirme onerileri. Kalite riski (QS<30) filtreleme. | ihsan | 2026-09-13T19:25:46 |
| COP-11 | Copilot: web_dashboard/tabs/admin_performance.py icin render_performance_tab fonksiyonunun unit testi. | copilot | 2026-09-13T17:20:00 |
| P7-33 | Sistem Performansi: Query latency, cache hit ratio, slow query tespiti, OpenTelemetry trace linking. /api/performance aggregation, Prometheus metrikleri. | utku | 2026-09-13T17:10:00 |
| COP-06 | Copilot: scripts/decision_log.py icin log_decision fonksiyonunun unit testi yaz. | copilot | 2026-09-13T17:04:09 |
| COP-07 | Copilot: src/company_master/utils/telegram_bot.py icin html_escape fonksiyonunun unit testi. | copilot | 2026-09-13T17:04:40 |
| COP-08 | Sistem-Maliyet testi (retarget: admin_sistem.py) | copilot | 2026-09-13T21:54:20 |
| COP-09 | Sistem-Kalite testi (retarget: admin_sistem.py) | copilot | 2026-09-13T21:59:50 |
| COP-10 | Sistem-Analitik testi (retarget: admin_sistem.py) | copilot | 2026-09-13T22:16:20 |
| COP-12 | Copilot: README.md guncelleme - Admin Panel Faz 2 gelismelerini dokumante et. | copilot | 2026-09-13T17:16:11 |
| P7-34 | Veri Kalitesi iyilestirme scripti: QS<30 firmalar icin otomatik duzeltme gorevleri olustur. | utku | 2026-09-13T17:15:00 |
| P7-35 | API Rate Limiting iyilestirme: user bazli limit esnekligi, burst mode, whitelist destegi. | utku | 2026-09-13T17:16:00 |
| P7-36 | Cache stratejisi: Redis cache layer, query result caching, TTL yonetimi. | utku | 2026-09-13T17:17:00 |
| P7-37 | Log aggregation: Loguru + PostgreSQL audit, structured logging, log rotation. | utku | 2026-09-13T17:18:00 |
| P7-38 | Webhook DLQ dashboard: Apify webhook hata kuyrugu izleme, retry istatistikleri. | utku | 2026-09-13T17:19:00 |
| COP-13 | Copilot: web_dashboard/tabs/admin_performance.py render_performance_tab fonksiyonunun unit testi. | copilot | 2026-09-13T18:24:11 |
| COP-14 | Copilot: web_dashboard/tabs/admin_dlq.py render_dlq_tab fonksiyonunun unit testi. | copilot | 2026-09-13T18:27:07 |
| COP-15 | Copilot: web_dashboard/tabs/webhook_monitor.py render_webhook_monitor_tab fonksiyonunun unit testi. | copilot | 2026-09-13T18:30:25 |
| COP-16 | Copilot: web_dashboard/css/style.css icin CSS lint ve optimizasyon kontrolu. | copilot | 2026-09-13T18:57:46 |
| COP-17 | Copilot: web_dashboard/js/app.js icin JavaScript fonksiyon testi. | copilot | 2026-09-13T21:14:18 |
| P7-39 | Dashboard veri yenileme optimizasyonu: Streamlit auto-refresh, session state yonetimi, gereksiz yenilemeleri eleme. | utku | 2026-09-13T17:30:00 |
| P7-40 | Export fonksiyonu: KPI ve veri tablolarindan CSV/Excel indirme. streamlit export butonu + pandas DataFrame export. | utku | 2026-09-13T17:30:00 |
| P7-41 | Arama ve filtreleme: Tum sekmelerde global arama, filtreleri kaydetme, favori filtreler. | utku | 2026-09-13T17:30:00 |
| P7-42 | Loading states: Skeleton screens, progress indicators, spinner componentleri. | utku | 2026-09-13T17:30:00 |
| P7-43 | Hata sayfalari: 404, 500, baglanti hatasi icin kullanici dostu hata mesajleri. | utku | 2026-09-13T17:30:00 |
| P7-44 | Dashboard UX redesign: Modern navigation | ihsan | 2026-09-14T00:06:52 |
| P7-45 | Canli veri akisi: Server-Sent Events | utku | 2026-09-13T22:30:00 |
| P7-46 | Kullanici ayarlar paneli | ihsan | 2026-09-14T04:13:27 |
| COP-18 | KPI bos-veri placeholder: web_dashboard/tabs/admin_kpi.py - veri yoksa st.spinner + 'Veri yukleniyor...' skeleton goster; yuklenince kartlar gorunsun. Kucuk diff, tek dosya. | copilot | 2026-09-13T18:24:11 |
| COP-19 | Login hata UX: web_dashboard/tabs/admin_auth.py - hatali giriste anlasilir st.error mesaji + hata temizleme; tests/test_admin_auth_login.py unit test ekle. | copilot | 2026-09-13T18:55:15 |
| COP-20 | DLQ sekmesi testi: tests/test_admin_dlq_tab.py - admin_dlq.py render_dlq_tab icin bos jsonl / dolu jsonl / bozuk satir senaryolari. | copilot | 2026-09-13T18:30:25 |
| COP-21 | Audit sekmesi testi: tests/test_admin_audit_tab.py - admin_audit.py render_audit_tab icin lock yok / lock var / bozuk json senaryolari. | copilot | 2026-09-13T18:40:44 |
| COP-22 | Karar defteri testi: tests/test_admin_panel_tab.py - admin_panel.py icin bos log / dolu log / bozuk jsonl senaryolari. | copilot | 2026-09-13T18:48:15 |
| P7-32 | API Analytics: endpoint bazli kullanim istatistikleri (cagri sayisi, response time, hata orani, rate-limit tetiklenmesi), en cok kullanilan endpointler, tier bazli kullanim dagilimi. Admin sekmesi. | ihsan | 2026-09-13T19:53:47 |
| ORCH-12-K | [ORCH-12] Isbirligi: CLI + test + dokumantasyon + nobetci bayragi (kilo yarisi) | utku | 2026-09-13T20:11:58 |
| BRIF-01 | [BRIF] roo brifi: 03_mimari kararlari okunup oneri/kritik/ekleme yazilsin | ihsan | 2026-09-13T21:14:18 |
| BRIF-02 | [BRIF] kilo brifi: 03_mimari kararlari okunup oneri/kritik/ekleme yazilsin | utku | 2026-09-13T21:16:48 |
| BRIF-03 | [BRIF] copilot brifi: 03_mimari kararlari okunup oneri/kritik/ekleme yazilsin | copilot | 2026-09-13T21:16:18 |
| SENTEZ-01 | [SENTEZ] 3 brifi oku -> 00_sentez.md: kabul / ret+gerekce / bekleyen kararlar | ihsan | 2026-09-13T21:29:21 |
| DASH-UX-02a | [DASH-UX] DASH-UX-02a: 5 sistem sekmesini tek 'admin_sistem.py' icinde birlest | copilot | 2026-09-13T21:34:19 |
| DASH-UX-02b | [DASH-UX] DASH-UX-02b: 4 sekmeyi tek 'admin_yonetim.py' icinde birlestir: extr | copilot | 2026-09-13T21:46:49 |
| DASH-UX-03 | [DASH-UX] DASH-UX-03: Paket + Cagraz Satis backend: paketler.py (paket CRUD + | utku | 2026-09-13T21:57:20 |
| AI-CHAT-01 | [DASH-UX] AI-CHAT-01: Abrakadabra: tabs/abrakadabra.py (st.chat_message) + sr | utku | 2026-09-13T22:00:00 |
| DASH-UX-01 | [DASH-UX] DASH-UX-01: ANA TASARIM: app.py (7 sekmeli yeni yapi, koyu tema CSS | ihsan | 2026-09-13T21:37:19 |
| DASH-UX-04 | [DASH-UX] DASH-UX-04: Paketler + Pazarlama UI: tabs/paketler.py + pazarlama.p | ihsan | 2026-09-13T22:58:52 |
| COP-23 | [COP-TASARIM] TASARIM-1: Bosta-veri bilgi kutusu tutarliligi (ro... | copilot | 2026-09-13T22:31:51 |
| COP-24 | [COP-TASARIM] TASARIM-2: Son-guncelleme + yenile kalibi (roo 4.1... | copilot | 2026-09-13T22:43:21 |
| COP-25 | [COP-TASARIM] TASARIM-3: Sidebar yardim satirlari. app.py icinde... | copilot | 2026-09-13T22:48:51 |
| COP-26 | MUSTERILER ekrani: firma listesi+filtre+bildirim blogu (roo uyarisi) | copilot | 2026-09-13T22:57:21 |
| WIKI-01 | Admin Panel KullanÃ„Â±m KÃ„Â±lavuzu Ã¢â‚¬â€ Obsidian Wiki | ihsan | - |
| ORCH-13 | Pano sema dogrulama (S-05) + tetik_al pano fallback (S-06) | yasu | 2026-09-14T00:38:53 |
| UX-01 | UI Component Library Ã¢â‚¬â€ Design System | ihsan | 2026-09-14T02:08:24 |
| UX-02 | Responsive Layout System ve Breakpoint Management | ihsan | 2026-09-14T02:33:25 |
| UX-03 | Design Token ve Theme Management System | ihsan | 2026-09-14T03:36:38 |
| BE-01 | Admin API Endpoint Optimization and Caching Layer | utku | 2026-09-14T01:00:00 |
| BE-02 | Database Migration Scripts and Schema Versioning | utku | 2026-09-14T01:00:00 |
| BE-03 | Event-Driven Architecture Ã¢â‚¬â€ Message Queue Integration | yasu | 2026-09-14T01:00:00 |
| WIKI-02 | Wiki Documentation Ã¢â‚¬â€ Architecture and API Reference | yasu | 2026-09-14T01:00:00 |
| ROO-UX-ADMIN-01 | Premium Enterprise Admin Panel UX audit sonrasi design system ve shell | ihsan | 2026-09-14T02:10:25 |
| CL-01 | Integration Test Suite for API Endpoints | yasu | 2026-09-14T06:03:25 |
| CL-02 | Performance Benchmark Scripts | yasu | 2026-09-14T06:29:56 |
| CL-03 | Security Audit Ã¢â‚¬â€ Dependency Vulnerability Scan | yasu | 2026-09-14T06:28:50 |
| DEV-01 | CI/CD Pipeline Ã¢â‚¬â€ GitHub Actions Optimization | gelistirici | - |
| AR-01 | Market Trend Analysis Ã¢â‚¬â€ Q3 2026 | utku | 2026-09-14T03:00:00 |
| AR-02 | Competitor Analysis Ã¢â‚¬â€ Direct and Indirect | utku | 2026-09-14T03:00:00 |
| AR-03 | User Persona and Journey Mapping | utku | 2026-09-14T03:00:00 |
| ORCH-11 | Scheduler Service Ã¢â‚¬â€ Cron-like Task Dispatch | ihsan | 2026-09-15T01:00:00 |
| ORCH-12 | Health Monitor Ã¢â‚¬â€ System Status Dashboard | ihsan | 2026-09-15T01:00:00 |
| FIX-ID-01 | Pano id alanı tutarsızlığı: task_id kanonik, 'id' bekleyen tüketiciler None alıyor | utku | 2026-09-14T03:45:00 |
| PO-BACK-01 | Tenant Health Score v1 (Data Quality + Entity Accuracy + Duplicate Rate) | yasu | 2026-09-15T04:20:41 |
| PO-BACK-02 | Segment Eligibility Skoru + Onay Akışı (Coverage + Profile Accuracy) | yasu | 2026-09-15T08:42:33 |
| PO-BACK-03 | Kampanya Durum-Makinesi Denetimi (Source Reliability) | ihsan | 2026-09-15T05:07:33 |
| PO-BACK-04 | Paket Fiyat Kataloğu Tekilleştirme (Field Completeness) | yasu | 2026-09-15T09:07:57 |
| PO-BACK-05 | Veri Tazelik Etiketi + Manuel Yenileme (Freshness) | utku | 2026-09-15T05:23:03 |
| PO-BACK-06 | Destek Merkezi MVP (Evidence Coverage) | utku | 2026-09-15T13:24:46 |
| PO-BACK-07 | Feature Flags MVP (Data Quality + Source Reliability) | utku | 2026-09-15T09:05:53 |
| PO-BACK-08 | Executive Dashboard v1 (Coverage + Data Quality Score) Ã¢â‚¬â€ REVIZE | yasu | 2026-09-15T11:12:44 |
| PO-BACK-09 | Duplicate Rate Dashboard (Admin) | yasu | 2026-09-15T05:32:10 |
| PO-BACK-10 | Coverage Analytics (Müşteri) | ihsan | 2026-09-15T09:00:46 |
| PO-BACK-11 | Source Reliability Monitor (Admin) | ihsan | 2026-09-15T05:43:04 |
| ADMIN-DOC-01 | Admin panel sitemap düzeltmesi ve uygulama öncelik dokümanı | utku | 2026-09-14T18:38:27 |
| USER-DOC-01 | User Panel sitemap belgesi oluÃ…Å¸tur (16_user_panel_sitemap.md) Ã¢â‚¬â€ TASLAK | utku | 2026-09-14T18:38:27 |
| ADMIN-WF-01 | İş akışı optimizasyonu ve görev sıralaması | utku | 2026-09-15T05:23:02 |
| MRK-03 | Marka konumlandirma belgesini projeye tasi + Obsidian baglami | utku | 2026-09-14T16:40:00 |
| MRK-04 | Marka terminolojisi + yazim sozlesmesi + guvenlik supabi kural dosyalarina | utku | 2026-09-14T16:40:00 |
| FIX-NOB-01 | gorev_nobetci.py durum komutu cp1254 UnicodeDecodeError | utku | 2026-09-14T16:40:00 |
| MRK-02F | card.py sayi bicimini i18n.sayi() ile tek kaynaga indir | yasu | 2026-09-14T21:36:59 |
| MRK-02G | tests/test_i18n.py - 13 bekci testi + 4 ek test | yasu | 2026-09-14T21:37:00 |
| MRK-02H | disa_aktar.py + web_dashboard/js/messages.js ureticisi | utku | 2026-09-14T16:40:00 |
| CHART-01 | Grafik altyapisi: charts modulu + requirements kontrolu | yasu | 2026-09-14T21:59:00.270289+00:00 |
| TEN-01 | Multi-tenant hazirligi: TenantContext + bekci + doc | utku | 2026-09-15T04:20:41 |
| GAM-01 | Rozet/Kesif motoru: 3 rozet + kullanici_ilerleme.json | utku | 2026-09-15T04:20:41 |
| AI-RAG-01 | Odin AI RAG iskeleti: kaynak protokolu + baglam derleyici (ai_chat.py'ye dokunma) | utku | 2026-09-15T04:20:41 |
| TEN-02 | Tenant health Streamlit import ayrıştırması | utku | 2026-09-15T04:58:22 |
| AI-CHAT-01-FIX | [FIX] AI-CHAT-01 teslim dosyalari diskte yok: ai_chat.py + abrakadabra.py yeniden uretim | ihsan | 2026-09-15T04:20:41 |
| PO-BACK-01-UI | Tenant Health Score v1 UI entegrasyonu (tenant_health_dashboard'ı ekrana göm) | yasu | 2026-09-15T04:20:41 |
| TEST-ISO-01 | [TEST] test_api_integration.py iÃƒÂ§in izole fixture DB Ã¢â‚¬â€ 69 deselect edilen testi regresyona geri kat | ihsan | 2026-09-15T05:13:08 |
| HEDEF-NACE-01 | Kapsam karti: gercek NACE hedef tablosu (data/nace_hedefleri.json) | ihsan | 2026-09-15T09:27:02 |
| FIX-LEDGER-01 | error_ledger Windows tmp kilidi (WinError 5) retry | ihsan | 2026-09-15T09:27:02 |
| BUG-DESTEK-UTF8 | KRITIK(P1): tests/test_destek.py UTF-16LE+BOM (4319 NUL bayt) Ã¢â‚¬â€ pytest koleksiyonunu durduruyor | ihsan | 2026-09-15T11:20:30 |
| BUG-CHART01-SYNTAX | SORUN(P2): ui/charts/__init__.py SyntaxError (CHART-01 kalÃ„Â±ntÃ„Â±sÃ„Â±) Ã¢â‚¬â€ ortak grafik modÃƒÂ¼lÃƒÂ¼ import edilemiyor | yasu | 2026-09-15T11:12:44 |
| BUG-MIG0006-UTF8 | KR-3: 0006_normalize_compat.py bozuk kodlama (orphan migration dosyasi) | ihsan | 2026-09-15T11:20:30 |
| BUG-ENCODING-GUARD | KR-4: Kodlama denetim araci (BOM/NUL/0-bayt) + ratchet guard + CI | yasu | 2026-09-15T13:23:35 |
| CI-GATE-01 | CI kapisi: tam tests/ + collection-errors + kodlama denetimi adimi | yasu | 2026-09-15T14:06:34 |
| CHART-INT-01 | ui.charts modulunu admin_executive ekranina entegre et | utku | 2026-09-15T14:41:12 |
| REPO-HIJYEN-01 | Kok dizin cop/gecici dosya envanteri (silme yok, karar Urun Sahibi) | ihsan | 2026-09-15T13:00:10 |
| I18N-SES-02 | Marka sesi JSON (105 tr anahtar) ses.json/ui.json ile birlestir | utku | 2026-09-15T15:38:28 |
| BUG-SCRIPTS-COMPILE-01 | scripts/ hijyen: 3 compile-bozuk script + scripts/scripts mukerrer klasor | yasu | 2026-09-15T14:45:47 |
| REVIEW-PO-BACK-06 | PO-BACK-06 Destek Merkezi capraz inceleme (kilo teslimi) | yasu | 2026-09-15T14:45:49 |
| UI-SIDEBAR-02 | [UI] Sidebar: marka blogu uste, logo, kompakt tooltip | utku | 2026-09-15T23:16:00 |
| UI-TOPBAR-02 | [UI] Topbar: arama sag ust, breadcrumb ayrac, Bu sayfada ayiraci | utku | 2026-09-15T23:16:21 |
| REV-I18N-SES-02 | Capraz inceleme: I18N-SES-02 kilo teslimi (ses.json birlestirme) | yasu | 2026-09-15T15:38:28 |
| AUDIT-ENC-02 | Repo geneli kodlama denetimi (BOM/UTF-16/0-bayt/CRLF) + kodlama_denetim.py kapsam kontrolu | yasu | 2026-09-15T15:38:28 |
| REV-UI-SIDEBAR-02 | Capraz inceleme: UI-SIDEBAR-02 kilo teslimi (app.py sidebar) | yasu | 2026-09-18T03:45:37 |
| MVP-KD-01 | MVP Karar Defteri ekrani: PageHeader + filtre + yeni karar formu | utku | 2026-09-15T16:47:21 |
| MVP-KUL-01 | MVP Kullanici Yonetimi ekrani: PageHeader + onayla + kredi formu | utku | 2026-09-15T18:10:18 |
| REV-MVP-KD-01 | Review: MVP-KD-01 Karar Defteri ekrani | yasu | 2026-09-15T16:30:23 |
| REV-MVP-KUL-01 | Review: MVP-KUL-01 Kullanici Yonetimi ekrani | yasu | 2026-09-15T18:10:18 |
| P7-6b | Kariyer.net scraper saglamlastirma (MVP sonrasi) | utku | 2026-09-15T23:20:10 |
| REV-MVP-ADMIN-01 | MVP-ADMIN 4 ekran capraz denetim (rapor-only) | yasu | 2026-09-15T18:29:40 |
| HIJYEN-01 | Kalinti gecici dosya temizligi | yasu | 2026-09-15T18:29:40 |
| ORCH-05b | ORCH-05 kilit dusurme yalniz done/blocked (gorev_guncelle bug) | ihsan | 2026-09-15T18:29:40 |
| MVP-KUL-02 | Kullanici onayinda tier secici (K-1 bulgusu) | utku | 2026-09-15T23:14:20 |
| ENC-ADMIN-PANEL-01 | admin_panel.py mojibake 2 dize (O-1) | ihsan | 2026-09-15T18:34:59 |
| FIX-YONETIM-01 | Yonetim bolumu to_excel hatasi + sekme rehberi metinleri (sahip bulgusu) | ihsan | 2026-09-15T18:51:04 |
| UI-REFRESH-01 | [UI] Otomatik Yenileme bloğu: dev buton/metric responsive + st.auto_refresh cokme fix | ihsan | 2026-09-15T19:09:59 |
| ADMIN-ENV-01 | Admin sifre sifirlama scripti + .env on-dolum (roo) | ihsan | 2026-09-15T19:25:56 |
| ADMIN-RESET-01 | Admin e-posta dogrulamali sifre degistirme (buyer reset altyapisini admin'e uyarla) | ihsan | 2026-09-15T20:20:57 |
| UI-CHART-01 | [UI] Havali KPI kartlari ve grafikler (Ana Kontrol + Yonetim) | ihsan | 2026-09-16T17:41:44 |
| REV-ADMIN-ENV-01 | Review: admin sifre sifirlama scripti + .env on-dolum + app.py restore | yasu | 2026-09-15T21:21:39 |
| GUARD-ENC-01 | kodlama_denetim.py: BOM + NUL + mojibake + ast.parse guard (pre-commit) | yasu | 2026-09-16T19:08:16 |
| UI-MODAL-01 | [UI] Admin panel acilir modal ekranlar + grafik/chart arastirma ve oneri calismasi (dokuman) | yasu | 2026-09-15T21:16:47 |
| REV-UI-CHART-01 | UI-CHART-01 capraz inceleme (roo teslimi, commit 928ef8b) | yasu | 2026-09-16T18:08:39 |
| DOC-HIBRIT-01 | [DOC] Hibrit gecis plani dosyasini repo icine yaz (docs/plans/UI-CHART-01_hibrit_gecis_plani.md) | utku | 2026-09-16T17:14:40 |
| NAV-FIX-01 | Tek tikta bolum gecisi + mojibake (app.py, admin_panel.py) | utku | 2026-09-16T17:41:39 |
| REV-NAV-FIX-01 | NAV-FIX-01 capraz inceleme (kilo teslimi) | yasu | 2026-09-16T18:08:39 |
| NAV-FIX-02 | Menu aciklamalari menu disinda sagda (topbar) gosterilsin; native tooltip kaldir | utku | 2026-09-16T18:21:51 |
| AUTH-GATE-01 | Giris kapisi modali + POST login + sifre sifirlama | utku | 2026-09-16T22:07:25 |
| NAV-IA-01 | Menu agaci: TabTanimi.ust_sayfa + ESKI_URL + 6 ust oge | utku | 2026-09-16T22:07:25 |
| NAV-IA-02 | Musteri Yonetimi sayfasi (6 alt sekme) + K-1 tier fix | utku | 2026-09-16T22:07:25 |
| TOK-01 | Ajan kural dosyalarinda token sikistirma (12K->6K) | yasu | 2026-09-16T21:58:45 |
| REV-TOK-01 | TOK-01 dokuman sadelestirme incelemesi (cline teslimi) | ihsan | 2026-09-16T21:59:50 |
| BRAND-KIMLIK-01 | Marka kimligi seti kuruldu - inceleme ve onay (brand.md + design-tokens.json + assets/LOGO.md) | ihsan | 2026-09-16T23:16:17 |
| MARKA-REVIZE-01 | Marka kalip dosyalari ORTAK REVIZE (roo + cline) - ileri tarihli planlama | yasu | 2026-09-18T03:45:36 |
| ELESTIRI-01 | ROO_ELESTIRI_NOTLARI.md gozden gecirme + cline gezinti bulgulari | ihsan | 2026-09-16T23:16:17 |
| REV-BATCH-01 | Capraz inceleme: BATCH-01 (AUTH-GATE-01+NAV-IA-01+NAV-IA-02, commit feea800) | yasu | 2026-09-16T22:26:29 |
| NAV-IA-04 | Sol-alt hesap karti popover + kimlik/yonetim kaldir | utku | 2026-09-17T03:07:28 |
| NAV-IA-03 | Proje Yonetimi sayfasi (5 alt sekme, Karar Defteri ustte) | utku | 2026-09-16T22:26:29 |
| DATA-LOG-01 | login_events + search_events tablolari, Giris Etkinligi/Aramalar gercek veri | utku | 2026-09-17T03:07:28 |
| SEC-AUTH-01 | Auth uclari guvenlik duzeltmeleri (REV-BATCH-01 Y-1..Y-4, O-1, O-2, O-4, D-1, D-4) | yasu | 2026-09-18T03:45:37 |
| ROO-GAP-NAV-IA04 | NAV-IA-04/AUTH-GATE-01 capsayÃ„Â± tutma Ã¢â‚¬â€ kontrol ve onay | ihsan | 2026-09-16T23:23:35 |
| MARKA-REVIZE-01B | Marka revizyon kod katmani: test_i18n Huggin regex + config.toml primaryColor #6366f1 + scripts/marka_denetim.py | utku | 2026-09-17T03:07:28 |
| TEST-ISO-02 | [TEST] Test izolasyonu: siraya bagimli testler (randomly + monkeypatch) | utku | 2026-09-17T03:28:59 |
| VEC-TEST-01 | Vektor katmani test kapsami >= %90 | utku | 2026-09-17T12:32:00 |
| API-SPLIT-01 | [API] web_app.py modullere bolme (src/company_master/api) | utku | 2026-09-17T14:46:16 |
| HANDOFF-TEMIZ-01 | P0-2 handoff/pano tarih damgasi temizligi (test sizintisi kalintisi) | ihsan | 2026-09-17T07:01:28 |
| TEST-CI-01 | [TEST] CI test isi: pytest -x --timeout + izolasyon guard + kapsam esigi | ihsan | 2026-09-17T06:56:27 |
| ADMIN-AYAR-01 | Admin ayar sekmesi: giris zorunlu + auto_refresh ayar dosyasi + KVKK yardimci (K-04/S-08) | utku | 2026-09-17T06:44:44 |
| UI-MIMARI-02 | [UI] Ana kontrol/musteri yonetimi temizligi: olu kod, inline import, KVKK tuketimi (M-03/M-05) | utku | 2026-09-17T12:29:55 |
| KPI-HIST-01 | GET /api/kpi/history + ana kontrol gercek sparkline (D-14) | utku | 2026-09-17T13:17:05 |
| ADMIN-KPI-KART-01 | Admin sekmelerinde st.metric -> kpi_karti (8 sekme, ~40 kart) | utku | 2026-09-17T19:29:49 |
| ADMIN-ROO-01 | Admin sekmeleri hata/bos-durum standardi + canli/pazarlama/paketler kpi_karti (roo ceza gorevi) | ihsan | 2026-09-17T15:39:39 |
| ADMIN-NAV-HAZIR-01 | Bayat hazir=False ust sayfalari ac (veri_kalite, musteri_onizleme) + girinti + sessiz pass | ihsan | 2026-09-17T07:59:14 |
| ADMIN-EXEC-01 | Executive Dashboard: st.metric->kpi_karti, sessiz except->hata_kutusu, ilk test dosyasi | ihsan | 2026-09-17T07:17:53 |
| ADMIN-SEARCH-01 | admin_search.py admin sekme kalibina gecis (kpi_karti + hata_kutusu + test) | ihsan | 2026-09-17T07:29:31 |
| ADMIN-REFRESH-FIX-01 | admin_auto_refresh: st.rerun oncesi ayar kaydi + sessiz except (roo) | ihsan | 2026-09-17T07:41:26 |
| ADMIN-NAV-HAZIR-02 | Navigasyon/auth sessiz except temizligi (render_fonksiyonu + admin_auth) | ihsan | 2026-09-17T10:49:50 |
| GIT-HIJYEN-01 | Satir sonu/dosya sonu hijyeni: kodlama_denetim.py --kapsam kod exit 0 olsun | utku | 2026-09-18T03:45:36 |
| ROO-CONFIG-01 | Roo Code IDE ucretsiz model yapilandirmasi ve fallback taslagi | utku | 2026-09-18T03:45:37 |
| ADMIN-ROO-DENETIM-01 | Admin panel gece zinciri teslimlerini incele ve onayla (ADMIN-HATA-02, KPI-KART-02, MUSTERI-02) | ihsan | 2026-09-18T05:31:51 |
| ADMIN-HITAP-01 | D-49 uygulama: sahip -> KAHIN (Urun Sahibi) taramasi (kurallar + docs + admin panel metinleri) | ihsan | 2026-09-18T05:27:42 |
| ADMIN-KOK-TEMIZLIK-01 | Kok dizindeki 3 gecici script sil + .gitignore kontrol + commit | ihsan | 2026-09-18T05:27:42 |
| AGN-STACK-01 | crewAI/LangChain vs Huginn orkestratoru kiyas raporu (KAHIN emri) | ihsan | 2026-09-18T05:41:12 |
| MARKA-REVIZE-01-BULGU | Marka denetim muafiyet mekanizmasi (B-1/B-2/B-6) | ihsan | 2026-09-18T05:55:37 |
| ADMIN-LOGIN-FIX-01 | Admin giris: baglanti hatasi ile 401 ayrimi + API kapali uyarisi | ihsan | 2026-09-19T11:37:55 |
| ADMIN-ADMIN2-DOGRULA-01 | 2. admin hesabi yassuacohen@gmail.com sifre dogrulama | utku | 2026-09-18T21:55:20 |
| ADMIN-MODAL-STIL-01 | Admin modal: blur backdrop + marka kimligini yansit | ihsan | 2026-09-19T11:37:55 |
| ADMIN-SIFRE-RESET-FLOW-01 | Sifre unuttum akisi: email gonder -> link -> sifre sifirla | ihsan | 2026-09-18T21:55:20 |
| V10-HIJYEN-01 | engine.py mukerrer+bozuk WHERE blogu temizligi (B-14) | ihsan | 2026-09-18T15:12:46.586128Z |
| UX-MENU-03 | Menu agaci sadelestirme (E1-E5) + Dashboard Overview aksiyon seridi | ihsan | 2026-09-18T17:30:00 |
| UI-AYARLAR-SAYFA-01 | [UI] Kullanici Ayarlari sayfasini yaz â†’ web_dashboard/tabs/admin_kullanici_ayarlari.py (2s) | ihsan | 2026-09-19T16:24:16 |
| ORKESTRA-BASLIK-GERIYE-01 | [ORKESTRA] Acik gorev basliklarini D-57 kalibina tasi â†’ data/orchestrator/task_board.json (2s) | yasu | 2026-09-19T11:39:13 |
| TEST-MERVE-KAPSAM-01 | [TEST] Ayarlar sayfasi testlerini denetle â†’ data/orchestrator/TEST-MERVE-KAPSAM-01_rapor_2026-09-18_denetim.md (2s) | salih | 2026-09-19T11:38:58 |
| ORKESTRA-SPRINT-01 | [ORKESTRA] düzelt tetik gecikmesini (posta kutusu senkronu) → src/company_master/orchestrator/trigger.py (2s) | ihsan | 2026-09-19T10:43:19 |
| ORKESTRA-SPRINT-02 | [ORKESTRA] düzelt bagimlilik zinciri deadlock'unu → scripts/optimize_plan.py (2s) | ihsan | 2026-09-19T10:44:42 |
| ORKESTRA-SPRINT-03 | [ORKESTRA] ölç onay kuyrugu bekleme suresini → data/orchestrator/onay_kuyrugu_metrik.json (1s) | ihsan | 2026-09-19T10:45:37 |
| TEST-SPRINT-04 | [TEST] yaz P2 gorevler icin zorunlu test kapisini â†’ scripts/kodlama_denetim.py (2s) | utku | 2026-09-19T10:43:19 |
| ALTYAPI-SPRINT-05 | [ALTYAPI] düzelt dosya kilidi cakisma hatasini → src/company_master/orchestrator/task_board.py (2s) | utku | 2026-09-19T10:44:42 |
| ORKESTRA-SPRINT-06 | [ORKESTRA] düzelt inceleme atlanan commit yolunu → .pre-commit-config.yaml (1s) | utku | 2026-09-19T10:45:37 |
| TEST-SPRINT-07 | [TEST] yaz bagimli modul regresyon suitini â†’ tests/test_regresyon_bagimli.py (4s) | salih | 2026-09-19T10:43:19 |
| ALTYAPI-SPRINT-08 | [ALTYAPI] yaz surum oncesi dogrulama kontrol listesini â†’ docs/SURUM_ONCESI_KONTROL.md (1s) | salih | 2026-09-19T10:44:42 |
| DOC-SPRINT-09 | [DOC] belgele test sonuc raporu formatini â†’ docs/TEST_RAPOR_FORMATI.md (1s) | salih | 2026-09-19T10:45:37 |
| ALTYAPI-SPRINT-10 | [ALTYAPI] denetle admin API auth bypass acigini â†’ data/orchestrator/ALTYAPI-SPRINT-10_rapor_denetim.md (2s) | yasu | 2026-09-19T10:43:19 |
| ALTYAPI-SPRINT-11 | [ALTYAPI] denetle katman sinirlarini ihlal eden degisiklikleri â†’ data/orchestrator/ALTYAPI-SPRINT-11_rapor_denetim.md (2s) | yasu | 2026-09-19T10:44:42 |
| DOC-SPRINT-12 | [DOC] belgele eksik API endpoint referansini â†’ docs/API_REFERANS.md (2s) | yasu | 2026-09-19T10:45:38 |
| UI-MUSTERI-SUBHEADER-01 | [UI] musteri_yonetimi subheader duzelt â†’ musteri_yonetimi.py (2s) | utku | 2026-09-19T17:18:59 |
| UI-PROFILMENU-01 | [UI] Profil menu yaz â†’ profil_menu.py (4s) | salih | 2026-09-20T05:55:02 |
| UI-MENUTREE-02 | [UI] Sol menu agaci düzelt → __init__.py (4s) | utku | 2026-09-20T08:10:46 |
| UI-AYARLAR-SAYFA-02 | [UI] Ayarlar sayfası yaz → admin_kullanici_ayarlari.py (4s) | utku | 2026-09-20T07:01:13 |
| UI-PROFILMENU-POPOVER-02 | [UI] native st.popover'a taşı → profil_menu.py (2s) | utku | 2026-09-20T07:37:55 |
| ORKESTRA-STALE-TEMIZLIK-01 | [ORKESTRA] Denetle → YASU stale görevleri (1s) | yasu | 2026-09-20T16:39:03 |
| ALTYAPI-SQLITE-INIT | [ALTYAPI] SQLite fixture companies tablosunu yaz â†’ tests/conftest.py (2s) | utku | 2026-09-20T13:25:49 |
| ALTYAPI-GOREVAT-GUNCELLE-01 | [ALTYAPI] gorev_at.py guncelle komutu yaz â†’ scripts/gorev_at.py (1s) | utku | 2026-09-20T11:18:57 |
| UI-MENU-FORM-01 | [UI] Kullanıcı menü form entegrasyonu → web_dashboard/pages/menu.py (2s) | utku | 2026-09-20T11:42:20 |
| UI-FORM-VALIDATION-02 | [UI] Form doğrulama kütüphanesi yaz → src/company_master/ui/forms/validators.py (2s) | utku | 2026-09-20T11:57:28 |
| ALTYAPI-FORM-SETUP-03 | [ALTYAPI] Form altyapısı hazırlığı (config, builder) → src/company_master/ui/forms/builder.py (2s) | utku | 2026-09-20T12:11:49 |
| DOC-V10-AUDIT-01 | [DOC] V10 belge uyum denetimi (AGENTS.md, decision_log, task_board) â†’ data/orchestrator/DOC-V10-AUDIT-01_rapor_2026-09-20_orkestrator.md (2s) | ihsan | 2026-09-20T16:39:09 |
| ALTYAPI-WEB-MONITOR-01 | [ALTYAPI] Web uygulaması canlı monitoring (health check, metrics) → src/company_master/monitoring/health.py (2s) | utku | 2026-09-20T12:33:52 |
| ALTYAPI-PROXY-CONFIG-02 | [ALTYAPI] Reverse proxy yapılandırması (Nginx) → config/nginx.conf (2s) | utku | 2026-09-20T12:47:26 |
| TEST-PLAN-COVERAGE-03 | [TEST] Test kapsam planı ve otomasyon → docs/TEST_PLAN.md (2s) | utku | 2026-09-20T13:13:37 |
| TEST-KAPSAM-OLCUM-01 | [TEST] Mevcut test kapsamını ölç ve raporla → docs/raporlar/test_kapsam_olcum_2026-09-20.md (2s) | salih | 2026-09-20T17:02:49 |
| ALTYAPI-BENCHMARK-02 | [ALTYAPI] Performans ölçümü (API+Streamlit) → docs/raporlar/benchmark_2026-09-20.md (2s) | salih | 2026-09-20T20:25:35 |
| ALTYAPI-BILGI-TABANI-03 | [ALTYAPI] Runbook ve uyum denetimi belgele â†’ docs/RUNBOOK.md (2s) | salih | 2026-09-20T19:32:28 |
| ORKESTRA-DUPLIK-KAPAYANIM-01 | [ORKESTRA] Çakışan görevleri araştır → data/orchestrator/ORKESTRA-DUPLIK-KAPAYANIM-01_rapor_2026-09-20_denetim.md (30d) | yasu | 2026-09-20T19:37:31 |
| ORKESTRA-BRIEF-KALITE-01 | [ORKESTRA] 12 yeni brifi denetle â†’ data/orchestrator/ORKESTRA-BRIEF-KALITE-01_rapor_2026-09-20_denetim.md (1s) | yasu | 2026-09-20T19:37:31 |
| ORKESTRA-KARAR-DEFTERI-AUDIT-01 | [ORKESTRA] Karar defterini denetle â†’ data/orchestrator/ORKESTRA-KARAR-DEFTERI-AUDIT-01_rapor_2026-09-20_denetim.md (30d) | yasu | 2026-09-20T18:58:23 |
| ALTYAPI-TEST-FAILURE-FIX-01 | [ALTYAPI] düzelt 4 pre-existing test failure → data/orchestrator/ALTYAPI-TEST-FAILURE-FIX-01_rapor_2026-09-20_uretim.md (2s) | utku | 2026-09-20T16:38:45 |
| TEST-D77-02 | [TEST] Done task | utku | 2026-09-20T16:32:21 |
| ORKESTRA-KARAR-DEFTERI-FIX-01 | [ORKESTRA] decision_log.jsonl kayıtlarını düzelt → data/orchestrator/decision_log.jsonl (1s) | ihsan | 2026-09-20T19:50:48 |
| ORKESTRA-BACKLOG-KANIT-01 | [ORKESTRA] Backlog kanıt-satırı kuralı yaz → AGENTS.md D-66 güncelleme (2s) | ihsan | 2026-09-20T19:40:18Z |
| ALTYAPI-DECISION-LOG-ENCODE-01 | [ALTYAPI] Decision log UTF-8 kodlamayı denetle → decision_log.jsonl (1s) | ihsan | 2026-09-20T19:40:18Z |
| TEST-D77-01 | [TEST] Pano işleri orkestrator kuralı denetle → TEST-D77-01_rapor_2026-09-20_orkestrator.md (2s) | ihsan | - |
| ORKESTRA-BASLIK-D57-FIX-01 | [ORKESTRA] 11 görev başlığını düzelt → task_board.json (2s) | ihsan | 2026-09-20T21:05:27 |
| TEST-PANO-IZOLASYON-01 | [TEST] Pano izolasyon duzelt â†’ tests/test_pano_bakim_d77.py (1s) | salih | 2026-09-20T21:58:45 |
| ORKESTRA-DECISION-LOG-FORMAT-01 | [ORKESTRA] Decision log format duzelt â†’ data/orchestrator/decision_log.jsonl (4s) | ihsan | - |
