# Admin Dashboard Hub

> Konu-bazli hub (PO karari 2026-09-21): Admin/Muninn paneli ile ilgili tum stratejik,
> mimari ve tasarim dokumanlari tek noktada. Yurutme raporlari (data/orchestrator/ADMIN-*_rapor*)
> bu hub'a dahil edilmedi — gurultu onlemek icin yalnizca karar/mimari/tasarim seviyesi belgeler secildi.

Uretim: Sprint Graf Hub'lastirma FAS-2 (2026-09-21). Bagli dokuman: **28** (2026-09-24: gorev taslagi + 10 brief eklendi)

Ana baglam: [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]] · [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]] · [[Huginn Data Insights/hubs/REPORTS_ANALYSIS_HUB]] · [[Huginn Data Insights/hubs/OSINT_INDEX]] · [[Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB]] · [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]] · [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]] · [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]] · [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]] · [[Huginn Data Insights/AGENTS]] · [[Huginn Data Insights/PROJECT_ROADMAP]] · [[Huginn Data Insights/hubs/V10_POC_HUB]]

---

## Kaynak / Sistem Referansi

- [[Huginn Data Insights/docs/ADMIN_UI_SISTEMI]] — Ana referans: tum admin sekmelerinin kod haritasi
- `Huginn Data Insights/AI proje v1/V10/wiki/admin_panel_kilavuz` — Kullanim kilavuzu

## Mimari Kararlar

- [[Huginn Data Insights/docs/ARCHITECTURE_DECISION_HYBRID_ADMIN]] — Hybrid Admin Panel karar dokumani
- `Huginn Data Insights/AI proje v1/V10/03_mimari/02_muninn_super_admin_panel_prd_ve_yol_haritasi` — PRD + yol haritasi
- `Huginn Data Insights/AI proje v1/V10/03_mimari/06_muninn_prd_vs_huginn_analiz` — PRD vs mevcut durum analizi
- `Huginn Data Insights/AI proje v1/V10/03_mimari/ADMIN-01-02-03_TASK_BRIEF` — Faz 0 gorev dagitimi

## Plan / Yol Haritasi

- [[Huginn Data Insights/docs/MUNINN_STREAMLIT_PLAN_2026-09-18]] — Muninn Streamlit plani
- [[Huginn Data Insights/docs/MUNINN_PLAN_UC_TUR_DEGERLENDIRME_2026-09-18]] — Uc tur degerlendirme
- [[Huginn Data Insights/plans/MVP_ADMIN_minimum_canli]] — Minimum canli MVP plani
- `Huginn Data Insights/AI proje v1/V10/13_po_karar_analizi` — PO karar destek analizi (metrik yonetimi)
- `Huginn Data Insights/AI proje v1/V10/14_urun_yuzeyleri_sitemap` — Urun yuzeyleri sitemap (Muninn/Huginn ayrimi)

## UX / Tasarim

- [[Huginn Data Insights/docs/UX_ADMIN_PANEL_REVIEW_2026-09-14]] — UX audit + premium arayuz plani
- [[Huginn Data Insights/docs/UX_ANA_SAYFA_WIREFRAME_2026-09-18]] — Ana sayfa wireframe
- [[Huginn Data Insights/docs/UX_AYARLAR_SAYFA_WIREFRAME_2026-09-18]] — Ayarlar sayfasi wireframe
- [[Huginn Data Insights/docs/UX_MENU_AGACI_WIREFRAME_2026-09-18]] — Menu agaci wireframe
- [[Huginn Data Insights/docs/UI_MODAL_CHART_ARASTIRMA_2026-09-15]] — Modal/chart arastirmasi

## Uygulama Tasarim Zinciri (2026-09-20)

- `Huginn Data Insights/data_worktree/orchestrator/ZINCIR-ADMIN-PANEL-UX-TASARIMI_2026-09-20_orkestrator` — UX zincir tasarimi (menu, profil, logout)

## Gorev Uretim Taslagi (2026-09-24, kalici)

