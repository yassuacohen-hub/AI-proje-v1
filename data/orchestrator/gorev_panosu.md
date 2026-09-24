# Gorev Panosu — Orkestrator

> Merkezi gorev listesi: herkes herkesin ne yaptigini takip eder.
> Kaynak: `data/orchestrator/task_board.json` — Obsidian okumasi icin disa aktarilir.

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum | Dosyalar |
|-------|--------|-------|---------|-------|----------|
| ADMIN-UX-PROFILMENU-01 | Sag-alt admin profil popover (ProfileMenu) + monokrom ikon + deep-link | salih | P0 | iptal | - |
| ADMIN-UX-MENUTREE-01 | Sol menu agaci yeniden gruplama; Ayarlar sekmesi menuden kalkar | ihsan | P1 | iptal | web_dashboard/tabs/__init__.py |
| WK-01 | Career Pages Scraper — Enhanced Data Extraction | salih | P1 | archive | - |
| WK-02 | OSB Tender Monitor — Real-time Tracking | - | P1 | archive | - |
| FMT-01 | ruff format/lint standardizasyonu (web_app/app/web_dashboard haric) | utku | P2 | archive | ruff.toml, .pre-commit-config.yaml |
| GUARD-ENC-02 | kodlama_denetim genisletme (CRLF/bosluk/tab/EOF + fix) | utku | P2 | archive | scripts/kodlama_denetim.py, tests/test_kodlama_denetim.py, data/kodlama_allowlist.json |
| WK-03 | Proxy Rotation and IP Management | - | P2 | archive | - |
| P7-5 | İSKUR Scraper | ihsan | P1 | archive | - |
| P7-6 | Kariyer.net Scraper (Hizli MVP) | utku | P1 | archive | src/company_master/scrapers/kariyernet.py, tests/test_kariyernet.py, docs/P7-6_kariyernet_arastirma.md |
| P7-24 | ASO ve OSTİM Veri Kalite Raporu | ihsan | P2 | archive | data/aso/, data/ostim/, scripts/quality_report.py |
| ORCH-08 | Gorev tetikleme + onay kuyrugu: orkestrator atar, ajan otomatik fark eder, teslim kontrol onayi olmadan done OLMaz | ihsan | P1 | archive | src/company_master/orchestrator/trigger.py, scripts/gorev_at.py, scripts/gorev_kutusu.py |
| ORCH-09 | Otomatik tetikleme nobetcisi: Gorev Zamanlayici poll (1dk deneme -> 10dk hedef, kaldirilabilir) | utku | P1 | archive | src/company_master/orchestrator/nobetci.py, scripts/gorev_nobetci.py, scripts/gorev_nobetci.bat |
| simple_1 | Basit Test Görevi | ihsan | P1 | archive | - |
| TEST-02 | [TEST] Test Görevi 2 | ihsan | P1 | archive | - |
| ORCH-10 | Telegram Orkestrator Entegrasyonu (ORCH-10) | utku | P1 | archive | scripts/telegram_polling.py, tests/test_telegram_polling.py, V10/09_kurallar_ve_promptlar/09_telegram_bot_rehberi.md |
| P7-25 | Admin Dashboard KPI Kartlari — musteri sayisi, API cagrilari, sinyal, sistem sagligi | ihsan | P1 | archive | web_dashboard/tabs/admin_kpi.py, app.py |
| YENI-3 | Supabase companies tablosu olusturma | utku | P0 | archive | - |
| YENI-5 | Apify webhook DLQ monitor | utku | P1 | archive | - |
| CO-01 | CoPlot Arastirmasi: CoPlot nedir, ozellikleri, fiyatlandirmasi, rakip analizi | ihsan | P0 | archive | - |
| CO-02 | CoPlot Entegrasyon Analizi: API, SDK, webhook destegi | ihsan | P1 | archive | - |
| COP-01 | VS Code Copilot Test: src/company_master/utils/telegram_bot.py dosyasindaki send_message fonksiyonunun unit testini yaz. | copilot | P1 | archive | tests/test_telegram_bot.py |
| COP-02 | VS Code Copilot Test: web_dashboard/tabs/admin_kpi.py icindeki render_kpi_tab fonksiyonunu refactor et. KPI kartlarini daha moduler yap. | copilot | P2 | archive | tests/test_web_dashboard_tabs.py, tests/test_admin_extras.py |
| COP-03 | Copilot Test: src/company_master/orchestrator/trigger.py teslim_et() fonksiyonunun edge-case testleri. | copilot | P1 | archive | tests/test_gorev_trigger.py |
| COP-04 | Copilot Test: scripts/gorev_kutusu.py icin CLI testi. | copilot | P1 | archive | tests/test_gorev_kutusu_cli.py |
| COP-05 | Copilot Test: src/company_master/orchestrator/nobetci.py nobet_tut fonksiyonu test. | copilot | P1 | archive | tests/test_gorev_nobetci.py |
| P7-27 | AI Cost Dashboard: 9router provider bazli gunluk/aylik maliyet, model breakdown, anomali tespiti. 9router_optimizer.py ciktilarindan veri, Plotly charts. | ihsan | P1 | archive | - |
| P7-31 | Veri Kalitesi Ozeti: company_quality_scores aggregation, 8313 firma kalite skoru dagilimi, eksik alan analizi, iyilestirme onerileri. Kalite riski (QS<30) filtreleme. | ihsan | P1 | archive | - |
| COP-11 | Copilot: web_dashboard/tabs/admin_performance.py icin render_performance_tab fonksiyonunun unit testi. | copilot | P2 | archive | - |
| COP-06 | Copilot: scripts/decision_log.py icin log_decision fonksiyonunun unit testi yaz. | copilot | P2 | archive | - |
| COP-07 | Copilot: src/company_master/utils/telegram_bot.py icin html_escape fonksiyonunun unit testi. | copilot | P2 | archive | - |
| COP-08 | Sistem-Maliyet testi (retarget: admin_sistem.py) | copilot | P2 | archive | tests/test_admin_sistem_cost.py |
| COP-09 | Sistem-Kalite testi (retarget: admin_sistem.py) | copilot | P2 | archive | tests/test_admin_sistem_quality.py |
| COP-10 | Sistem-Analitik testi (retarget: admin_sistem.py) | copilot | P2 | archive | tests/test_admin_sistem_analytics.py |
| COP-12 | Copilot: README.md guncelleme - Admin Panel Faz 2 gelismelerini dokumante et. | copilot | P2 | archive | - |
| COP-13 | Copilot: web_dashboard/tabs/admin_performance.py render_performance_tab fonksiyonunun unit testi. | copilot | P2 | archive | - |
| COP-14 | Copilot: web_dashboard/tabs/admin_dlq.py render_dlq_tab fonksiyonunun unit testi. | copilot | P2 | archive | - |
| COP-15 | Copilot: web_dashboard/tabs/webhook_monitor.py render_webhook_monitor_tab fonksiyonunun unit testi. | copilot | P2 | archive | - |
| COP-16 | Copilot: web_dashboard/css/style.css icin CSS lint ve optimizasyon kontrolu. | copilot | P2 | archive | - |
| COP-17 | Copilot: web_dashboard/js/app.js icin JavaScript fonksiyon testi. | copilot | P2 | archive | - |
| P7-44 | Dashboard UX redesign: Modern navigation | ihsan | P0 | archive | app.py, web_dashboard/tabs/__init__.py |
| P7-46 | Kullanici ayarlar paneli | ihsan | P1 | archive | web_dashboard/tabs/admin_panel.py |
| COP-18 | KPI bos-veri placeholder: web_dashboard/tabs/admin_kpi.py - veri yoksa st.spinner + 'Veri yukleniyor...' skeleton goster; yuklenince kartlar gorunsun. Kucuk diff, tek dosya. | copilot | P2 | archive | web_dashboard/tabs/admin_kpi.py |
| COP-19 | Login hata UX: web_dashboard/tabs/admin_auth.py - hatali giriste anlasilir st.error mesaji + hata temizleme; tests/test_admin_auth_login.py unit test ekle. | copilot | P2 | archive | web_dashboard/tabs/admin_auth.py, tests/test_admin_auth_login.py |
| COP-20 | DLQ sekmesi testi: tests/test_admin_dlq_tab.py - admin_dlq.py render_dlq_tab icin bos jsonl / dolu jsonl / bozuk satir senaryolari. | copilot | P2 | archive | tests/test_admin_dlq_tab.py |
| COP-21 | Audit sekmesi testi: tests/test_admin_audit_tab.py - admin_audit.py render_audit_tab icin lock yok / lock var / bozuk json senaryolari. | copilot | P2 | archive | tests/test_admin_audit_tab.py |
| COP-22 | Karar defteri testi: tests/test_admin_panel_tab.py - admin_panel.py icin bos log / dolu log / bozuk jsonl senaryolari. | copilot | P2 | archive | tests/test_admin_panel_tab.py |
| P7-32 | API Analytics: endpoint bazli kullanim istatistikleri (cagri sayisi, response time, hata orani, rate-limit tetiklenmesi), en cok kullanilan endpointler, tier bazli kullanim dagilimi. Admin sekmesi. | ihsan | P1 | archive | web_dashboard/tabs/admin_api_analytics.py |
| BRIF-01 | [BRIF] roo brifi: 03_mimari kararlari okunup oneri/kritik/ekleme yazilsin | ihsan | P1 | archive | AI proje v1/V10/03_mimari/brifler/brif_roo.md |
| BRIF-02 | [BRIF] kilo brifi: 03_mimari kararlari okunup oneri/kritik/ekleme yazilsin | utku | P1 | archive | AI proje v1/V10/03_mimari/brifler/brif_kilo.md |
| BRIF-03 | [BRIF] copilot brifi: 03_mimari kararlari okunup oneri/kritik/ekleme yazilsin | copilot | P1 | archive | AI proje v1/V10/03_mimari/brifler/brif_copilot.md |
| DASH-UX-02a | [DASH-UX] DASH-UX-02a: 5 sistem sekmesini tek 'admin_sistem.py' icinde birlest | copilot | P1 | archive | web_dashboard/tabs/admin_sistem.py |
| DASH-UX-02b | [DASH-UX] DASH-UX-02b: 4 sekmeyi tek 'admin_yonetim.py' icinde birlestir: extr | copilot | P1 | archive | web_dashboard/tabs/admin_yonetim.py |
| DASH-UX-03 | [DASH-UX] DASH-UX-03: Paket + Cagraz Satis backend: paketler.py (paket CRUD + | utku | P1 | archive | src/company_master/paketler.py, src/company_master/pazarlama.py, data/demo/paketler_demo.jsonl |
| DASH-UX-01 | [DASH-UX] DASH-UX-01: ANA TASARIM: app.py (7 sekmeli yeni yapi, koyu tema CSS | ihsan | P1 | archive | app.py, web_dashboard/css/style.css, web_dashboard/tabs/ana_kontrol.py |
| DASH-UX-04 | [DASH-UX] DASH-UX-04: Paketler + Pazarlama UI: tabs/paketler.py + pazarlama.p | ihsan | P1 | archive | web_dashboard/tabs/paketler.py, web_dashboard/tabs/pazarlama.py |
| COP-23 | [COP-TASARIM] TASARIM-1: Bosta-veri bilgi kutusu tutarliligi (ro... | copilot | P2 | archive | web_dashboard/tabs/admin_sistem.py |
| COP-24 | [COP-TASARIM] TASARIM-2: Son-guncelleme + yenile kalibi (roo 4.1... | copilot | P2 | archive | web_dashboard/tabs/admin_kpi.py, web_dashboard/tabs/admin_quality.py |
| COP-25 | [COP-TASARIM] TASARIM-3: Sidebar yardim satirlari. app.py icinde... | copilot | P2 | archive | app.py |
| ORCH-13 | Pano sema dogrulama (S-05) + tetik_al pano fallback (S-06) | yasu | P2 | archive | src/company_master/orchestrator/task_board.py, src/company_master/orchestrator/trigger.py, tests/test_pano_sema.py |
| UX-01 | UI Component Library — Design System | ihsan | P1 | archive | src/company_master/ui/ |
| UX-02 | Responsive Layout System ve Breakpoint Management | ihsan | P1 | archive | web_dashboard/css/ |
| UX-03 | Design Token ve Theme Management System | ihsan | P2 | archive | web_dashboard/css/ |
| ROO-UX-ADMIN-01 | Premium Enterprise Admin Panel UX audit sonrasi design system ve shell | ihsan | P1 | archive | docs/UX_ADMIN_PANEL_REVIEW_2026-09-14.md, web_dashboard/css/admin_tokens.css |
| CL-01 | Integration Test Suite for API Endpoints | yasu | P1 | archive | tests/ |
| CL-02 | Performance Benchmark Scripts | yasu | P2 | archive | scripts/ |
| CL-03 | Security Audit — Dependency Vulnerability Scan | yasu | P1 | archive | data/orchestrator/ |
| AR-02 | Competitor Analysis — Direct and Indirect | utku | P2 | archive | data/orchestrator/AR-02_rekabet_analizi.md |
| PO-BACK-02 | Segment Eligibility Skoru + Onay Akışı (Coverage + Profile Accuracy) | yasu | P1 | archive | src/company_master/segment.py, tests/test_segment.py |
| PO-BACK-03 | Kampanya Durum-Makinesi Denetimi (Source Reliability) | ihsan | P1 | archive | src/company_master/kampanya_durum.py, tests/test_kampanya_durum.py |
| PO-BACK-04 | Paket Fiyat Kataloğu Tekilleştirme (Field Completeness) | yasu | P1 | archive | src/company_master/paketler.py, scripts/sync_paket_fiyatlari.py, tests/test_paket_fiyat.py |
| PO-BACK-05 | Veri Tazelik Etiketi + Manuel Yenileme (Freshness) | utku | P2 | archive | src/company_master/tazelik.py, web_dashboard/tabs/admin_auto_refresh.py, tests/test_tazelik.py |
| PO-BACK-06 | Destek Merkezi MVP (Evidence Coverage) | utku | P2 | archive | src/company_master/destek.py, web_dashboard/tabs/admin_destek.py, tests/test_destek.py |
| PO-BACK-07 | Feature Flags MVP (Data Quality + Source Reliability) | utku | P2 | archive | src/company_master/feature_flags.py, tests/test_feature_flags.py, data/feature_flags.json |
| PO-BACK-08 | Executive Dashboard v1 (Coverage + Data Quality Score) — REVIZE | yasu | P3 | archive | - |
| PO-BACK-09 | Duplicate Rate Dashboard (Admin) | yasu | P1 | archive | src/company_master/dedup_metrics.py, tests/test_dedup_metrics.py |
| PO-BACK-10 | Coverage Analytics (Müşteri) | ihsan | P1 | archive | src/company_master/coverage_analitik.py, tests/test_coverage_analitik.py |
| PO-BACK-11 | Source Reliability Monitor (Admin) | ihsan | P1 | archive | src/company_master/kaynak_guvenilirlik.py, web_dashboard/tabs/admin_quality.py, tests/test_kaynak_guvenilirlik.py |
| ADMIN-WF-01 | İş akışı optimizasyonu ve görev sıralaması | utku | P1 | archive | data/orchestrator/WORKFLOW_OPTIMIZATION.md |
| MRK-02F | card.py sayi bicimini i18n.sayi() ile tek kaynaga indir | yasu | P1 | archive | src/company_master/ui/components/card.py |
| MRK-02G | tests/test_i18n.py - 13 bekci testi + 4 ek test | yasu | P1 | archive | tests/test_i18n.py |
| TEN-01 | Multi-tenant hazirligi: TenantContext + bekci + doc | utku | P1 | archive | src/company_master/tenant/__init__.py, src/company_master/tenant/model.py, tests/test_tenant.py |
| GAM-01 | Rozet/Kesif motoru: 3 rozet + kullanici_ilerleme.json | utku | P2 | archive | src/company_master/rozet/__init__.py, tests/test_rozet.py, data/kullanici_ilerleme.json |
| AI-RAG-01 | Odin AI RAG iskeleti: kaynak protokolu + baglam derleyici (ai_chat.py'ye dokunma) | utku | P2 | archive | src/company_master/odin_ai/__init__.py, src/company_master/odin_ai/rag.py, tests/test_odin_ai.py |
| TEN-02 | Tenant health Streamlit import ayrıştırması | utku | P1 | archive | src/company_master/tenant/health.py, web_dashboard/tabs/tenant_health_dashboard.py, web_dashboard/tabs/admin_kpi.py |
| AI-CHAT-01-FIX | [FIX] AI-CHAT-01 teslim dosyalari diskte yok: ai_chat.py + abrakadabra.py yeniden uretim | ihsan | P1 | archive | src/company_master/ai_chat.py, web_dashboard/tabs/abrakadabra.py, tests/test_ai_chat.py |
| TEST-ISO-01 | [TEST] test_api_integration.py için izole fixture DB — 69 deselect edilen testi regresyona geri kat | ihsan | P1 | archive | tests/test_api_integration.py, tests/conftest.py |
| HEDEF-NACE-01 | Kapsam karti: gercek NACE hedef tablosu (data/nace_hedefleri.json) | ihsan | P2 | archive | src/company_master/coverage_analitik.py, web_dashboard/tabs/pazarlama.py, tests/test_coverage_analitik.py |
| FIX-LEDGER-01 | error_ledger Windows tmp kilidi (WinError 5) retry | ihsan | P2 | archive | - |
| BUG-DESTEK-UTF8 | KRITIK(P1): tests/test_destek.py UTF-16LE+BOM (4319 NUL bayt) — pytest koleksiyonunu durduruyor | ihsan | P1 | archive | - |
| BUG-CHART01-SYNTAX | SORUN(P2): ui/charts/__init__.py SyntaxError (CHART-01 kalıntısı) — ortak grafik modülü import edilemiyor | yasu | P2 | archive | src/company_master/ui/charts/__init__.py, tests/test_ui_charts.py |
| BUG-MIG0006-UTF8 | KR-3: 0006_normalize_compat.py bozuk kodlama (orphan migration dosyasi) | ihsan | P2 | archive | - |
| BUG-ENCODING-GUARD | KR-4: Kodlama denetim araci (BOM/NUL/0-bayt) + ratchet guard + CI | yasu | P2 | archive | scripts/kodlama_denetim.py, tests/test_kodlama_guard.py, data/kodlama_allowlist.json |
| CI-GATE-01 | CI kapisi: tam tests/ + collection-errors + kodlama denetimi adimi | yasu | P1 | archive | .github/workflows/ci.yml |
| CHART-INT-01 | ui.charts modulunu admin_executive ekranina entegre et | utku | P2 | archive | web_dashboard/tabs/admin_executive.py |
| I18N-SES-02 | Marka sesi JSON (105 tr anahtar) ses.json/ui.json ile birlestir | utku | P2 | archive | src/company_master/i18n/_gelen_marka_sesi_2026-09-15.json, src/company_master/i18n/ses.json |
| BUG-SCRIPTS-COMPILE-01 | scripts/ hijyen: 3 compile-bozuk script + scripts/scripts mukerrer klasor | yasu | P2 | archive | scripts/check_email_dist.py, scripts/test_growth.py, scripts/scripts |
| REVIEW-PO-BACK-06 | PO-BACK-06 Destek Merkezi capraz inceleme (kilo teslimi) | yasu | P1 | archive | data/orchestrator/REVIEW-PO-BACK-06_rapor_20260915_cline.md |
| UI-SIDEBAR-02 | [UI] Sidebar: marka blogu uste, logo, kompakt tooltip | utku | P2 | archive | app.py |
| UI-TOPBAR-02 | [UI] Topbar: arama sag ust, breadcrumb ayrac, Bu sayfada ayiraci | utku | P2 | archive | app.py |
| REV-I18N-SES-02 | Capraz inceleme: I18N-SES-02 kilo teslimi (ses.json birlestirme) | yasu | P1 | archive | data/orchestrator/REV-I18N-SES-02_bulgular_2026-09-15_cline.md |
| AUDIT-ENC-02 | Repo geneli kodlama denetimi (BOM/UTF-16/0-bayt/CRLF) + kodlama_denetim.py kapsam kontrolu | yasu | P2 | archive | data/orchestrator/AUDIT-ENC-02_bulgular_2026-09-15_cline.md |
| MVP-KD-01 | MVP Karar Defteri ekrani: PageHeader + filtre + yeni karar formu | utku | P1 | archive | web_dashboard/tabs/admin_panel.py, tests/test_admin_panel_karar_defteri.py |
| MVP-KUL-01 | MVP Kullanici Yonetimi ekrani: PageHeader + onayla + kredi formu | utku | P1 | archive | web_dashboard/tabs/admin_extras.py, tests/test_admin_extras_kullanici.py |
| REV-MVP-KD-01 | Review: MVP-KD-01 Karar Defteri ekrani | yasu | P1 | archive | - |
| P7-6b | Kariyer.net scraper saglamlastirma (MVP sonrasi) | utku | P2 | archive | src/company_master/scrapers/kariyernet.py, tests/test_kariyernet.py |
| REV-MVP-ADMIN-01 | MVP-ADMIN 4 ekran capraz denetim (rapor-only) | yasu | P1 | archive | data/orchestrator/REV-MVP-ADMIN-01_bulgular_20260915_cline.md |
| HIJYEN-01 | Kalinti gecici dosya temizligi | yasu | P2 | archive | data/_tmp/mvp_pano_duzenle.py |
| MVP-KUL-02 | Kullanici onayinda tier secici (K-1 bulgusu) | utku | P2 | archive | web_dashboard/tabs/admin_extras.py, tests/test_admin_extras_kullanici.py |
| REV-ADMIN-ENV-01 | Review: admin sifre sifirlama scripti + .env on-dolum + app.py restore | yasu | P1 | archive | data/orchestrator/REV-ADMIN-ENV-01_bulgular_20260915_cline.md |
| UI-MODAL-01 | [UI] Admin panel acilir modal ekranlar + grafik/chart arastirma ve oneri calismasi (dokuman) | yasu | P2 | archive | docs/UI_MODAL_CHART_ARASTIRMA_2026-09-15.md |
| ALTYAPI-KILIT-TEMIZLIK-V10-01 | [ALTYAPI] V10-HIJYEN dosyaları kilit sil → file_locks.json (1s) | cline | P2 | iptal | - |
| ORKESTRA-BRIEF-TALIMAT-01 | [ORKESTRA] 4 brife talimat dosyası yaz → data/orchestrator/*.md (1s) | yasu | P2 | archive | - |
| BRIK-00 | ALTYAPI Archive sema + gece zinciri → kurulum ve test (D-62, D-63) | ihsan | P1 | archive | - |
| ORKESTRA-ONAY-BOSALT-01 | [ORKESTRA] Onay kuyrugundaki 9 teslimi denetle → data/orchestrator/ORKESTRA-ONAY-BOSALT-01_rapor_2026-09-23_salih.md (4s) | salih | P0 | iptal | - |
| ALTYAPI-D66-BYPASS-TETIKLEME | [ALTYAPI] D-65 Is Durmaz Bypass Tetikleme -> pano_duzenleme (2s) | ihsan | P1 | plan | scripts/pano_denetim.py, scripts/tetik_senk.py, tests/test_d66_bypass_tetikleme.py |

## Tamamlananlar

| Görev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| ADMIN-UX-LOGOUT-01 | [UI] Yönetici çıkış uygulaması yaz → web_dashboard/tabs/admin_auth.py (1s) | ihsan | 2026-09-19T16:22:23 |
| RESEARCH-PONYTALE | Ponytail vs Caveman derinlemesine arastirma | ihsan | 2026-09-22T05:55:45 |
| ADMIN-UX-AYARLAR-SAYFA-01 | Kullanici Ayarlari tek sayfa: profil + sifre degistir/sifirla | utku | 2026-09-19T16:49:34 |
| V10-BELGE-01 | 6 curutulen iddiaya K1/K3/K4 duzeltme notu | ihsan | - |
| ADMIN-HATA-01 | Hata Yonetimi sekmesi: sahte istatistik/demo raise kaldir, gercek kaynak + rapor kaydi | utku | 2026-09-18T21:55:21 |
| ADMIN-HATA-02 | Admin sekmelerinde 16 sessiz except:pass -> log/hata_kutusu + AST testi | utku | 2026-09-18T21:55:21 |
| ADMIN-KPI-KART-02 | Kalan st.metric -> kpi_karti (webhook_monitor, tenant_health) + AST testi | utku | 2026-09-19T11:37:27 |
| ADMIN-MUSTERI-02 | Musteri Yonetimi: placeholder alt sekmeler gercek icerik (kullanicilar_onay + paket_kredi) | utku | 2026-09-19T11:37:28 |
| AGN-CREWAI-PILOT-01 | crewAI hibrit worker pilotu (metin-üretimi deneyi, scripts/deney/) | ihsan | - |
| SEC-BANDIT-01 | Bandit statik guvenlik taramasi + HIGH bulgular | utku | 2026-09-19T12:25:44 |
| V10-HIJYEN-02 | search/fulltext.py olu kod silinmesi (B-15) | ihsan | 2026-09-18T21:07:00 |
| ADLANDIRMA-GERIYE-01 | D-55 geriye donuk: 55 rapor dosyasindan ajan adini kaldir, rol bazli son eke cevir | ihsan | - |
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
| P7-12 | Apify Webhook Prod Hardening — Rate limiting, signature validation, Prometheus metrikleri, dead-letter queue, retry/backoff, health endpoint | utku | 2026-09-11T13:21:19 |
| P7-13 | MCP -> OSINT Motoru Bridge — ApifyAdapter + HuginnMCPServer SourceRegistry ile entegre, SourceSpec apify enabled=true | utku | 2026-09-11T13:21:19 |
| P7-15 | Signal Dashboard / Aggregation — company_signals + company_intelligence_scores -> Grafana/HTML dashboard | utku | 2026-09-11T23:57:48 |
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
| P7-14 | E2E Pipeline Test — Webhook -> ingest -> SignalAnalyzer -> IntelligenceScorer tam akış testi (fixture + CI) | utku | 2026-09-11T22:47:41 |
| CLEANUP-01 | test_job_intelligence_e2e.py temizlik - import time + FakeRow kaldir | utku | 2026-09-11T23:04:42 |
| GIT-01 | Temiz depo + hibrit push stratejisi devreye alma | yasu | 2026-09-12T01:35:49 |
| 9R-02 | Vektor Katmani + Dublikasyon Pilotu - ChromaDB, vector/ paketi, index_companies.py, matcher doldurma (VKN+fuzzy+vektor) | ihsan | 2026-09-12T00:18:01 |
| 9R-03 | Chat Tabanli Ilan Zenginlestirme - analyzer.py'ye 9Router chat ile sektor/pozisyon/skill cikarimi (fallback: regex) | ihsan | 2026-09-12T01:50:13 |
| 9R-04 | Web Fetch/Search Aktivasyonu - Firecrawl+Tavily provider eklendikten sonra web_fetch/web_search canli test + kariyer sayfasi analiz akisi | ihsan | 2026-09-12T03:29:34 |
| P7-16 | Entegrasyon Test Kapsamını Genişletme - Vektör, Varlık Çözümlemesi ve DLQ/Yeniden Deneme Senaryoları | utku | 2026-09-12T01:57:31 |
| P7-17 | Performans ve Ölçeklenebilirlik Benchmark’i - Webhook alıcısı ve MCP sunucusunun yük altında davranışını ölçme | utku | 2026-09-12T02:13:32 |
| P7-18 | Observability: Distributed Tracing Entegrasyonu - OpenTelemetry entegrasyonu ile webhook alıcı, MCP sunucusu ve vektör servisleri arasındaki istekleri izleme | utku | 2026-09-12T04:04:31 |
| TG-01 | Telegram Bot Gonderim ve Komut Aksini Duzelt | utku | 2026-09-18T04:55:50 |
| P7-19 | P7-19: SSE Gerçek Zamanlı Bildirim Sistemi — Server-Sent Events ile canlı dashboard güncelleme | gelistirici | 2026-09-12T17:25:51 |
| P7-20 | Admin Dashboard — Kullanıcı yönetimi, API key yönetimi, sistem durumu, webhook metrics UI | gelistirici | 2026-09-12T17:25:51 |
| P7-21 | Performans Metrikleri Paneli — Response time, throughput, error rate grafikleri (Chart.js) | gelistirici | 2026-09-12T17:25:51 |
| DOC-02 | [DOC] Decision Log mekanizmasini kur | mimari | 2026-09-12T21:03:39 |
| DASH-04 | Hybrid Admin Panel - API client + DB fallback | mimar | 2026-09-12T21:12:02 |
| DASH-05 | Admin Panel Karar Defteri sekmesi | mimar | 2026-09-12T21:12:02 |
| DASH-06 | Admin Panel API Yönetimi ve Kullanıcı Yönetimi | utku | 2026-09-12T22:27:22 |
| P7-4 | Company Career Pages Scraper | utku | 2026-09-13T08:30:00 |
| P7-22 | Apify Dead-Letter Queue ve Yeniden Deneme Akışı | utku | 2026-09-13T07:29:52 |
| P7-23 | Vektör Katmanı Üretim Entegrasyonu | utku | 2026-09-13T08:15:00 |
| DASH-08 | Admin Denetim (Audit) Sekmesi | utku | 2026-09-13T08:40:00 |
| DASH-07 | Admin Panel JWT Auth & Rol Yönetimi | mimar | 2026-09-13T00:09:05 |
| ORCH-07 | Obsidian vault git entegrasyonu (kurumsal hafiza) | yasu | 2026-09-13T02:01:29 |
| P7-26 | Webhook Monitor sekmesi — endpoint, latency, status dagilimi, hata loglari | utku | 2026-09-13T07:39:40 |
| YENI-1 | Veri Temizleme Scripti | utku | 2026-09-13T06:15:00 |
| YENI-2 | API Rate Limiting Optimizasyonu | ihsan | 2026-09-13T09:50:00 |
| YENI-4 | Dashboard veri akisi duzelt | ihsan | 2026-09-13T09:55:00 |
| YENI-6 | Telegram komut test suite | ihsan | 2026-09-13T09:40:00 |
| NOB-01 | Nobetci Alarm Sistemi: Zincir devami + teslim onayi ses cal | utku | 2026-09-13T12:15:00 |
| P7-28 | LinkedIn + Indeed + ISKUR is ilanlari. LinkedIn icin Apify actor kullan. | utku | 2026-09-13T11:00:00 |
| P7-29 | Google Dorking + Wayback Machine: site:kariyer.net cache verisi topla. | ihsan | 2026-09-13T12:30:00 |
| P7-30 | Selenium + Rotating Proxy: Kariyer.net icin anti-bot asma scraper. | utku | 2026-09-13T12:45:00 |
| P7-33 | Sistem Performansi: Query latency, cache hit ratio, slow query tespiti, OpenTelemetry trace linking. /api/performance aggregation, Prometheus metrikleri. | utku | 2026-09-13T17:10:00 |
| P7-34 | Veri Kalitesi iyilestirme scripti: QS<30 firmalar icin otomatik duzeltme gorevleri olustur. | utku | 2026-09-13T17:15:00 |
| P7-35 | API Rate Limiting iyilestirme: user bazli limit esnekligi, burst mode, whitelist destegi. | utku | 2026-09-13T17:16:00 |
| P7-36 | Cache stratejisi: Redis cache layer, query result caching, TTL yonetimi. | utku | 2026-09-13T17:17:00 |
| P7-37 | Log aggregation: Loguru + PostgreSQL audit, structured logging, log rotation. | utku | 2026-09-13T17:18:00 |
| P7-38 | Webhook DLQ dashboard: Apify webhook hata kuyrugu izleme, retry istatistikleri. | utku | 2026-09-13T17:19:00 |
| P7-39 | Dashboard veri yenileme optimizasyonu: Streamlit auto-refresh, session state yonetimi, gereksiz yenilemeleri eleme. | utku | 2026-09-13T17:30:00 |
| P7-40 | Export fonksiyonu: KPI ve veri tablolarindan CSV/Excel indirme. streamlit export butonu + pandas DataFrame export. | utku | 2026-09-13T17:30:00 |
| P7-41 | Arama ve filtreleme: Tum sekmelerde global arama, filtreleri kaydetme, favori filtreler. | utku | 2026-09-13T17:30:00 |
| P7-42 | Loading states: Skeleton screens, progress indicators, spinner componentleri. | utku | 2026-09-13T17:30:00 |
| P7-43 | Hata sayfalari: 404, 500, baglanti hatasi icin kullanici dostu hata mesajleri. | utku | 2026-09-13T17:30:00 |
| P7-45 | Canli veri akisi: Server-Sent Events | utku | 2026-09-13T22:30:00 |
| ORCH-12-K | [ORCH-12] Isbirligi: CLI + test + dokumantasyon + nobetci bayragi (kilo yarisi) | utku | 2026-09-13T20:11:58 |
| SENTEZ-01 | [SENTEZ] 3 brifi oku -> 00_sentez.md: kabul / ret+gerekce / bekleyen kararlar | ihsan | 2026-09-13T21:29:21 |
| AI-CHAT-01 | [DASH-UX] AI-CHAT-01: Abrakadabra: tabs/abrakadabra.py (st.chat_message) + sr | utku | 2026-09-13T22:00:00 |
| COP-26 | MUSTERILER ekrani: firma listesi+filtre+bildirim blogu (roo uyarisi) | ihsan | 2026-09-24T01:33:09 |
| WIKI-01 | Admin Panel Kullanım Kılavuzu — Obsidian Wiki | ihsan | - |
| BE-01 | Admin API Endpoint Optimization and Caching Layer | utku | 2026-09-14T01:00:00 |
| BE-02 | Database Migration Scripts and Schema Versioning | utku | 2026-09-14T01:00:00 |
| BE-03 | Event-Driven Architecture — Message Queue Integration | yasu | 2026-09-14T01:00:00 |
| WIKI-02 | Wiki Documentation — Architecture and API Reference | yasu | 2026-09-14T01:00:00 |
| DEV-01 | CI/CD Pipeline — GitHub Actions Optimization | gelistirici | - |
| AR-01 | Market Trend Analysis — Q3 2026 | utku | 2026-09-14T03:00:00 |
| AR-03 | User Persona and Journey Mapping | utku | 2026-09-14T03:00:00 |
| ORCH-11 | Scheduler Service — Cron-like Task Dispatch | ihsan | 2026-09-15T01:00:00 |
| ORCH-12 | Health Monitor — System Status Dashboard | ihsan | 2026-09-15T01:00:00 |
| FIX-ID-01 | Pano id alanı tutarsızlığı: task_id kanonik, 'id' bekleyen tüketiciler None alıyor | utku | 2026-09-14T03:45:00 |
| PO-BACK-01 | Tenant Health Score v1 (Data Quality + Entity Accuracy + Duplicate Rate) | yasu | 2026-09-15T04:20:41 |
| ADMIN-DOC-01 | Admin panel sitemap düzeltmesi ve uygulama öncelik dokümanı | utku | 2026-09-14T18:38:27 |
| USER-DOC-01 | User Panel sitemap belgesi oluştur (16_user_panel_sitemap.md) — TASLAK | utku | 2026-09-14T18:38:27 |
| MRK-03 | Marka konumlandirma belgesini projeye tasi + Obsidian baglami | utku | 2026-09-14T16:40:00 |
| MRK-04 | Marka terminolojisi + yazim sozlesmesi + guvenlik supabi kural dosyalarina | utku | 2026-09-14T16:40:00 |
| FIX-NOB-01 | gorev_nobetci.py durum komutu cp1254 UnicodeDecodeError | utku | 2026-09-14T16:40:00 |
| MRK-02H | disa_aktar.py + web_dashboard/js/messages.js ureticisi | utku | 2026-09-14T16:40:00 |
| CHART-01 | Grafik altyapisi: charts modulu + requirements kontrolu | yasu | 2026-09-14T21:59:00.270289+00:00 |
| PO-BACK-01-UI | Tenant Health Score v1 UI entegrasyonu (tenant_health_dashboard'ı ekrana göm) | yasu | 2026-09-15T04:20:41 |
| REPO-HIJYEN-01 | Kok dizin cop/gecici dosya envanteri (silme yok, karar Urun Sahibi) | ihsan | 2026-09-15T13:00:10 |
| REV-UI-SIDEBAR-02 | Capraz inceleme: UI-SIDEBAR-02 kilo teslimi (app.py sidebar) | yasu | 2026-09-18T03:45:37 |
| REV-MVP-KUL-01 | Review: MVP-KUL-01 Kullanici Yonetimi ekrani | yasu | 2026-09-15T18:10:18 |
| ORCH-05b | ORCH-05 kilit dusurme yalniz done/blocked (gorev_guncelle bug) | ihsan | 2026-09-15T18:29:40 |
| ENC-ADMIN-PANEL-01 | admin_panel.py mojibake 2 dize (O-1) | ihsan | 2026-09-15T18:34:59 |
| FIX-YONETIM-01 | Yonetim bolumu to_excel hatasi + sekme rehberi metinleri (sahip bulgusu) | ihsan | 2026-09-15T18:51:04 |
| UI-REFRESH-01 | [UI] Otomatik Yenileme bloğu: dev buton/metric responsive + st.auto_refresh cokme fix | ihsan | 2026-09-15T19:09:59 |
| ADMIN-ENV-01 | Admin sifre sifirlama scripti + .env on-dolum (roo) | ihsan | 2026-09-15T19:25:56 |
| ADMIN-RESET-01 | Admin e-posta dogrulamali sifre degistirme (buyer reset altyapisini admin'e uyarla) | ihsan | 2026-09-15T20:20:57 |
| UI-CHART-01 | [UI] Havali KPI kartlari ve grafikler (Ana Kontrol + Yonetim) | ihsan | 2026-09-16T17:41:44 |
| GUARD-ENC-01 | kodlama_denetim.py: BOM + NUL + mojibake + ast.parse guard (pre-commit) | yasu | 2026-09-16T19:08:16 |
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
| ROO-GAP-NAV-IA04 | NAV-IA-04/AUTH-GATE-01 capsayı tutma — kontrol ve onay | ihsan | 2026-09-16T23:23:35 |
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
| REVIEW-ONAY-KUYRUGU-01 | Onay kuyrugundaki 2 teslimi denetle (ADMIN-LOGIN-FIX-01, ADMIN-MODAL-STIL-01) | yasu | - |
| TEST-AYARLAR-KAPSAM-01 | [TEST] Kullanici Ayarlari sayfasi icin test iskeleti yaz (tests/ altinda) | yasu | 2026-09-22T05:56:24 |
| UI-AYARLAR-SAYFA-01 | [UI] Kullanici Ayarlari sayfasini yaz → web_dashboard/tabs/admin_kullanici_ayarlari.py (2s) | ihsan | 2026-09-19T16:24:16 |
| ORKESTRA-BASLIK-GERIYE-01 | [ORKESTRA] Acik gorev basliklarini D-57 kalibina tasi → data/orchestrator/task_board.json (2s) | yasu | 2026-09-19T11:39:13 |
| TEST-MERVE-KAPSAM-01 | [TEST] Ayarlar sayfasi testlerini denetle → data/orchestrator/TEST-MERVE-KAPSAM-01_rapor_2026-09-18_denetim.md (2s) | salih | 2026-09-19T11:38:58 |
| ORKESTRA-SPRINT-01 | [ORKESTRA] düzelt tetik gecikmesini (posta kutusu senkronu) → src/company_master/orchestrator/trigger.py (2s) | ihsan | 2026-09-19T10:43:19 |
| ORKESTRA-SPRINT-02 | [ORKESTRA] düzelt bagimlilik zinciri deadlock'unu → scripts/optimize_plan.py (2s) | ihsan | 2026-09-19T10:44:42 |
| ORKESTRA-SPRINT-03 | [ORKESTRA] ölç onay kuyrugu bekleme suresini → data/orchestrator/onay_kuyrugu_metrik.json (1s) | ihsan | 2026-09-19T10:45:37 |
| TEST-SPRINT-04 | [TEST] yaz P2 gorevler icin zorunlu test kapisini → scripts/kodlama_denetim.py (2s) | utku | 2026-09-19T10:43:19 |
| ALTYAPI-SPRINT-05 | [ALTYAPI] düzelt dosya kilidi cakisma hatasini → src/company_master/orchestrator/task_board.py (2s) | utku | 2026-09-19T10:44:42 |
| ORKESTRA-SPRINT-06 | [ORKESTRA] düzelt inceleme atlanan commit yolunu → .pre-commit-config.yaml (1s) | utku | 2026-09-19T10:45:37 |
| TEST-SPRINT-07 | [TEST] yaz bagimli modul regresyon suitini → tests/test_regresyon_bagimli.py (4s) | salih | 2026-09-19T10:43:19 |
| ALTYAPI-SPRINT-08 | [ALTYAPI] yaz surum oncesi dogrulama kontrol listesini → docs/SURUM_ONCESI_KONTROL.md (1s) | salih | 2026-09-19T10:44:42 |
| DOC-SPRINT-09 | [DOC] belgele test sonuc raporu formatini → docs/TEST_RAPOR_FORMATI.md (1s) | salih | 2026-09-19T10:45:37 |
| ALTYAPI-SPRINT-10 | [ALTYAPI] denetle admin API auth bypass acigini → data/orchestrator/ALTYAPI-SPRINT-10_rapor_denetim.md (2s) | yasu | 2026-09-19T10:43:19 |
| ALTYAPI-SPRINT-11 | [ALTYAPI] denetle katman sinirlarini ihlal eden degisiklikleri → data/orchestrator/ALTYAPI-SPRINT-11_rapor_denetim.md (2s) | yasu | 2026-09-19T10:44:42 |
| DOC-SPRINT-12 | [DOC] belgele eksik API endpoint referansini → docs/API_REFERANS.md (2s) | yasu | 2026-09-19T10:45:38 |
| UI-MUSTERI-SUBHEADER-01 | [UI] musteri_yonetimi subheader duzelt → musteri_yonetimi.py (2s) | utku | 2026-09-19T17:18:59 |
| UI-PROFILMENU-01 | [UI] Profil menu yaz → profil_menu.py (4s) | salih | 2026-09-20T05:55:02 |
| UI-MENUTREE-02 | [UI] Sol menu agaci düzelt → __init__.py (4s) | utku | 2026-09-20T08:10:46 |
| DOC-SIRKET-MASTER-01 | [DOC] Şirket Master ana belgesi düzelt -> 01_sirket_master_ana_belgesi.md (3s) | utku | - |
| UI-AYARLAR-SAYFA-02 | [UI] Ayarlar sayfası yaz → admin_kullanici_ayarlari.py (4s) | utku | 2026-09-20T07:01:13 |
| ALTYAPI-KILIT-TEMIZLE-01 | [ALTYAPI] Duzelt kilitleri → file_locks.json (1s) | yasu | 2026-09-23T07:08:00 |
| UI-PROFILMENU-POPOVER-02 | [UI] native st.popover'a taşı → profil_menu.py (2s) | utku | 2026-09-20T07:37:55 |
| ORKESTRA-STALE-TEMIZLIK-01 | [ORKESTRA] Denetle → YASU stale görevleri (1s) | yasu | 2026-09-20T16:39:03 |
| ALTYAPI-SQLITE-INIT | [ALTYAPI] SQLite fixture companies tablosunu yaz → tests/conftest.py (2s) | utku | 2026-09-20T13:25:49 |
| ALTYAPI-GOREVAT-GUNCELLE-01 | [ALTYAPI] gorev_at.py guncelle komutu yaz → scripts/gorev_at.py (1s) | utku | 2026-09-20T11:18:57 |
| UI-MENU-FORM-01 | [UI] Kullanıcı menü form entegrasyonu → web_dashboard/pages/menu.py (2s) | utku | 2026-09-20T11:42:20 |
| UI-FORM-VALIDATION-02 | [UI] Form doğrulama kütüphanesi yaz → src/company_master/ui/forms/validators.py (2s) | utku | 2026-09-20T11:57:28 |
| ALTYAPI-FORM-SETUP-03 | [ALTYAPI] Form altyapısı hazırlığı (config, builder) → src/company_master/ui/forms/builder.py (2s) | utku | 2026-09-20T12:11:49 |
| DOC-V10-AUDIT-01 | [DOC] V10 belge uyum denetimi (AGENTS.md, decision_log, task_board) → data/orchestrator/DOC-V10-AUDIT-01_rapor_2026-09-20_orkestrator.md (2s) | ihsan | 2026-09-20T16:39:09 |
| ORKESTRA-NAMING-AUDIT-02 | [ORKESTRA] D-55/D-57 adlandırma kurallarını denetle → data/orchestrator/ORKESTRA-NAMING-AUDIT-02_rapor_2026-09-20_orkestrator.md (2s) | ihsan | 2026-09-23T23:09:51 |
| ORKESTRA-DECISION-LOG-03 | [ORKESTRA] Karar defterini düzelt → data/orchestrator/ORKESTRA-DECISION-LOG-03_rapor_2026-09-20_orkestrator.md (2s) | ihsan | 2026-09-24T01:30:13 |
| ALTYAPI-WEB-MONITOR-01 | [ALTYAPI] Web uygulaması canlı monitoring (health check, metrics) → src/company_master/monitoring/health.py (2s) | utku | 2026-09-20T12:33:52 |
| ALTYAPI-PROXY-CONFIG-02 | [ALTYAPI] Reverse proxy yapılandırması (Nginx) → config/nginx.conf (2s) | utku | 2026-09-20T12:47:26 |
| TEST-PLAN-COVERAGE-03 | [TEST] Test kapsam planı ve otomasyon → docs/TEST_PLAN.md (2s) | utku | 2026-09-20T13:13:37 |
| TEST-KAPSAM-OLCUM-01 | [TEST] Mevcut test kapsamını ölç ve raporla → docs/raporlar/test_kapsam_olcum_2026-09-20.md (2s) | salih | 2026-09-20T17:02:49 |
| ALTYAPI-BENCHMARK-02 | [ALTYAPI] Performans ölçümü (API+Streamlit) → docs/raporlar/benchmark_2026-09-20.md (2s) | salih | 2026-09-20T20:25:35 |
| ALTYAPI-BILGI-TABANI-03 | [ALTYAPI] Runbook ve uyum denetimi belgele → docs/RUNBOOK.md (2s) | salih | 2026-09-20T19:32:28 |
| ORKESTRA-DUPLIK-KAPAYANIM-01 | [ORKESTRA] Çakışan görevleri araştır → data/orchestrator/ORKESTRA-DUPLIK-KAPAYANIM-01_rapor_2026-09-20_denetim.md (30d) | yasu | 2026-09-20T19:37:31 |
| ORKESTRA-BRIEF-KALITE-01 | [ORKESTRA] 12 yeni brifi denetle → data/orchestrator/ORKESTRA-BRIEF-KALITE-01_rapor_2026-09-20_denetim.md (1s) | yasu | 2026-09-20T19:37:31 |
| ORKESTRA-KARAR-DEFTERI-AUDIT-01 | [ORKESTRA] Karar defterini denetle → data/orchestrator/ORKESTRA-KARAR-DEFTERI-AUDIT-01_rapor_2026-09-20_denetim.md (30d) | yasu | 2026-09-20T18:58:23 |
| ALTYAPI-TEST-FAILURE-FIX-01 | [ALTYAPI] düzelt 4 pre-existing test failure → data/orchestrator/ALTYAPI-TEST-FAILURE-FIX-01_rapor_2026-09-20_uretim.md (2s) | utku | 2026-09-20T16:38:45 |
| ORKESTRA-VAULT-TEKRAR-01 | [ORKESTRA] denetle vault isim tekrarlari → ORKESTRA-VAULT-TEKRAR-01_rapor.md (2s) | ihsan | 2026-09-23T07:21:00 |
| TEST-D77-02 | [TEST] Done task | utku | 2026-09-20T16:32:21 |
| ORKESTRA-KARAR-DEFTERI-FIX-01 | [ORKESTRA] decision_log.jsonl kayıtlarını düzelt → data/orchestrator/decision_log.jsonl (1s) | ihsan | 2026-09-20T19:50:48 |
| ORKESTRA-BACKLOG-KANIT-01 | [ORKESTRA] Backlog kanıt-satırı kuralı yaz → AGENTS.md D-66 güncelleme (2s) | ihsan | 2026-09-20T19:40:18Z |
| ALTYAPI-DECISION-LOG-ENCODE-01 | [ALTYAPI] Decision log UTF-8 kodlamayı denetle → decision_log.jsonl (1s) | ihsan | 2026-09-20T19:40:18Z |
| TEST-D77-01 | [TEST] Pano işleri orkestrator kuralı denetle → TEST-D77-01_rapor_2026-09-20_orkestrator.md (2s) | ihsan | - |
| ORKESTRA-BASLIK-D57-FIX-01 | [ORKESTRA] 11 görev başlığını düzelt → task_board.json (2s) | ihsan | 2026-09-20T21:05:27 |
| ALTYAPI-TEST-FAILURE-FIX-02 | [ALTYAPI] Test hatasi duzelt → tests/test_mcp.py (2s) | utku | 2026-09-22T05:55:44 |
| TEST-PANO-IZOLASYON-01 | [TEST] Pano izolasyon duzelt → tests/test_pano_bakim_d77.py (1s) | salih | 2026-09-20T21:58:45 |
| ORKESTRA-DECISION-LOG-FORMAT-01 | [ORKESTRA] Decision log format duzelt → data/orchestrator/decision_log.jsonl (4s) | ihsan | - |
| ALTYAPI-KILIT-YOL-FIX-01 | [ALTYAPI] kilit yolunu düzelt → file_locks.json (1s) | utku | - |
| ALTYAPI-PANO-ENCODING-FIX-01 | [ALTYAPI] pano encoding hatalarini duzelt → task_board.json (2s) | utku | 2026-09-22T05:55:45 |
| TEST-BATCH-01 | [TEST] batch lock test -> _tmp (1s) | utku | 2026-09-22T06:54:43 |
| DASH-UX-02a-SECTIONS | [DOC] duzelt [DASH-UX] DASH-UX-02a-SECTIONS: admin_sistem sekme -> web_dashboard/tabs/__init__.py (2s) | utku | 2026-09-22T08:57:51 |
| ORKESTRA-IHSAN-TETIK-01 | [ORKESTRA] Ihsan tetik dosyasini duzelt → triggers/ihsan.jsonl (1s) | ihsan | 2026-09-22T00:01:33 |
| ORKESTRA-ONAY-KUYRUGU-02 | [ORKESTRA] Onay kuyrugundaki 3 teslimi denetle → data/orchestrator/REVIEW-ONAY-KUYRUGU-02_rapor_2026-09-21.md (1s) | ihsan | 2026-09-22T08:08:25.639765 |
| ORKESTRA-ONAY-KUYRUK-01 | [ORKESTRA] Onay kuyrugunu denetle → onay_kuyrugu.json (1s) | yasu | 2026-09-22T00:23:52 |
| ORKESTRA-TETIK-TEMIZLIK-01 | [ORKESTRA] ihsan postasindaki 5 yinelenen DASH-UX-02a tetigini sil | ihsan | 2026-09-22T00:01:33 |
| ORPHAN-ARASTIRMA-01 | [ARASTIRMA] 4 orphan kuyruk kaydi — pano kayit kurali oncesi mi? | yasu | 2026-09-22T12:41:45 |
| TEST-GRAPH-KOPRU | [TEST] denetle backlink_sayimi → dogrulama_raporu.md (2s) | utku | 2026-09-21T19:13:28 |
| VERI-ARSIV-01 | [VERI] düzelt gizleme_filtreleri → app.json (2s) | utku | 2026-09-21T19:03:26 |
| VERI-GRAPH-01 | [VERI] yaz wikilink kopruleri → graph_kopru_d182.md (4s) | utku | 2026-09-21T18:48:32 |
| VERI-ARSIV-01 | [VERI] düzelt gizleme_filtreleri → app.json (2s) | utku | 2026-09-21T19:03:26 |
| TEST-GRAPH-KOPRU | [TEST] denetle backlink_sayimi → dogrulama_raporu.md (2s) | utku | 2026-09-21T19:13:28 |
| UI-ADOPT-01 | [UI] UI-ADOPT-01: kpi_karti() -> MetricCard bileşen benimsemesi (admin_auto_refresh, admin_api_analytics, admin_performance) | utku | - |
| CHART-KATEGORI-02 | [CHART] KATEGORI_RENK <-> KATEGORILER uyumlaştırması → web_dashboard/charts.py (1s) | utku | - |
| TEST-DASHBOARD-REGRESYON-01 | [TEST] Dashboard test regresyonu: 8 kırık + 71 kayıp test araştırması (2s) | utku | - |
| ADMIN-UI-CACHE-OPT-01 | [ALTYAPI] Admin UI cache optimizasyonu ve TTL ayarlari | yasu | 2026-09-23T23:10:04 |
| GRAPH-CANONICAL-SECER-02 | [GRAPH] Canonical graph baglanti guvenligi secer | yasu | 2026-09-23T23:10:05 |
| AGENTS-MERGE-UU | [DOC] AGENTS.md kok/vault kopuklugunu duzelt → tek SSOT + D-188 (2s) | ihsan | 2026-09-24T01:25:02 |
| VAULT-CLEANUP-BATCH | [ALTYAPI] Vault alarm/tetik artiklarini sil → temiz kuyruk (1s) | ihsan | 2026-09-24T01:59:12 |
| ADMIN-UX-SIDEBAR-TAB | [UI] Sidebar tab secim durumunu sakla -> web_dashboard/tabs/__init__.py (2s) | utku | 2026-09-23T23:09:51 |
| ORKESTRA-GOREV-KAPI-01 | [ORKESTRA] Gorev atama kapisini düzelt → scripts/gorev_at.py (4s) | ihsan | 2026-09-23T23:09:39 |
| ALTYAPI-KILIT-OTOMATIK-01 | [ALTYAPI] Kilit otomatik birakmayi yaz → src/company_master/orchestrator/task_board.py (3s) | yasu | 2026-09-24T01:59:37 |
| ALTYAPI-TETIK-ARSIV-01 | [ALTYAPI] Kanonik olmayan tetik dosyalarini taşı → data/orchestrator/triggers/_arsiv_2026-09-23/ (2s) | yasu | 2026-09-23T23:10:05 |
| ALTYAPI-MOJIBAKE-DIZIN-01 | [ALTYAPI] mojibake_onar.py dizin taramasini yaz → mojibake_onar.py (2s) | yasu | 2026-09-24T01:59:13 |
| ALTYAPI-IMPORT-TEKLES-01 | [ALTYAPI] trigger.py import yolunu düzelt → trigger.py (1s) | yasu | 2026-09-23T17:06:52 |
| ALTYAPI-TETIK-ZAMAN-01 | [ALTYAPI] tetik_senk zamanlamasini yaz → tetik_senk.py (2s) | yasu | 2026-09-24T01:59:13 |
| TEST-ADMIN-PERF-01 | [TEST] admin_performance kpi_karti gecisini yaz → web_dashboard/tabs/admin_performance.py (2s) | utku | 2026-09-24T02:24:43 |
| TEST-WEBHOOK-KPI-01 | [TEST] webhook_monitor mock hedefini duzelt → tests/test_webhook_monitor_tab.py (1s) | utku | 2026-09-24T01:59:13 |
| UI-SUBHEADER-MUSTERI-01 | [UI] musteri_yonetimi subheader temizligini yaz → web_dashboard/tabs/musteri_yonetimi.py (2s) | utku | 2026-09-24T01:59:13 |
| ALTYAPI-MARKA-HUGGINN-01 | [ALTYAPI] HUGGINN yazimini duzelt → marka_denetim temiz (3s) | yasu | 2026-09-23T17:06:23 |
| ALTYAPI-D182-MIMIR-01 | [ALTYAPI] mimir ajanini yaz → trigger.AJANLAR (2s) | ihsan | 2026-09-23T23:09:52 |
| ORKESTRA-D65-ISDURMAZ-01 | [ORKESTRA] ölç D-65 İş Durmaz ihlalini → data/orchestrator/ORKESTRA-D65-ISDURMAZ-01_rapor.md (3s) | ihsan | 2026-09-23T23:09:52 |
| ALTYAPI-MOJIBAKE-BARIYER-01 | [ALTYAPI] Mojibake araci yazim-oncesi hasar bariyeri → scripts/mojibake_onar.py (2s) | ihsan | 2026-09-23T23:09:39 |
| ALTYAPI-DURUM-SOZLUK-01 | [ALTYAPI] Gorev durum sozlugu tutarsizligini düzelt → task_board.py (2s) | ihsan | 2026-09-23T23:09:52 |
| ALTYAPI-TEST-HERMETIK-01 | [ALTYAPI] Uretim verisine dokunan testleri düzelt → tests/test_d87_atama_otomasyonu_fixed.py (2s) | ihsan | 2026-09-23T23:09:52 |
| ALTYAPI-D66-BYPASS-TETIKLEME-01 | [ALTYAPI] duzelt tetik_senk.py bypass flag -> tetik_senk.py (2s) | ihsan | 2026-09-24T01:28:33 |
| TEST-13-PREEXIST-DUZELT-01 | [TEST] düzelt 13 pre-existing hata → d193_menu_e2e_report.md (3s) | utku | 2026-09-24T01:59:13 |
| ALTYAPI-GROQ-KEY-DOGRULA-01 | [ALTYAPI] denetle Groq canlı key → groq_client.chat() test (30d) | yasu | 2026-09-24T01:44:00 |
| D-192-FAZ2 | [ADMIN-UI] Ajan Chat Faz 2: Onem Derecesi + Cozum kolonu + 6 ajan rengi + Tarih sona tasindi | orkestrator | 2026-09-23T22:00:00 |
| NINEROUTER-IMAGE-GEN-01 | [SKILL] ninerouter.py'ye ninerouter_image_gen ekle | yasu | 2026-09-24T01:44:00 |
| TEST-13-PREEXIST-DUZELT-02 | [TEST] duzelt 7 kalan test hatasi → pytest yesil (2s) | utku | 2026-09-24T03:46:16 |
| UI-ADMIN-SAHTE-KPI-01 | [UI] Sahte API KPI kartını düzelt → admin_kpi.py rozetli boş kart (2s) | utku | 2026-09-24T05:47:14 |
| UI-ADMIN-SAHTE-EXEC-02 | [UI] Sahte gelir kartlarını düzelt → admin_executive.py rozetli boş kart (2s) | utku | 2026-09-24T05:47:14 |
| UI-ADMIN-SSE-IHLAL-03 | [UI] SSE mimari ihlalini düzelt → admin_realtime.py polling (3s) | ihsan | 2026-09-24T04:43:33 |
| VERI-ADMIN-LASTLOGIN-MIGRATION-04 | [VERI] users.last_login kolonunu yaz → schema migration (1s) | ihsan | 2026-09-24T04:43:33 |
| API-ADMIN-LASTLOGIN-YAZ-05 | [API] Giriş anında last_login değerini yaz → auth akışı (1s) | ihsan | 2026-09-24T04:43:34 |
| API-ADMIN-CHURN-FONKSIYON-06 | [API] Churn risk fonksiyonunu yaz → churn.py saf fonksiyon (2s) | ihsan | 2026-09-24T04:43:34 |
| UI-ADMIN-CHURN-KOLON-07 | [UI] Churn risk kolonunu yaz → musteri_yonetimi.py listesi (1s) | ihsan | 2026-09-24T04:53:44 |
| UI-ADMIN-MAU-08 | [UI] Yanlış DAU etiketini düzelt → admin_kpi.py gerçek MAU (2s) | ihsan | 2026-09-24T04:53:44 |
| UI-ADMIN-KULLANICI-BIRLESTIR-09 | [UI] Üç kopya kullanıcı yönetimini taşı → tek modül (3s) | utku | 2026-09-24T05:47:15 |
| UI-ADMIN-GUNCELLIK-KOVA-10 | [UI] Veri güncellik kovalarını yaz → admin_quality.py dağılımı (2s) | utku | 2026-09-24T05:47:15 |
| UI-ADMIN-MALIYET-ANOMALI-11 | [UI] AI maliyet anomali bloğunu yaz → admin_cost.py z-skor (2s) | utku | 2026-09-24T05:47:15 |
| DOC-ADMIN-ARSIV-12 | [DOC] Bayat analiz dökümanını taşı → arşiv + §0.1 güncel (1s) | utku | 2026-09-24T05:41:46 |
