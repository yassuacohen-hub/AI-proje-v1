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
| APIFY-01 | Apify uygunluk ve entegrasyon mimarisi araştirma | **kilo** | **done** | 3 araç kıyaslandı: Apify GO. ADR: 07_referanslar/10_apify_entegrasyon_arastirmasi_20260910.md |
| APIFY-02 | Apify REST Adaptoru + Polling Pilotu | web_kazima | done | ApifyJobSource tamamlandı. SourceSpec'e 'apify' eklendi. |
| APIFY-03 | Apify Webhook + Kalıcı Olay İşleme | **kilo** | **done** | apify_webhook_receiver.py + /api/webhooks/apify + manage_apify_webhooks.py. 22 test. |
| MCP-01 | Kontrollu Apify MCP Erisimi | **kilo** | **done** | PolicyEngine + ApifyAdapter. Whitelist, spend limits, data limits, NACE scope. 33 test. |
| MCP-02 | Huginn MCP Sunucusu + Ters Connector | **kilo** | **done** | HuginnMCPServer. get_source_policy, get_collection_run_status, submit_evidence_batch, report_collection_failure. |
| DOC-01 | Kanonik Dokumantasyon: tek V10 kaynagi | **kilo** | **done** | 07_referanslar/11_apify_mcp_entegrasyon.md: APIFY-01/02/03 + MCP-01/02. README/docs kilitli; dokunulmadı. |
| OBS-01 | Obsidian vault modernizasyonu | koordinator | done | YAML frontmatter eklendi, encoding düzeltildi, 10_ankara_osb… |
| QTK-01 | Quick Task Wrapper + Harici Ajan Görev Senkronizasyonu | mimar | done | dispatch/review senkronizasyonu, handoff_ekle, quick_task wrapper, 36 test pass |

## P7 — Job Intelligence Modülü (İş İlanı Takip Motoru)

| ID | Görev | Sahip | Durum | Not |
|----|-------|-------|-------|-----|
| P7-1 | DB Migration 0007 - Job Intelligence tabloları | gelistirici | **done** | job_postings, company_signals, company_intelligence_scores, company_tech_profile, company_aliases. Doğrulandi. |
| P7-2 | Job Intelligence modul yapısı oluşturma | mimar | **done** | sources/, pipeline/, storage/, api/ klasörleri. Doğrulandi. |
| P7-3 | Company Matcher (eşleştirme motoru) | gelistirici | **done** | Exact + fuzzy + domain + mersis/vkn + alias multi-pass. kilo tarafindan doğrulandi. |
| P7-4 | Company Career Pages Scraper | kilo | **done** | CareerPagesApifySource (Apify actor bazli kariyer sayflari scraper). 10 test gecti. |
| P7-5 | İSKUR Scraper | kazi_scraper | **done** | P7-5 ISKUR Scraper dogrulandi: iskur.py (269 satir) mevcut ve calisir durumda. IskurSource: JSON-LD + HTML parsing, rate limit 2.0s, pagination (max_pages), Turkce tarih/maas parsing, error handling. Y21 arastirmasi geregi public metadata only (ozel sektor firma adi gizli). syntax OK, import OK. |
| P7-6 | Kariyer.net Scraper | web_kazima | blocked | Anti-bot koruması; proxy/headless gerekebilir |
| Y21 | ARASTIRMA: ISKUR kurumsal eşleştirme verisi | arastirmaci | done | Açık API yok, özel sektör işyeri adları gizli; ilan metadata + aggregation intelligence odaklı çalışılacak. Detay: data/orchestrator/y21_result.json |
| P7-7 | Job Postings Ingest Script | gelistirici | **done** | JSONL -> job_postings; company_id eşleştirme; deduplication. kilo tarafindan doğrulandi. |
| P7-8 | Job Signals Analyzer | **kilo** | **done** | Growth, Risk, Tech, Geo, Org sinyalleri. pipeline/analyzer.py + analyze_job_signals.py. |
| P7-9 | Intelligence Scorer | **kilo** | **done** | growth, expansion, tech_transformation, investment, org_change, risk skorları. scorer.py doğrulandi. |
| P7-10 | Intelligence Scores Recalc Script | **kilo** | **done** | recalc_intelligence_scores.py. score_all_companies + tekil company_id. Router async→sync düzeltmesi yapildi. |
| P7-TEST | Job Intelligence test coverage | kilo | **done** | test_job_intelligence_analyzer.py (27 test) + test_job_intelligence_dikey.py (9 test). black, flake8, py_compile temiz. |
| P7-11 | Post-scrape workflow entegrasyonu | gelistirici | done | Adım 5, 6, 7 eklendi (post_scrape_workflow.py) |