- [[Huginn Data Insights/data/orchestrator/gorev_taslagi]] — **Kalici gorev taslagi**: acik gorev sayaci (P0/P1/P2), ana + yedek gorevler, tur kaydi. Her yeni gorev turunda once bu dosya okunur (tekrar onleme).

## Gorev Brief'leri — Tur 2026-09-24 (ADMIN-KIT · SSOT tabanli)

| # | Brief | Oncelik | SSOT kaynagi |
|---|-------|---------|--------------|
| 13 | [[Huginn Data Insights/plans/brief_utku_VERI-ADMIN-AKTIVITE-LOG-13]] | P0 | §8.4 EK BULGU-8 · §10:366 · §12 G2 |
| 14 | [[Huginn Data Insights/plans/brief_utku_API-ADMIN-AKTIVITE-YAZ-14]] | P0 | §8.4 EK BULGU-8 · §12 G2 |
| 15 | [[Huginn Data Insights/plans/brief_utku_DOC-ADMIN-DURUM-SENKRON-15]] | P1 | §8.4 · §10 · §14 tutarsizligi |
| 16 | [[Huginn Data Insights/plans/brief_utku_API-ADMIN-CHURN-3SINYAL-16]] | P1 | §9 K1 · §10:368 · §12 G2 |
| 17 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-DAU-17]] | P1 | §8.1 A9 · §10:369 · §12 G4 |
| 18 | [[Huginn Data Insights/plans/brief_utku_API-ADMIN-KAYNAK-SAGLIK-18]] | P1 | §9 K4 |
| 19 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-CRAWL-KONTROL-19]] | P1 | §8.1 A8 · §10:373 · §12 G8 |
| 20 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-ARAMA-BOSLUK-20]] | P2 | §9 K9 · §10:375 |
| 21 | [[Huginn Data Insights/plans/brief_utku_API-ADMIN-SUPHELI-AKTIVITE-21]] | P2 | §9 K10 · §10:374 · §12 G9 |
| 22 | [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-UPSELL-22]] | P2 | §9 K7 |

SSOT: `Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani` (ADMIN-KIT, D-196)

## Kapanan isler (B-14 · hafiza izi)

> Kapanan her gorev buraya bir satir birakir. `gorev_kutusu.py teslim` bu bolumde
> task_id gormezse teslimi reddeder (`--zorla` ile gecilebilir, panoya `hafiza_izi=atlandi` islenir).
> Asagidaki satirlar TUR-B2 (2026-09-24) ile geriye donuk yazildi — denetim B-14 borcu.
> Kapi `HAFIZA_KAPISI_YURURLUK = 2026-09-24` esiginden once kapanan isleri tek tek
> aramaz; onlarin karsiligi asagidaki ceyreklik arsiv baglantisidir (D-186, D-198).

