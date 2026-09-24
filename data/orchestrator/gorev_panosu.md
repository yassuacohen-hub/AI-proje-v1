# Gorev Panosu — Orkestrator

> Merkezi gorev listesi: herkes herkesin ne yaptigini takip eder.
> Kaynak: `data/orchestrator/task_board.json` — Obsidian okumasi icin disa aktarilir.

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum | Dosyalar |
|-------|--------|-------|---------|-------|----------|
| ALTYAPI-D66-BYPASS-TETIKLEME | [ALTYAPI] D-65 Is Durmaz Bypass Tetikleme -> pano_duzenleme (2s) | ihsan | P1 | iptal | scripts/pano_denetim.py, scripts/tetik_senk.py, tests/test_d66_bypass_tetikleme.py |
| API-ADMIN-AKTIVITE-YAZ-14 | [API] Giriş/arama/AI olaylarını log'a yaz → web_app.py + arama uçları (2s) | utku | P0 | review | web_app.py |
| DOC-ADMIN-DURUM-SENKRON-15 | [DOC] Bayat durum satırlarını düzelt → §8.4/§10 kanıtlı (1s) | orkestrator | P1 | review | AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md |
| API-ADMIN-CHURN-3SINYAL-16 | [API] Churn kuralını 3 sinyalli hâlde yaz → churn.py tam formül (2s) | utku | P1 | review | src/company_master/churn.py |
| API-ADMIN-KAYNAK-SAGLIK-18 | [API] Kaynak sağlık skorunu ölç → 3 kovalı rozet + DLQ birikme hızı (2s) | yasu | P1 | aktif | src/company_master/kaynak_guvenilirlik.py |
| UI-ADMIN-CRAWL-KONTROL-19 | [UI] Crawl tetikle/durdur aksiyonunu yaz → operatör kontrol paneli (3s) | yasu | P1 | aktif | web_dashboard/tabs/webhook_monitor.py |
| UI-ADMIN-ARAMA-BOSLUK-20 | [UI] Sonuçsuz arama frekans raporunu yaz → içerik boşluk raporu (2s) | utku | P2 | review | web_dashboard/tabs/admin_quality.py |
| API-ADMIN-SUPHELI-AKTIVITE-21 | [API] Şüpheli aktivite kurallarını yaz → 3 sinyalli güvenlik uyarısı (3s) | utku | P2 | review | src/company_master/admin_audit.py |
| UI-ADMIN-UPSELL-22 | [UI] Upsell aday listesini yaz → satış aksiyon listesi (2s) | utku | P2 | review | web_dashboard/tabs/musteri_yonetimi.py |
| TEST-ADMIN-K2-AGIRLIK-23 | [TEST] K2 ağırlık şemasını denetle → test + SSOT kanıt (1s) | yasu | P2 | aktif | - |
| DOC-ADMIN-V9-KUTUCUK-24 | [DOC] V9 §16.5 kutucuklarını düzelt → 6 madde (1s) | utku | P2 | review | - |
| UI-ADMIN-FEATURE-FLAG-25 | [UI] Feature flag yönetim ekranını yaz → A5 MVP (3s) | utku | P2 | yedek | - |
| API-ADMIN-MFA-26 | [API] MFA + hesap kilidi akışını yaz → A6 auth (4s) | utku | P2 | yedek | - |
| UI-ADMIN-LTV-CAC-27 | [UI] LTV/CAC kartlarını yaz → K8 tamamlama (2s) | utku | P2 | yedek | - |
| DOC-ADMIN-MULTITENANT-KARAR-28 | [DOC] Multi-tenant kararını belgele → KK-7 (1s) | utku | P2 | yedek | - |
| ALTYAPI-SECRETS-SETUP-01 | [ALTYAPI] Vault kurup .env template yaz → .env.example (2s) | orkestrator | P0 | aktif | .env.example, .env.vault, scripts/rotate_secrets.py |
| ALTYAPI-DB-MIGRATION-01 | [ALTYAPI] v0016 → v0017 prod migration planı yaz → db_migrate_prod.sh (1s) | orkestrator | P1 | aktif | scripts/db_migrate.py, src/company_master/schema/migrations/0017_user_activity_log.sql, scripts/db_migrate_prod.sh |
| ALTYAPI-ADMIN-PANO-01 | [ALTYAPI] Task board 4 bolum yaz → render_task_board_tab.py (2s) | orkestrator | P2 | aktif | web_dashboard/tabs/admin_panel.py, tests/test_admin_pano_board_view.py, docs/ADMIN_PANO_BOARD_VIEW.md |

## Tamamlananlar

| Görev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| VERI-ADMIN-AKTIVITE-LOG-13 | [VERI] Kullanıcı aktivite log tablosunu yaz → migration 0017 (2s) | utku | 2026-09-24T19:25:07 |
| UI-ADMIN-DAU-17 | [UI] Gerçek DAU kartını yaz → admin_kpi.py aktivite sorgusu (2s) | utku | 2026-09-24T19:25:07 |
| TEST-BLOKE-FAKTOR-ARASTIRMA-01 | [TEST] Test hazirlik plani arastir → test_bloke_hazirlik.py (3s) | yasu | 2026-09-24T22:11:11.842076 |
| ORKESTRA-AI-CHAT-KOORDINASYON-01 | [ORKESTRA] Ajan arasi protokol yaz → ajan_chat_koordinasyon.py (3s) | ihsan | 2026-09-24T22:02:28 |
