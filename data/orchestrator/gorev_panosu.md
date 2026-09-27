# Gorev Panosu — Orkestrator

> Merkezi gorev listesi: herkes herkesin ne yaptigini takip eder.
> Kaynak: `data/orchestrator/task_board.json` — Obsidian okumasi icin disa aktarilir.

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum | Dosyalar |
|-------|--------|-------|---------|-------|----------|
| ALTYAPI-D66-BYPASS-TETIKLEME | [ALTYAPI] D-65 Is Durmaz Bypass Tetikleme -> pano_duzenleme (2s) | ihsan | P1 | iptal | scripts/pano_denetim.py, scripts/tetik_senk.py, tests/test_d66_bypass_tetikleme.py |
| UTKU-02 | [UTKU] API endpoint optimizasyon - response time (2s) | utku | P1 | archive | src/api/endpoints.py |
| UTKU-04 | [UTKU] Veritabanı migration - index optimizasyon (1s) | utku | P1 | archive | src/company_master/schema/migrations/0020_index_optimization.sql |
| UTKU-05 | [UTKU] Kullanıcı kimlik doğrulama - token yenileme (2s) | utku | P0 | archive | src/auth/token_refresh.py |
| ORCH-01 | [ORCH] İş akışı koordinasyon - görev planlama (2s) | ihsan | P0 | archive | orchestration/workflow_coordinator.py |
| ORCH-02 | [ORCH] Bağımlılık yönetimi - görüntü grafiği (2s) | ihsan | P1 | archive | orchestration/dependency_graph.py |
| ORCH-03 | [ORCH] Görev dağıtımı - load balancing (2s) | ihsan | P0 | archive | orchestration/load_balancer.py |
| ORCH-04 | [ORCH] Hata toleransı - retry mekanizması (2s) | ihsan | P1 | archive | orchestration/retry_handler.py |
| ORCH-05 | [ORCH] İzleme ve metrikler - telemetri sistemi (3s) | ihsan | P0 | archive | orchestration/telemetry.py |
| ALTYAPI-TEST-FAILURE-FIX-02 | [ALTYAPI] Test hatasi duzelt -> tests/test_mcp.py | utku | P1 | archive | - |
| ALTYAPI-KILIT-TEMIZLE-01 | [ALTYAPI] Kilitleri duzelt -> file_locks.json | yasu | P2 | archive | - |
| TEST-AYARLAR-KAPSAM-01 | Kullanici Ayarlari sayfasi icin test iskeleti yaz | yasu | P2 | archive | - |
| ADLANDIRMA-GERIYE-01 | D-55 geriye donuk: rapor dosyalarindan ajan adini kaldir | ihsan | P3 | archive | - |
| V10-BELGE-01 | 6 curutulen iddiaya K1/K3/K4 duzeltme notu | ihsan | P1 | archive | - |
| WK-02 | OSB Tender Monitor - Real-time Tracking | - | P1 | archive | - |
| WK-03 | Proxy Rotation and IP Management | - | P2 | archive | - |
| VERI-02 | [VERI] OSB ihale izleyicisini yaz → src/scrapers/osb_tender_monitor.py (3s) | utku | P1 | plan | - |
| VERI-03 | [VERI] Proxy rotasyonunu yaz → src/scrapers/proxy_rotation.py (2s) | utku | P2 | plan | - |
| SEMA-01 | Migration down dosyalarinda ad/yol duzeni tek standarda baglansin | - | P1 | plan | src/company_master/schema/migrations/, tests/test_migration_0017.py, tests/test_schema_validation.py |
| API-07 | 11 yeni API rotasi envantere islensin + match 404 dogrulamasi | - | P1 | plan | tests/test_api_integration.py, src/api/ |
| UI-11 | admin_mfa + ana_kontrol ekranlari ADMIN-UI-10 kalibina tasinsin | - | P2 | plan | tests/test_sayfa_iskeleti.py |

## Tamamlananlar