## Eksik / Yeni Görevler

| ID | Görev | Sahip | Durum | Not |
|----|-------|-------|-------|-----|
| P7-12 | Apify Webhook Prod Hardening — Rate limiting, signature validation, Prometheus metrikleri, dead-letter queue, retry/backoff, health endpoint | kilo | done | Webhook hardening test suite: 33 passed in 1.42s. |
| P7-13 | MCP -> OSINT Motoru Bridge — ApifyAdapter + HuginnMCPServer SourceRegistry ile entegre, SourceSpec apify enabled=true | kilo | done | Apify SourceSpec enabled=True; ApifyAdapter get_apify_source_spec ve HuginnMCPServer list_sources SourceRegistry entegrasyonu tamamlandi. 38 test gecti. |
| P7-14 | E2E Pipeline Test — Webhook -> ingest -> SignalAnalyzer -> IntelligenceScorer tam akış testi (fixture + CI) | kilo | done | E2E Pipeline Test tamamlandi: tests/test_job_intelligence_e2e.py (6 test, DB bagimsiz - fake engine). Webhook -> ingest -> SignalAnalyzer -> IntelligenceScorer zinciri dogrulandi. |
| P7-15 | Signal Dashboard / Aggregation — company_signals + company_intelligence_scores -> Grafana/HTML dashboard | kilo | done | web_app.py /api/intelligence/dashboard (SQLite uyumlu) + web_dashboard index.html+app.js+style.css + test eklendi. 9 test gecti. |
| P7-19 | SSE Gerçek Zamanlı Bildirim Sistemi — Server-Sent Events ile canlı dashboard güncelleme | gelistirici | done | Panel entegrasyonu tamamlandi (commit da90f3e). **P7-19a** operasyonel webhook bildirimleri Streamlit'te, **P7-19b** müşteri SSE'si FastAPI panosuna taşınacak. |
| P7-20 | Admin Dashboard — Kullanıcı yönetimi, API key yönetimi, sistem durumu, webhook metrics UI | gelistirici | done | Admin gercek veri paneli tamamlandi (commit 2258c83). Streamlit'te kalır. |
| P7-21 | Performans Metrikleri Paneli — Response time, throughput, error rate grafikleri (Chart.js) | gelistirici | done | Performans gercek veri paneli tamamlandi (commit 2258c83). Streamlit'te kalır; `/api/performance` SSOT. |
| REFACTOR-01 | gorev_guncelle() not keyword argümanını temizle | mimar | done | test_gorev_guncelle_not_keyword_argument eklendi; **{"not": ...} gecisi dogrulandi |
| TEST-01 | Review başarısız senaryo testi ekle | mimar | done | test_dispatch_review.py: bilinmeyen task ve çıktısız task senaryoları |
| VALIDATE-01 | quick_task.py uçtan uca validasyonu | external_agent | done | test_quick_task.py: unit + e2e; quick_task exit-code hatası düzeltildi |
| DOCS-04 | Brief.package() ile brief.py package_brief birleştirme | mimar | done | package_brief() = json.dumps(brief.to_dict()); eşdeğerlik testleri geçti |
| DOCS-05 | Dosya Kilitleme Protokolü Dokümanı | mimar | done | docs/DOSYA_KILITLEME_PROTOKOLU.md |
| DOCS-06 | Görev Panosu Kullanım Kılavuzu | mimar | done | docs/GOREV_PANOSU_KULLANIM_KILAVUZU.md |
| DASH-06 | Admin Panel API Yönetimi ve Kullanıcı Yönetimi | kilo | done | API client kullanarak admin panelinde kullanıcı yönetimi ve API kullanım sekmesi (DASH-06) — done |

## P7 Admin Panel Roadmap Görevleri (Faz 1: MVP)