| task_id | Ne kapandi | Bitis |
|---------|------------|-------|
| UI-ADMIN-SAHTE-KPI-01 | Sahte API KPI karti duzeltildi → `web_dashboard/tabs/admin_kpi.py` gercek rozet | 2026-09-24 |
| UI-ADMIN-SAHTE-EXEC-02 | Sahte gelir kartlari duzeltildi → `web_dashboard/tabs/admin_executive.py` | 2026-09-24 |
| UI-ADMIN-SSE-IHLAL-03 | SSE mimari ihlali giderildi → `web_dashboard/tabs/admin_realtime.py` polling | 2026-09-24 |
| VERI-ADMIN-LASTLOGIN-MIGRATION-04 | `users.last_login` kolonu → schema migration | 2026-09-24 |
| API-ADMIN-LASTLOGIN-YAZ-05 | Giris aninda `last_login` yazimi → auth akisi | 2026-09-24 |
| API-ADMIN-CHURN-FONKSIYON-06 | Churn risk saf fonksiyonu → `churn.py` | 2026-09-24 |
| UI-ADMIN-CHURN-KOLON-07 | Churn risk kolonu → `web_dashboard/tabs/musteri_yonetimi.py` | 2026-09-24 |
| UI-ADMIN-MAU-08 | Yanlis DAU etiketi MAU olarak duzeltildi → `admin_kpi.py` | 2026-09-24 |
| UI-ADMIN-KULLANICI-BIRLESTIR-09 | Uc kopya kullanici yonetimi tek modulde birlestirildi | 2026-09-24 |
| UI-ADMIN-GUNCELLIK-KOVA-10 | Veri guncellik kovalari → `web_dashboard/tabs/admin_quality.py` | 2026-09-24 |
| UI-ADMIN-MALIYET-ANOMALI-11 | AI maliyet anomali blogu (z-skor) → `web_dashboard/tabs/admin_cost.py` | 2026-09-24 |
| DOC-ADMIN-ARSIV-12 | Bayat analiz dokumani arsive tasindi + SSOT §0.1 guncellendi | 2026-09-24 |
| ORKESTRA-AI-CHAT-KOORDINASYON-01 | SISTEM_PROMPT + ajan_chat_koordinasyon.py library + testler + AJAN_ARASI_ILETISIM.md dok | 2026-09-24 |
| ALTYAPI-SECRETS-SETUP-01 | Credential vault kuruldu: .env.example, .env.vault, rotate_secrets.py, config_test.py | 2026-09-24 |
| ALTYAPI-DB-MIGRATION-01 | Migration altyapisi: db_migrate.py, 0017.down.sql, db_migrate_prod.sh, AlertManager kuralari | 2026-09-24 |
| ALTYAPI-ADMIN-PANO-01 | Task board guncel gorunum: render_task_board_tab, 4 bolum, filtreleme, testler, dok | 2026-09-24 |
| API-ADMIN-AKTIVITE-YAZ-14 | Giris/arama/AI olaylari loglandi: aktivite_yaz, web_app.py, 5 test | 2026-09-24 |
| API-ADMIN-CHURN-3SINYAL-16 | Churn 3 sinyalli formulu: risk_etiketi_3sinyal, musteri_yonetimi.py SQL guncellendi | 2026-09-24 |
| UI-ADMIN-ARAMA-BOSLUK-20 | Icerik bosluk raporu: admin_quality.py, normalize+frekans+eskik, rozet, testler | 2026-09-24 |
| API-ADMIN-SUPHELI-AKTIVITE-21 | Supheli aktivite 3 kural: admin_audit.py, skor+etiket, doctest+pytest gecti | 2026-09-24 |
| UI-ADMIN-UPSELL-22 | Upsell aday listesi: musteri_yonetimi.py, 3 kosul (doygunluk+churn+buyume), testler | 2026-09-24 |
| DOC-ADMIN-V9-KUTUCUK-24 | V9 §16.5 kutucuclari: 6 madde bullet listesi, format temizlendi | 2026-09-25 |
| UI-ADMIN-KVKK-MODU-26 | KVKK Mode sekmesi: render_kvkk_mode_tab, strict/lenient toggle, API POST, testler | 2026-09-25 |
| UI-ADMIN-KVKK-RAPOR-28 | KVKK Raporu sekmesi: render_kvkk_rapor_tab, admin_kvkk_mode, KPI, trend, testler | 2026-09-25 |
| DOC-VISIBILITY-KATMANI-29 | Visibility katmani dokumani: VISIBILITY_LAYER_GUIDE.md, Layer 1/2, modul kontor, karantina | 2026-09-25 |
| DOKUMAN-KVKK-FAQ-33 | KVKK FAQ dokumani: docs/KVKK_FAQ.md, 7 SSS + 3 troubleshooting + 3 kod ornegi | 2026-09-25 |
| UI-ADMIN-FEATURE-FLAG-25 | Feature Flag sekmesi: render_feature_flags_tab, 4 flag, audit trail, testler | 2026-09-25 |
| COP-26 | MUSTERILER ekrani: firma listesi + filtre + bildirim blogu | 2026-09-24 |
| UI-SUBHEADER-MUSTERI-01 | `musteri_yonetimi.py` subheader temizligi (sayfa iskeleti sozlesmesi) | 2026-09-24 |
| TEST-ADMIN-PERF-01 | `admin_performance` kpi_karti gecis testi | 2026-09-24 |
| TEST-WEBHOOK-KPI-01 | `tests/test_webhook_monitor_tab.py` mock hedefi duzeltildi | 2026-09-24 |
| TEST-BLOKE-FAKTOR-ARASTIRMA-01 | Test hazırlık araştırma ve test skeletleri oluşturuldu | 2026-09-24 |
| API-ADMIN-KAYNAK-SAGLIK-18 | Kaynak sağlık skorunu ölç → 3 kovalı rozet + DLQ birikme hızı | 2026-09-24 |
| UI-ADMIN-CRAWL-KONTROL-19 | Crawl tetikle/durdur aksiyonunu yaz → operatör kontrol paneli | 2026-09-24 |
| TEST-ADMIN-K2-AGIRLIK-23 | K2 ağırlık şemasını denetle → test + SSOT kanıt | 2026-09-24 |
| DOC-ADMIN-DURUM-SENKRON-15 | Bayat durum satırlarını düzelt → §8.4/§10 kanıtlı (SSOT senkronize) | 2026-09-24 |
| ALTYAPI-VERI-GORUNURLUK-01 | Katmanlı görünürlük & kontör sistemi: 0018 migration (3 tablo), normalize.py dict, web_app.py SELECT düzelt, test 5+4 | 2026-09-24 |
| API-ADMIN-AKTIVITE-YAZ-14 | Giris/arama/AI olaylari loglandi: aktivite_yaz, web_app.py, 5 test | 2026-09-24 |
| API-ADMIN-CHURN-3SINYAL-16 | Churn 3 sinyalli formulu: risk_etiketi_3sinyal, musteri_yonetimi.py SQL guncellendi | 2026-09-24 |
| UI-ADMIN-ARAMA-BOSLUK-20 | Icerik bosluk raporu: admin_quality.py, normalize+frekans+eskik, rozet, testler | 2026-09-24 |
| API-ADMIN-SUPHELI-AKTIVITE-21 | Supheli aktivite 3 kural: admin_audit.py, skor+etiket, doctest+pytest gecti | 2026-09-24 |
| UI-ADMIN-UPSELL-22 | Upsell aday listesi: musteri_yonetimi.py, 3 kosul (doygunluk+churn+buyume), testler | 2026-09-24 |
| DOC-ADMIN-V9-KUTUCUK-24 | V9 §16.5 kutucuclari: 6 madde bullet listesi, format temizlendi | 2026-09-24 |
| ALTYAPI-SECRETS-SETUP-01 | Credential vault kuruldu: .env.example, .env.vault, rotate_secrets.py, config_test.py | 2026-09-24 |
| ALTYAPI-DB-MIGRATION-01 | Migration altyapisi: db_migrate.py, 0017.down.sql, db_migrate_prod.sh, AlertManager kuralari | 2026-09-24 |
| UI-ADMIN-FEATURE-FLAG-25 | Feature Flag sekmesi: render_feature_flags_tab, 4 flag, audit trail, testler | 2026-09-25 |
| UI-ADMIN-LTV-CAC-27 | LTV/CAC analiz sekmesi: render_ltv_cac_tab, KPI + trend + tier breakdown, testler | 2026-09-25 |
| DOC-ADMIN-MULTITENANT-KARAR-28 | Multi-tenant karar belgesi: MULTITENANT_ARCHITECTURE_DECISION.md, 3 model karsilastirmasi, migration path, security checklist | 2026-09-25 |
| ADMIN-UX-GELIR-GRUP-01 | Gelir grubu: GRUP_GELIR + executive+maliyet sekmeleri (ust=gelir, sira=1/2) | 2026-09-25 |

Kapanan is sayisi bu hub'da: **30**. Tam liste ceyreklik arsivde:
`data/orchestrator/task_board_arsiv_2026-Q3.json`

---

## İlgili Nodlar

- [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]]
- [[Huginn Data Insights/PROJECT_ROADMAP]]
- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]] — Kardes hub: Musteri/Huginn paneli (ayni urun, ayri kullanici kitlesi; kimlik dogrulama + kullanici yonetimi ortak)
