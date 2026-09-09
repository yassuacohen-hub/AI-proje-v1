"""PostgreSQL geri yukleme scripti.

scripts/backup/ altindaki yedekleri hedef veritabanina geri yukler.
Hem custom format (.dump) hem de plain SQL (.sql.gz) desteklenir.

Kullanim:
    python scripts/backup/pg_restore.py <yedek_dosyasi>

Ornek:
    python scripts/backup/pg_restore.py scripts/backup/pg_20260101_000000.dump
    python scripts/backup/pg_restore.py scripts/backup/pg_20260101_000000.sql.gz

Varsayilan olarak DATABASE_URL hedef olarak kullanilir. Farkli bir hedef
icin ortam degiskeni ile belirtilebilir:
    DATABASE_URL=postgresql://... python scripts/backup/pg_restore.py <dosya>
"""

from __future__ import annotations

import argparse
import gzip
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PG_RESTORE_FALLBACK = [
    r"C:\Program Files\PostgreSQL\17\bin\pg_restore.exe",
    r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe",
]


def find_pg_restore() -> str | None:
    path = shutil.which("pg_restore")
    if path:
        return path
    for p in PG_RESTORE_FALLBACK:
        if Path(p).exists():
            return p
    return None


def load_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DATABASE_URL="):
                return line.split("=", 1)[1].strip().strip('"').strip("\'")
    print("HATA: DATABASE_URL bulunamadi (ortam degiskeni veya .env).")
    sys.exit(1)


def restore_custom(backup_path: Path, database_url: str, pg_restore: str) -> int:
    print(f"Geri yukleniyor (custom): {backup_path.name}")
    proc = subprocess.run(
        [
            pg_restore,
            "--no-owner",
            "--no-privileges",
            "-d",
            database_url,
            str(backup_path),
        ],
        capture_output=True,
    )
    if proc.returncode != 0:
        print(f"HATA: pg_restore basarisiz:\n{proc.stderr.decode('utf-8', errors='replace')}")
        return 1
    print("[OK] Geri yukleme tamamlandi (custom).")
    return 0


def restore_plain(backup_path: Path, database_url: str) -> int:
    print(f"Geri yukleniyor (plain): {backup_path.name}")
    with gzip.open(backup_path, "rb") as f:
        sql_data = f.read()

    psql = shutil.which("psql")
    if not psql:
        psql = r"C:\Program Files\PostgreSQL\17\bin\psql.exe"
        if not Path(psql).exists():
            psql = r"C:\Program Files\PostgreSQL\16\bin\psql.exe"

    if not Path(psql).exists():
        print("HATA: psql bulunamadi. PostgreSQL istemci araçlarini kurun.")
        return 1

    proc = subprocess.run(
        [psql, database_url],
        input=sql_data,
        capture_output=True,
    )
    if proc.returncode != 0:
        print(f"HATA: psql basarisiz:\n{proc.stderr.decode('utf-8', errors='replace')}")
        return 1
    print("[OK] Geri yukleme tamamlandi (plain).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="PostgreSQL geri yukleme aracı.")
    parser.add_argument("backup_file", type=Path, help="Yedek dosyasi (.dump veya .sql.gz)")
    args = parser.parse_args()
    backup_path = args.backup_file

    if not backup_path.exists():
        print(f"HATA: Dosya bulunamadi: {backup_path}")
        return 1

    database_url = load_database_url()

    if backup_path.suffix == ".dump":
        pg_restore = find_pg_restore()
        if pg_restore is None:
            print("HATA: pg_restore bulunamadi. PostgreSQL istemci araçlarini kurun.")
            return 1
        return restore_custom(backup_path, database_url, pg_restore)
    elif backup_path.suffix == ".gz":
        return restore_plain(backup_path, database_url)
    else:
        print("HATA: Desteklenmeyen dosya uzantisi. .dump veya .sql.gz kullanin.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