| ID | Görev | Sahip | Durum | Not |
|----|-------|-------|-------|-----|
| P7-25 | Admin Dashboard KPI Kartları — Müşteri sayısı, API çağrıları, sinyal, sistem sağlığı | **roo** | **done** | Admin KPI tab (render_kpi_tab): toplam_firma, aktif_kullanici, api_cagri, sinyal. Trendler 7/30/90 gün. Bitis: 2026-09-13T07:19:27 |
| P7-26 | Webhook Monitor Sekmesi — Apify ingest pipeline health, DLQ, rate limit | **kilo** | **done** | Webhook Monitor tab oluşturuldu (render_webhook_monitor_tab): endpoint health, olay istatistikleri, durum dağılımı, hata türleri, DLQ kayıtları, latency/Prometheus. app.py'ye 7. admin tab entegre. Py_compile + import OK. |
| P7-22 | Apify Dead-Letter Queue ve Yeniden Deneme Akışı | **kilo** | **done** | DLQ + retry/backoff + rate limiting tamamlandı; 15 test geçiyor. |
| P7-23 | Vektör Katmanı Üretim Entegrasyonu | kilo | **done** | vector_search.py (VectorSearch, VectorSearchConfig, VectorSearchResult). similarity search endpoint, index_companies, search_by_ids, health. Supabase pgvector destegi. 10 test. Toplam vektör testleri 55 geçiyor. |
| P7-24 | ASO ve OSTİM Veri Kalite Raporu | mimar | plan | (Panodaki gerçek P7-24 — admin panel değil) |

> ⚠️ **ID Uyumsuzluk Notu (2026-09-13):** Bu tablodaki P7-22/23/24 ID'leri panoda (task_board.json) farklı görevlere atanmış durumda: gerçek P7-22 = "Apify DLQ" (kilo, **done**), P7-23 = "Vektör Katmanı" (kilo, **done**), P7-24 = "ASO/OSTİM Kalite Raporu" (mimar, plan). **P7-25/26/27 panoda boştur** — admin panel görevleri için kullanılabilir. Karşılaştırma analizi: [[06_muninn_prd_vs_huginn_analiz]]

## Tamamlanan Dönem Özetleri

| Dönem | Kapsam | Detay |
|-------|--------|-------|
| 2026-09-02 | Supabase migration (22 tablo), ETL pipeline, arama motoru, entity resolution | [[CHANGELOG]] |
| 2026-09-03 | OSINT Motoru v1 + NACE + orkestratör (D-1..D-7) | [[CHANGELOG]] |
| 2026-09-08 | Kalite skoru reformu 22.66 → 63.94 | [[CHANGELOG]] |
| 2026-09-09 | P4+P5 metrikleri (→ 76.44), P6 e-posta MX (→ 53.37) | [[CHANGELOG]] |
| 2026-09-09 | P7 Job Intelligence planlaması + altyapı (P0/P1/P2 tabloları done) | [[CHANGELOG]] |
| 2026-09-13 | Orkestrasyon Faz 1: ORCH-08/10 tetik+onay+Telegram, Muninn PRD + Roo analizi vault'a, P7-25/26 admin panel başlangıcı | [[CHANGELOG]] |

---

## Tamamlanan Görevler (En Son)

