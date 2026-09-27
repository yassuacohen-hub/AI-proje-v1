# ALTYAPI-DB-MIGRATION-01 — v0016/v0017 Prod Migration Planı

**Ajan:** Utku  
**Aciliyet:** P1 (Sunucu geçişi, SECRETS sonrası)  
**Süre:** 1 saat  
**Tür:** Altyapı (DB migration)  
**Kilitli dosya:** `scripts/db_migrate.py`  
**Bağımlılık:** ALTYAPI-SECRETS-SETUP-01  
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md`

## Neden
VERI-ADMIN-AKTIVITE-LOG-13 (done, onaylandı) migration 0017 `user_activity_log` tablosunu oluşturdu. Prod'a uygulamadan önce staging'de test + rollback doğrulaması şart. Risk sırası: P0-SECRETS (2s) > P1-DB (1s) > P2-DNS (otomatik).

## Doğrulanacak varsayım
- v0016: Mevcut prod schema snapshot
- v0017: `src/company_master/schema/migrations/0017_user_activity_log.sql` dosyası mevcut
- Tablo sema: BIGSERIAL PK, UUID FK, CHECK (olay_tipi), INET/CHAR kolonları NULL gecebilir, iki indeks
- Down (rollback) scripti v0017 dosyasında tanımlı
- Test: 12/12 geçti (VERI-ADMIN-AKTIVITE-LOG-13 teslimi)
- Staging ortamı erişilebilir ve prod schema ile birebir aynı

## Adımlar
1. Migration dosyalarını kontrol et (v0016 ↔ v0017)
2. Staging test (dry-run + apply):
   - `python scripts/db_migrate.py --env staging --target 0017 --dry-run`
   - `python scripts/db_migrate.py --env staging --target 0017`
   - Doğrula: `SELECT COUNT(*) FROM user_activity_log;` → 0 (boş ok)
   - Doğrula: `SELECT * FROM pg_tables WHERE tablename='user_activity_log';` → exists
3. Rollback test:
   - `python scripts/db_migrate.py --env staging --target 0016 --dry-run`
   - `python scripts/db_migrate.py --env staging --target 0016`
   - Doğrula: `SELECT * FROM pg_tables WHERE tablename='user_activity_log';` → not exists
4. Prod migration runbook yaz: `scripts/db_migrate_prod.sh` + adım adım doküman
5. Monitoring config: AlertManager rules (replication lag > 5s = page)
6. Backup script: `pg_dump --env prod --file=backups/prod_v0016_$(date +%s).sql.gz`

## Kabul kriteri
- [ ] Migration script validation (v0016 ↔ v0017) tamam
- [ ] Staging test raporu (200 satır: dry-run output + verify queries + rollback confirmation)
- [ ] Prod migration runbook (`scripts/db_migrate_prod.sh` + step-by-step doc)
- [ ] Monitoring config (AlertManager rules: replication lag > 5s = page)
- [ ] Backup script hazır

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** yukarıdaki `**Hub:**` dosyasının "Kapanan işler" bölümüne `<TASK_ID>` satırı yaz (B-14 kapısı).
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id ALTYAPI-DB-MIGRATION-01 --ozet "<özet>"`

## Ilgili Nodlar
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
- [[hubs/ADMIN_DASHBOARD_HUB]]