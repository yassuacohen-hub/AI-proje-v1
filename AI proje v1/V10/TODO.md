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
| P7-4 | Company Career Pages Scraper | web_kazima | plan | 5000+ website_domain -> /kariyer, /jobs, /career keşif |
| P7-5 | İSKUR Scraper | kazi_scraper | plan | Public metadata only; firma adı gizli. İşveren Kayıt Sorgulama authenticated erişimle SGK/VKN üzerinden firma adı üretebilir; bu yöntem aktif olursa firma-level matching için revize edilecek. |
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

- [x] DOC-02 (P1): Decision Log mekanizmasini kur — sahibi: mimari (architect) — done

- [x] DASH-04 (P1): Hybrid Admin Panel - API client + DB fallback — sahibi: mimar (architect) — done

- [x] DASH-05 (P1): Admin Panel Karar Defteri sekmesi — sahibi: mimar (architect) — done

## Oturum Özeti

DASH-04 API client + DB fallback tamamlandı; api_client.py, db_reader.py, app.py entegrasyonu ve test dosyası eklendi.


DOC-02 Decision Log mekanizmasi tamamlandi; scripts/decision_log.py (read_decisions, log_decision, search_decisions), data/orchestrator/decision_log.jsonl (6 girdi, UTF-8), tests/test_decision_log.py (4 test, hepsi gecti).

DASH-05 Admin Panel Karar Defteri sekmesi tamamlandi; web_dashboard/tabs/admin_panel.py (render_decision_tab), web_dashboard/tabs/__init__.py, app.py 4. sekme eklendi. py_compile + smoke test OK.

DASH-06 Admin Panel API Yönetimi ve Kullanıcı Yönetimi tamamlandı; web_dashboard/tabs/admin_extras.py (render_api_management, render_user_management), app.py 5. sekme, tests/test_admin_extras.py (3 test). py_compile + pytest OK.