| ID | Görev | Sahip | Tamamlanma Tarihi | Not |
|-------|--------|-------|----------|-----|
| DASH-08 | Admin Denetim (Audit) Sekmesi | kilo | 2026-09-13T08:40:00 | render_audit_tab: Karar Defteri, Dosya Kilidi, Handoff, Görev Durumu, Trigger Logu. app.py 8. admin tab. |
| YENI-1 | Veri Temizleme Scripti | kilo | 2026-09-13T06:15:00 | scripts/veri_temizleme.py |
| YENI-3 | Supabase companies tablosu olusturma | kilo | 2026-09-13T09:30:16 | src/company_master/schema/companies.sql kontrol edildi |
| YENI-5 | Apify webhook DLQ monitor | kilo | 2026-09-13T09:32:40 | pipeline/dlq_monitor.py: ApifyDLQMonitor sinifi |
| P7-4 | Company Career Pages Scraper | kilo | 2026-09-13T08:30:00 | CareerPagesApifySource (Apify actor bazli kariyer sayflari scraper). 10 test gecti. |
| P7-26 | Webhook Monitor Sekmesi | kilo | 2026-09-13T07:39:40 | Webhook Monitor tab: endpoint health, olay stats, DLQ kayıtları, latency |
| P7-22 | Apify Dead-Letter Queue | kilo | 2026-09-13T07:29:52 | DLQ + retry/backoff + rate limiting; 15 test OK |
| P7-25 | Admin Dashboard KPI Kartları | roo | 2026-09-13T07:19:27 | KPI tab: firma/kullanıcı/API/sinyal metrikleri + trendler |
| ORCH-10 | Telegram Orkestrator Entegrasyonu | kilo | 2026-09-13T06:51:01 | Komutlar: set_status, list_tasks, get_logs. scripts/telegram_polling.py |
| ORCH-08 | Görev Tetikleme + Onay Kuyruğu | orkestrator | 2026-09-13T06:51:01 | trigger.py, gorev_at.py, gorev_kutusu.py. 14 yeni test + 53 regresyon OK |
| PANEL-FIX-01 | Panel Başlangıç Hataları Onarımı | roo | 2026-09-15T07:20:26 | Bayat Streamlit süreci (PID 39288) + toml bozukluğu + emoji (✓→✅) + venv CRLF onarımı (3551 dosya). Sonuç: 3261 test passed, panel health 200, nav 174 passed |

## Not

Her tamamlanan görev için [[CHANGELOG]] güncellenir ve [[project_state]] yenilenir.

- [x] DOC-02 (P1): Decision Log mekanizmasini kur — sahibi: mimari (architect) — done

- [x] DASH-04 (P1): Hybrid Admin Panel - API client + DB fallback — sahibi: mimar (architect) — done

- [x] DASH-05 (P1): Admin Panel Karar Defteri sekmesi — sahibi: mimar (architect) — done

- [x] DASH-07 (P1): Admin Panel JWT Auth & Rol Yönetimi — sahibi: mimar (architect) — done

## Oturum Özeti (13 Eyl — Muninn Faz 1 Tamamlandı + Worktree Fix)

**Tamamlanan:**
- ✅ DASH-08 (kilo): Admin Denetim (Audit) Sekmesi — render_audit_tab, 8 admin tab entegre
- ✅ YENI-1 (kilo): Veri Temizleme Scripti — scripts/veri_temizleme.py, OSTIM 5485 + ASO 785 kayit
- ✅ P7-4 (kilo): Company Career Pages Scraper — CareerPagesApifySource (Apify actor bazli), 10 test OK (2026-09-13T08:30:00)
- ✅ ORCH-08 (cline): Görev tetikleme + onay kuyruğu sistemi
- ✅ ORCH-10 (kilo): Telegram orkestratör entegrasyonu (set_status, list_tasks, get_logs)
- ✅ TEST-02 (roo): Kullanıcı başlatma akışı testi
- ✅ TG-01 (kilo): Telegram bot mesaj gönderme sorunları giderildi
- ✅ P7-22 (kilo): Apify DLQ + Retry (2026-09-13T07:29:52)
- ✅ P7-25 (roo): Admin Dashboard KPI Kartları (2026-09-13T07:19:27)
- ✅ P7-26 (kilo): Webhook Monitor Sekmesi (2026-09-13T07:39:40)
- ✅ Roo mimari analizi vault'a taşındı: `V10/03_mimari/06_muninn_prd_vs_huginn_analiz.md`
- ✅ kilo worktree fix: `.kilo/worktrees/.../AGENT_SYNC.md` 2 gün eskiydi, root'tan güncellendi

**Muninn Faz 1 Admin Panel MVP:** ✅ Tamamlandı (P7-22/25/26)

**Sıradaki P1 Öncelikli Görevler:**
- 🔴 P7-6 (web_kazima): Kariyer.net Scraper (blocked — anti-bot)
- 🔴 P7-5 (kazi_scraper): İSKUR Scraper (review — orchestrator onayı bekleniyor)

**Karar Kaydı:** "Muninn faz kapsamı Roo analiziyle doğrulandı" (accepted, 2026-09-13T06:51)

**Telegram Özeti:** message_id: 120, 122, 123

