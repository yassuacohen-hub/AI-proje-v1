# Gorev Panosu — Orkestrator

> Merkezi gorev listesi: herkes herkesin ne yaptigini takip eder.
> Kaynak: `data/orchestrator/task_board.json` — Obsidian okumasi icin disa aktarilir.

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum | Dosyalar |
|-------|--------|-------|---------|-------|----------|
| ALTYAPI-D66-BYPASS-TETIKLEME | [ALTYAPI] D-65 Is Durmaz Bypass Tetikleme -> pano_duzenleme (2s) | ihsan | P1 | iptal | scripts/pano_denetim.py, scripts/tetik_senk.py, tests/test_d66_bypass_tetikleme.py |
| TEST-ADMIN-K2-AGIRLIK-23 | [TEST] K2 ağırlık şemasını denetle → test + SSOT kanıt (1s) | yasu | P2 | aktif | - |
| UI-ADMIN-FEATURE-FLAG-25 | [UI] Feature flag yönetim ekranını yaz → A5 MVP (3s) | utku | P2 | bekliyor | - |
| API-ADMIN-MFA-26 | [API] MFA + hesap kilidi akışını yaz → A6 auth (4s) | utku | P2 | bekliyor | - |
| UI-ADMIN-LTV-CAC-27 | [UI] LTV/CAC kartlarını yaz → K8 tamamlama (2s) | utku | P2 | bekliyor | - |
| DOC-ADMIN-MULTITENANT-KARAR-28 | [DOC] Multi-tenant kararını belgele → KK-7 (1s) | utku | P2 | bekliyor | - |
| ALTYAPI-VERI-GORUNURLUK-01 | [ALTYAPI] Katmanlı görünürlük & kontör sistemi → 0018 migration + 3 tablo (4s) | orkestrator | P0 | tamamlandi | src/company_master/schema/migrations/0018_visibility_layer.sql, field_catalog.md, src/company_master/api/core/normalize.py |
| API-KVKK-KONTROL-25 | [API] Kontör endpoint entegrasyonu (match/ilan) → _charge_module_credit çağrısı | yasu | P1 | baslatdi | web_app.py, src/company_master/schema/migrations/0018_visibility_layer.sql |
| TEST-VISIBILITY-ENTEGRASYON-27 | [TEST] E2E senaryo testi (visibility layer + kontör) → 5 scenario + 4 conflict | yasu | P1 | baslatdi | tests/test_visibility_layer.py, src/company_master/api/core/normalize.py |
| UI-ADMIN-KVKK-MODU-26 | [UI] Admin KVKK mode toggle (strict ↔ lenient) → web_app POST endpoint | utku | P1 | review | web_app.py, web_dashboard/tabs/admin_panel.py |
| UI-ADMIN-KVKK-RAPOR-28 | [UI] KVKK maskeleme raporu → admin paneline ek sekme | utku | P2 | review | web_dashboard/tabs/admin_panel.py, web_app.py |
| DOC-VISIBILITY-KATMANI-29 | [DOC] Kullanıcı dokümanı (görünürlük katmanı + kontör) → markdown guide | utku | P2 | review | docs/VISIBILITY_LAYER_GUIDE.md |
| API-LAYER2-DINAMIK-YÜKLEME-30 | [API] Layer 2 dinamik yükleme → plan_field_group tablosundan görünürlük oku | yasu | P1 | bekliyor | src/company_master/api/core/normalize.py, web_app.py |
| KONTROL-KVKK-MASKELEME-31 | [KONTROL] KVKK maskeleme end-to-end test → admin panel e2e | yasu | P1 | baslatdi | tests/test_visibility_layer.py, web_app.py |
| UI-KONTROL-PANOSU-32 | [UI] Admin kontrol panosu → maskeleme durum metriksleri | utku | P2 | review | web_dashboard/tabs/admin_panel.py, web_app.py |
| DOKÜMAN-KVKK-FAQ-33 | [DOC] KVKK FAQ & sorun çözme → markdown troubleshooting guide | utku | P2 | bekliyor | docs/KVKK_FAQ.md |

## Tamamlananlar

| Görev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| VERI-ADMIN-AKTIVITE-LOG-13 | [VERI] Kullanıcı aktivite log tablosunu yaz → migration 0017 (2s) | utku | 2026-09-24T19:25:07 |
| API-ADMIN-AKTIVITE-YAZ-14 | [API] Giriş/arama/AI olaylarını log'a yaz → web_app.py + arama uçları (2s) | utku | 2026-09-24T20:56:00 |
| DOC-ADMIN-DURUM-SENKRON-15 | [DOC] Bayat durum satırlarını düzelt → §8.4/§10 kanıtlı (1s) | orkestrator | 2026-09-24T20:56:00 |
| API-ADMIN-CHURN-3SINYAL-16 | [API] Churn kuralını 3 sinyalli hâlde yaz → churn.py tam formül (2s) | utku | 2026-09-24T20:56:00 |
| UI-ADMIN-DAU-17 | [UI] Gerçek DAU kartını yaz → admin_kpi.py aktivite sorgusu (2s) | utku | 2026-09-24T19:25:07 |
| API-ADMIN-KAYNAK-SAGLIK-18 | [API] Kaynak sağlık skorunu ölç → 3 kovalı rozet + DLQ birikme hızı (2s) | yasu | 2026-09-24T23:38:00 |
| UI-ADMIN-CRAWL-KONTROL-19 | [UI] Crawl tetikle/durdur aksiyonunu yaz → operatör kontrol paneli (3s) | yasu | 2026-09-24T23:38:00 |
| UI-ADMIN-ARAMA-BOSLUK-20 | [UI] Sonuçsuz arama frekans raporunu yaz → içerik boşluk raporu (2s) | utku | 2026-09-24T20:56:00 |
| API-ADMIN-SUPHELI-AKTIVITE-21 | [API] Şüpheli aktivite kurallarını yaz → 3 sinyalli güvenlik uyarısı (3s) | utku | 2026-09-24T20:56:00 |
| UI-ADMIN-UPSELL-22 | [UI] Upsell aday listesini yaz → satış aksiyon listesi (2s) | utku | 2026-09-24T20:56:00 |
| DOC-ADMIN-V9-KUTUCUK-24 | [DOC] V9 §16.5 kutucuklarını düzelt → 6 madde (1s) | utku | 2026-09-24T20:56:00 |
| TEST-BLOKE-FAKTOR-ARASTIRMA-01 | [TEST] Test hazirlik plani arastir → test_bloke_hazirlik.py (3s) | yasu | 2026-09-24T22:11:11.842076 |
| ALTYAPI-SECRETS-SETUP-01 | [ALTYAPI] Vault kurup .env template yaz → .env.example (2s) | orkestrator | 2026-09-24T20:56:00 |
| ALTYAPI-DB-MIGRATION-01 | [ALTYAPI] v0016 → v0017 prod migration planı yaz → db_migrate_prod.sh (1s) | orkestrator | 2026-09-24T20:56:00 |
| ALTYAPI-ADMIN-PANO-01 | [ALTYAPI] Task board 4 bolum yaz → render_task_board_tab.py (2s) | orkestrator | 2026-09-24T20:56:00 |
| ORKESTRA-AI-CHAT-KOORDINASYON-01 | [ORKESTRA] Ajan arasi protokol yaz → ajan_chat_koordinasyon.py (3s) | ihsan | 2026-09-24T22:02:28 |
