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
SCHEMA_VERSIONS_FILE = MIGRATIONS_DIR / "schema_versions.json"


# ============================================================
# Public API — migration dosyalari + cevrimici fonksiyonlar
# ============================================================

def get_db_url(env: str = "staging") -> str:
    """Ortama ait DATABASE_URL degerini dondurur.

    Oncelik sirasi:
      1) DATABASE_URL_{ENV}  (orn. DATABASE_URL_PROD)
      2) DATABASE_URL
      3) Bos string (cagiran taraf hata mesaji verir)
    """
    anahtar = f"DATABASE_URL_{(env or '').upper()}"
    return os.getenv(anahtar) or os.getenv("DATABASE_URL") or ""


def read_migration_file(version: str, direction: str = "up") -> str:
    """Migration SQL dosyasini oku.

    Args:
        version: Migration versiyonu, orn. "0017" veya "17".
        direction: "up" (varsayilan) veya "down".

    Returns:
        SQL dosyasinin icerigi.

    Raises:
        FileNotFoundError: Dosya bulunamazsa.
        ValueError: direction gecersizse.
    """
    if direction not in ("up", "down"):
        raise ValueError(f"direction 'up' veya 'down' olmali, verilen: {direction!r}")

    # "0017", "17", 17 -> "0017"
    ham = str(version).strip()
    sayi = int(ham) if ham.isdigit() else None
    if sayi is None:
        raise ValueError(f"Gecersiz migration versiyonu: {version!r}")

    # Tam eslesme (0017_user_activity_log.sql) ya da on ek (0017_*.sql)
    for kalip in (f"{sayi:04d}_*.sql", f"{sayi:04d}.sql"):
        adaylar = sorted(MIGRATIONS_DIR.glob(kalip))
        for aday in adaylar:
            is_down = aday.name.endswith(".down.sql")
            if (direction == "down") == is_down:
                return aday.read_text(encoding="utf-8")

    raise FileNotFoundError(
        f"Migration dosyasi bulunamadi: {version} ({direction}) "
        f"-> {MIGRATIONS_DIR}"
    )


def verify_table_exists(db_url: str, table_name: str) -> bool:
    """Veritabaninda tablonun var oldugunu dogrula (baglanti acmadan)."""
    if psycopg2 is None:
        print("[HATA] psycopg2 yuklu degil - tablo dogrulamasi yapilamaz")
        return False

    conn = None
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = %s
            )
            """,
            (table_name,),
        )
        return bool(cursor.fetchone()[0])
    except Exception as e:
        print(f"[HATA] Tablo dogrulama hatasi ({table_name}): {e}")
        return False
    finally:
        if conn is not None:
            conn.close()


def migrate(
    target_version: int,
    env: str = "staging",
    dry_run: bool = False,
    db_url: str | None = None,
) -> bool:
    """Hedef migration versiyonuna gecer.

    Args:
        target_version: Hedef versiyon (orn. 17).
        env: Ortam adi ("dev" | "staging" | "prod").
        dry_run: True ise SQL yazdirilir, uygulanmaz.
        db_url: Veritabani URL'si (verilmezse get_db_url(env) kullanilir).

    Returns:
        Basarili ise True, aksi halde False.
    """
    if dry_run:
        print(f"[DRY-RUN] {get_current_version_from_disk():04d} -> {target_version:04d}")
        for v in range(get_current_version_from_disk() + 1, target_version + 1):
            sql_up = read_migration_file(f"{v:04d}", "up")
            print(f"\n--- {v:04d} up ---\n{sql_up}")
        return True

    url = db_url or get_db_url(env)
    if not url:
        print(f"[HATA] {env} icin DATABASE_URL bulunamadi")
        return False

    manager = MigrationManager(env, dry_run=False)
    manager.connect()
    try:
        return manager.migrate_to_target(target_version)
    finally:
        manager.disconnect()


def get_current_version_from_disk() -> int:
    """En yuksek migration versiyonunu dosya adlarindan bul (DB'siz)."""
    if SCHEMA_VERSIONS_FILE.exists():
        try:
            veri = json.loads(SCHEMA_VERSIONS_FILE.read_text(encoding="utf-8"))
            if isinstance(veri, dict):
                mevcut = veri.get("current_version") or veri.get("current")
                if isinstance(mevcut, int):
                    return mevcut
        except (json.JSONDecodeError, OSError):
            pass

    en_yuksek = 0
    for aday in MIGRATIONS_DIR.glob("[0-9][0-9][0-9][0-9]_*.sql"):
        if aday.name.endswith(".down.sql"):
            continue
        sayi = int(aday.name[:4])
        en_yuksek = max(en_yuksek, sayi)
    return en_yuksek

# Import PostgreSQL client (or use psycopg2)
psycopg2 = None
sql = None
try:
    import psycopg2  # type: ignore[no-redefine]
    from psycopg2 import sql  # type: ignore[no-redef]
except ImportError:  # pragma: no cover - DB bagimliligi opsiyonel
    # Test/dry-run modunda psycopg2 olmadan da modul import edilebilir olmali.
    print("[UYARI] psycopg2 yüklü değil: pip install psycopg2-binary")


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