| Görev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| VERI-ADMIN-AKTIVITE-LOG-13 | [VERI] Kullanıcı aktivite log tablosunu yaz → migration 0017 (2s) | utku | 2026-09-24T19:25:07 |
| API-ADMIN-AKTIVITE-YAZ-14 | [API] Giriş/arama/AI olaylarını log'a yaz → web_app.py + arama uçları (2s) | utku | 2026-09-24T20:56:00 |
| DOC-ADMIN-DURUM-SENKRON-15 | [DOC] Bayat durum satırlarını düzelt → §8.4/§10 kanıtlı (1s) | ihsan | 2026-09-24T20:56:00 |
| API-ADMIN-CHURN-3SINYAL-16 | [API] Churn kuralını 3 sinyalli hâlde yaz → churn.py tam formül (2s) | utku | 2026-09-24T20:56:00 |
| UI-ADMIN-DAU-17 | [UI] Gerçek DAU kartını yaz → admin_kpi.py aktivite sorgusu (2s) | utku | 2026-09-24T19:25:07 |
| API-ADMIN-KAYNAK-SAGLIK-18 | [API] Kaynak sağlık skorunu ölç → 3 kovalı rozet + DLQ birikme hızı (2s) | yasu | 2026-09-24T23:38:00 |
| UI-ADMIN-CRAWL-KONTROL-19 | [UI] Crawl tetikle/durdur aksiyonunu yaz → operatör kontrol paneli (3s) | yasu | 2026-09-24T23:38:00 |
| UI-ADMIN-ARAMA-BOSLUK-20 | [UI] Sonuçsuz arama frekans raporunu yaz → içerik boşluk raporu (2s) | utku | 2026-09-24T20:56:00 |
| API-ADMIN-SUPHELI-AKTIVITE-21 | [API] Şüpheli aktivite kurallarını yaz → 3 sinyalli güvenlik uyarısı (3s) | utku | 2026-09-24T20:56:00 |
| UI-ADMIN-UPSELL-22 | [UI] Upsell aday listesini yaz → satış aksiyon listesi (2s) | utku | 2026-09-24T20:56:00 |
| TEST-ADMIN-K2-AGIRLIK-23 | [TEST] K2 ağırlık şemasını denetle → test + SSOT kanıt (1s) | yasu | 2026-09-25T04:26:42 |
| DOC-ADMIN-V9-KUTUCUK-24 | [DOC] V9 §16.5 kutucuklarını düzelt → 6 madde (1s) | utku | 2026-09-24T20:56:00 |
| UI-ADMIN-FEATURE-FLAG-25 | [UI] Feature flag yönetim ekranını yaz → A5 MVP (3s) | utku | 2026-09-25T04:36:47 |
| API-ADMIN-MFA-26 | [API] MFA + hesap kilidi akışını yaz → A6 auth (4s) | utku | 2026-09-26T04:06:34 |
| UI-ADMIN-LTV-CAC-27 | [UI] LTV/CAC kartlarını yaz → K8 tamamlama (2s) | utku | 2026-09-25T22:31:25 |
| DOC-ADMIN-MULTITENANT-KARAR-28 | [DOC] Multi-tenant kararını belgele → KK-7 (1s) | utku | 2026-09-25T22:31:15 |
| TEST-BLOKE-FAKTOR-ARASTIRMA-01 | [TEST] Test hazirlik plani arastir → test_bloke_hazirlik.py (3s) | yasu | 2026-09-24T22:11:11.842076 |
| ALTYAPI-SECRETS-SETUP-01 | [ALTYAPI] Vault kurup .env template yaz → .env.example (2s) | ihsan | 2026-09-24T20:56:00 |
| ALTYAPI-DB-MIGRATION-01 | [ALTYAPI] v0016 → v0017 prod migration planı yaz → db_migrate_prod.sh (1s) | utku | 2026-09-26T14:48:08 |
| ALTYAPI-ADMIN-PANO-01 | [ALTYAPI] Task board 4 bolum yaz → render_task_board_tab.py (2s) | ihsan | 2026-09-24T20:56:00 |
| ORKESTRA-AI-CHAT-KOORDINASYON-01 | [ORKESTRA] Ajan arasi protokol yaz → ajan_chat_koordinasyon.py (3s) | ihsan | 2026-09-24T22:02:28 |
| ALTYAPI-VERI-GORUNURLUK-01 | [ALTYAPI] Katmanlı görünürlük & kontör sistemi → 0018 migration + 3 tablo (4s) | ihsan | 2026-09-25T22:48:38 |
| API-KVKK-KONTROL-25 | [API] Kontör endpoint entegrasyonu (match/ilan) → _charge_module_credit çağrısı | yasu | 2026-09-25T22:48:38 |
| TEST-VISIBILITY-ENTEGRASYON-27 | [TEST] E2E senaryo testi (visibility layer + kontör) → 5 scenario + 4 conflict | yasu | 2026-09-25T22:48:38 |
| UI-ADMIN-KVKK-MODU-26 | [UI] Admin KVKK mode toggle (strict ↔ lenient) → web_app POST endpoint | utku | 2026-09-25T22:29:48 |
| UI-ADMIN-KVKK-RAPOR-28 | [UI] KVKK maskeleme raporu → admin paneline ek sekme | utku | 2026-09-25T04:36:54 |
| DOC-VISIBILITY-KATMANI-29 | [DOC] Kullanıcı dokümanı (görünürlük katmanı + kontör) → markdown guide | utku | 2026-09-25T04:36:47 |
| API-LAYER2-DINAMIK-YÜKLEME-30 | [API] Layer 2 dinamik yükleme → plan_field_group tablosundan görünürlük oku | yasu | 2026-09-25T22:48:39 |
| KONTROL-KVKK-MASKELEME-31 | [KONTROL] KVKK maskeleme end-to-end test → admin panel e2e | yasu | 2026-09-25T22:48:39 |
| UI-KONTROL-PANOSU-32 | [UI] Admin kontrol panosu → maskeleme durum metriksleri | utku | 2026-09-25T04:36:47 |
| DOKUMAN-KVKK-FAQ-33 | [DOC] KVKK FAQ & sorun çözme → markdown troubleshooting guide | utku | 2026-09-25T04:36:47 |
| UTKU-01 | [UTKU] Veri şeması doğrulama - Core modülü (2s) | utku | 2026-09-25T20:30:00 |
| UTKU-03 | [UTKU] Hata loglama sistemi - production hazırlığı (2s) | utku | 2026-09-26T14:30:53 |
| YASU-01 | [YASU] Frontend bileşen kütüphanesi - temel UI (3s) | yasu | 2026-09-26T04:06:33 |
| YASU-02 | [YASU] Responsive tasarım - mobil uyumluluk (2s) | yasu | 2026-09-26T04:06:33 |
| YASU-03 | [YASU] Grafiksel dashboard - veri görselleştirme (3s) | yasu | 2026-09-26T04:06:33 |
| YASU-04 | [YASU] Durum yönetimi - state management (2s) | yasu | 2026-09-26T04:06:33 |
| YASU-05 | [YASU] Erişilebilirlik - WCAG 2.1 uyumu (2s) | yasu | 2026-09-26T04:06:34 |
| ADMIN-UX-GELIR-GRUP-01 | Gelir&Paketler grubu tamamla: executive+maliyet sekmelerini ust=gelir'e tasi | utku | 2026-09-25T23:21:54 |
| UI-ADMIN-MENU-D215216 | [UI] Admin menü ağacını düzelt → web_dashboard/tabs/__init__.py (3s) | utku | 2026-09-27T00:20:36 |
| RESEARCH-PONYTALE | Ponytail vs Caveman derinlemesine arastirma | ihsan | 2026-09-27T02:35:00 |
| DOC-SIRKET-MASTER-01 | [DOC] Sirket Master ana belgesi duzelt | utku | 2026-09-27T02:35:00 |
| REVIEW-ONAY-KUYRUGU-01 | Onay kuyrugundaki 2 teslimi denetle | yasu | 2026-09-27T02:35:00 |
| AGN-CREWAI-PILOT-01 | crewAI hibrit worker pilotu (metin uretimi deneyi) | ihsan | 2026-09-27T02:35:00 |
| ORKESTRA-DECISION-LOG-03 | [ORKESTRA] Karar defteri duzenleme ve validasyon | ihsan | 2026-09-27T02:35:00 |
| ORKESTRA-NAMING-AUDIT-02 | [ORKESTRA] D-55/D-57 adlandirma kurallari denetimi | ihsan | 2026-09-27T02:35:00 |
| ORKESTRA-BRIEF-TALIMAT-01 | [ORKESTRA] 4 brife talimat dosyasi yaz | yasu | 2026-09-27T02:35:00 |
| ORKESTRA-VAULT-TEKRAR-01 | [ORKESTRA] Vault isim tekrarlarini denetle | ihsan | 2026-09-27T02:35:00 |
| VAULT-ORPHAN-INCELEME-01 | [VAULT] Orphan nod siniflama: 3361 dosya, D-173 | orkestrator | 2026-09-27T02:35:00 |
