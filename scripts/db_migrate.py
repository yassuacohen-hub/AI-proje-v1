#!/usr/bin/env python3
"""
Database Migration Manager — v0016/v0017 Prod Migration

Kullanım:
  python scripts/db_migrate.py --env staging --target 0017 --dry-run
  python scripts/db_migrate.py --env staging --target 0017
  python scripts/db_migrate.py --env staging --target 0016
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
import json

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "src" / "company_master" / "schema" / "migrations"

# Import PostgreSQL client (or use psycopg2)
try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("[HATA] psycopg2 yüklü değil: pip install psycopg2-binary")
    sys.exit(1)


class MigrationManager:
    """Migration manager — up/down cycle."""

    def __init__(self, env: str, dry_run: bool = False):
        self.env = env
        self.dry_run = dry_run
        self.conn = None
        self.migration_history = []

    def connect(self) -> None:
        """Veritabanına bağlan."""
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("[HATA] DATABASE_URL ortam değişkeni yok")
            sys.exit(1)

        try:
            self.conn = psycopg2.connect(db_url)
            self.conn.autocommit = False
            print(f"[✓] Bağlantı başarılı ({self.env})")
        except Exception as e:
            print(f"[HATA] Bağlantı hatası: {e}")
            sys.exit(1)

    def disconnect(self) -> None:
        """Bağlantıyı kapat."""
        if self.conn:
            self.conn.close()

    def get_current_version(self) -> int:
        """Mevcut migration versiyonu oku."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT MAX(version) FROM _schema_version WHERE applied = TRUE"
            )
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except psycopg2.Error:
            # Schema version tablosu yoksa 0
            return 0
        finally:
            cursor.close()

    def ensure_schema_version_table(self) -> None:
        """_schema_version tablosu oluştur (varsa skip)."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS _schema_version (
                    version BIGINT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    applied BOOLEAN DEFAULT FALSE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    execution_time_ms BIGINT
                )
            """)
            self.conn.commit()
            print("[✓] _schema_version tablosu hazır")
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"[HATA] _schema_version oluşturma hatası: {e}")
        finally:
            cursor.close()

    def apply_migration(self, version: int, direction: str = "up") -> bool:
        """Single migration uygula (up/down)."""
        if direction == "up":
            migration_file = MIGRATIONS_DIR / f"{version:04d}_*.sql"
            # Dosyayı bul (tam ad pattern)
            import glob
            files = list(MIGRATIONS_DIR.glob(f"{version:04d}_*.sql"))
            files = [f for f in files if ".down" not in f.name]
            if not files:
                print(f"[HATA] Migration {version:04d} bulunamadı (up)")
                return False
            migration_file = files[0]
        else:
            migration_file = MIGRATIONS_DIR / "down" / f"{version:04d}_*.sql"
            import glob
            files = list((MIGRATIONS_DIR / "down").glob(f"{version:04d}_*.sql"))
            if not files:
                print(f"[UYARI] Rollback {version:04d} bulunamadı, skip")
                return True
            migration_file = files[0]

        try:
            sql_content = migration_file.read_text(encoding="utf-8")

            if self.dry_run:
                print(f"[DRY-RUN] {direction.upper()} {version:04d}: {migration_file.name}")
                print(f"  SQL Preview: {sql_content[:100]}...")
                return True

            cursor = self.conn.cursor()
            cursor.execute(sql_content)

            # İstatistik kaydet
            cursor.execute("""
                INSERT INTO _schema_version (version, name, applied, execution_time_ms)
                VALUES (%s, %s, %s, 0)
                ON CONFLICT (version) DO UPDATE
                SET applied = %s, applied_at = CURRENT_TIMESTAMP
            """, (version, migration_file.name, direction == "up", direction == "up"))

            self.conn.commit()
            print(f"[✓] {direction.upper()} {version:04d} başarılı")
            return True

        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"[HATA] Migration {version:04d} ({direction}) hatası: {e}")
            return False
        finally:
            cursor.close()

    def migrate_to_target(self, target_version: int) -> bool:
        """Target versiyona geç (up or down)."""
        self.ensure_schema_version_table()
        current_version = self.get_current_version()

        print(f"[Durum] Mevcut: {current_version:04d}, Hedef: {target_version:04d}")

        if current_version == target_version:
            print("[✓] Zaten hedef versiyonda")
            return True

        if current_version < target_version:
            # Up migration
            for v in range(current_version + 1, target_version + 1):
                if not self.apply_migration(v, "up"):
                    return False
        else:
            # Down migration (rollback)
            for v in range(current_version, target_version, -1):
                if not self.apply_migration(v, "down"):
                    return False

        print(f"[✓] Migration tamamlandı: {current_version:04d} → {target_version:04d}")
        return True


def verify_user_activity_log_table() -> bool:
    """user_activity_log tablosu doğrula (post-migration check)."""
    db_url = os.getenv("DATABASE_URL")
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Tablo mevcudiyeti kontrol et
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'user_activity_log'
            )
        """)
        exists = cursor.fetchone()[0]

        # Şema doğrula (varsa)
        if exists:
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'user_activity_log'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print("[✓] user_activity_log şeması:")
            for col_name, col_type in columns:
                print(f"    - {col_name}: {col_type}")

        cursor.close()
        conn.close()

        return exists
    except Exception as e:
        print(f"[HATA] Doğrulama hatası: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="DB Migration Manager")
    parser.add_argument("--env", choices=["dev", "staging", "prod"], default="staging",
                        help="Hedef ortam")
    parser.add_argument("--target", type=lambda x: int(x) if x.isdigit() else x,
                        default=17, help="Hedef migration versiyonu (int, örnek: 17)")
    parser.add_argument("--dry-run", action="store_true", help="Sadece simülasyon (apply yok)")
    parser.add_argument("--verify", action="store_true", help="Sonrası doğrulama")

    args = parser.parse_args()

    print(f"[Başlat] DB Migration Manager")
    print(f"  Ortam: {args.env}")
    print(f"  Hedef: {args.target:04d}")
    print(f"  Dry-run: {args.dry_run}")
    print()

    # Migration yapıcı oluştur
    manager = MigrationManager(args.env, args.dry_run)

    if not args.dry_run:
        manager.connect()

    # Migration uygula
    success = manager.migrate_to_target(args.target)

    # Doğrulama
    if success and args.verify and not args.dry_run:
        print("\n[Doğrulama] user_activity_log şeması...")
        if verify_user_activity_log_table():
            print("[✓] Şema doğrulaması geçti")
        else:
            print("[UYARI] Şema doğrulaması kontrol yapın")

    if not args.dry_run:
        manager.disconnect()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
