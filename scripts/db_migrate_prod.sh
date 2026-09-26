#!/bin/bash
# Prod DB Migration Runbook — v0016 → v0017
# Yazar: orkestrator
# Tarih: 2026-09-24
# Bağımlılık: ALTYAPI-SECRETS-SETUP-01 (prod secrets)

set -euo pipefail

# Konfigürasyon
# Prod DB URL: once ortam degiskeni (PROD_DATABASE_URL), sonra DATABASE_URL.
#   export PROD_DATABASE_URL="postgresql://user:pass@prod-host:5432/dbname"
# Guvenlik: URL asla loglanmaz; yalnizca sunucu adi gorunur.
PROD_DATABASE_URL="${PROD_DATABASE_URL:-${DATABASE_URL:-}}"
BACKUP_DIR="backups"
TIMESTAMP=$(date +%s)
BACKUP_FILE="${BACKUP_DIR}/prod_v0016_${TIMESTAMP}.sql.gz"
MIGRATION_LOG="logs/migration_${TIMESTAMP}.log"
ALERT_CHANNEL="ops-alerts"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${MIGRATION_LOG}"
}

error() {
    echo "[ERROR] $*" | tee -a "${MIGRATION_LOG}"
    exit 1
}

success() {
    echo "[OK] $*" | tee -a "${MIGRATION_LOG}"
}

warn() {
    echo "[WARN] $*" | tee -a "${MIGRATION_LOG}"
}

# Adım 1: Pre-flight checks
log "=== ADIM 1: Ön Kontroller ==="

if [ -z "${PROD_DATABASE_URL:-}" ]; then
    error "PROD_DATABASE_URL ortam değişkeni yok"
fi

# Baglanti sagligi (pg_isready) — migration oncesi zorunlu
if ! pg_isready -d "${PROD_DATABASE_URL}" -q; then
    error "PostgreSQL erisilebilir degil (pg_isready basarisiz)"
fi
success "pg_isready: PostgreSQL erisilebilir"

# Migration dosyalari mevcut mu
MIGRATION_UP="src/company_master/schema/migrations/0017_user_activity_log.sql"
MIGRATION_DOWN="src/company_master/schema/migrations/0017_user_activity_log.down.sql"
for f in "${MIGRATION_UP}" "${MIGRATION_DOWN}"; do
    [ -f "$f" ] || error "Migration dosyasi eksik: $f"
done
success "0017_user_activity_log up/down dosyalari mevcut"

success "Environment kontrol OK"

# Backup dizini oluştur
mkdir -p "${BACKUP_DIR}" "logs"
success "Dizinler hazır"

# Adım 2: Backup oluştur
log ""
log "=== ADIM 2: Prod Backup (v0016) ==="

if ! pg_dump --compress=9 --verbose \
    -d "${PROD_DATABASE_URL}" \
    -f "${BACKUP_FILE}" 2>&1 | tee -a "${MIGRATION_LOG}"; then
    error "Backup hatası"
fi

BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
success "Backup tamamlandı: ${BACKUP_FILE} (${BACKUP_SIZE})"

# Backup doğrulama
if ! gzip -t "${BACKUP_FILE}" 2>/dev/null; then
    error "Backup gzip doğrulaması başarısız"
fi
success "Backup integrity check geçti"

# Adım 3: Staging dry-run
log ""
log "=== ADIM 3: Staging Dry-Run (v0016 → v0017) ==="

if [ -z "${DATABASE_URL_STAGING:-}" ]; then
    warn "DATABASE_URL_STAGING yok, staging testi skip"
else
    if ! DATABASE_URL="${DATABASE_URL_STAGING}" python scripts/db_migrate.py \
        --env staging --target 0017 --dry-run >> "${MIGRATION_LOG}" 2>&1; then
        error "Staging dry-run başarısız"
    fi
    success "Staging dry-run OK"
fi

# Adım 4: Prod migration uygula
log ""
log "=== ADIM 4: Prod Migration Uygulanıyor (v0016 → v0017) ==="

MIGRATION_START=$(date +%s)

if ! DATABASE_URL="${PROD_DATABASE_URL}" python scripts/db_migrate.py \
    --env prod --target 0017 --verify >> "${MIGRATION_LOG}" 2>&1; then
    error "Prod migration başarısız"
fi

MIGRATION_END=$(date +%s)
MIGRATION_TIME=$((MIGRATION_END - MIGRATION_START))

success "Prod migration tamamlandı (${MIGRATION_TIME}s)"

# Adım 5: Post-migration doğrulama
log ""
log "=== ADIM 5: Post-Migration Doğrulama ==="

# Tablo mevcudiyeti
if ! psql "${PROD_DATABASE_URL}" -t -c "SELECT COUNT(*) FROM user_activity_log;" > /dev/null 2>&1; then
    error "user_activity_log tablosu doğrulama hatası"
fi
success "user_activity_log tablosu mevcuttur"

success "Post-migration doğrulama tamamlandı"

# Adım 6: Rollback planı belgesini oluştur
log ""
log "=== ADIM 6: Rollback Belgesi ==="

cat > "logs/rollback_${TIMESTAMP}.md" << EOF
# Rollback Plan — v0017 → v0016

## Graceful Rollback
\`\`\`bash
export PROD_DATABASE_URL="postgresql://..."
DATABASE_URL="\$PROD_DATABASE_URL" python scripts/db_migrate.py --env prod --target 0016
\`\`\`

## Emergency Restore (Backup'tan)
\`\`\`bash
gunzip -c backups/prod_v0016_${TIMESTAMP}.sql.gz | psql "\$PROD_DATABASE_URL"
\`\`\`
EOF
```
EOF

success "Rollback belgesi oluşturuldu"

log ""
log "=== Migration Başarılı ==="
log "  - Backup: ${BACKUP_FILE}"
log "  - Log: ${MIGRATION_LOG}"

exit 0
