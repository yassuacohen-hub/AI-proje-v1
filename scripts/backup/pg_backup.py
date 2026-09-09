"""PostgreSQL otomatik yedekleme scripti.

DATABASE_URL ile baglanir, pg_dump ile veritabanini scripts/backup/ altina
tarih damgali olarak kaydeder. Hem custom format (.dump) hem de plain SQL
gzip (.sql.gz) ciktisi uretir.

Kullanım:
    python scripts/backup/pg_backup.py

Ciktilar:
    scripts/backup/pg_YYYYMMDD_HHMMSS.dump      (pg_restore ile geri yuklenir)
    scripts/backup/pg_YYYYMMDD_HHMMSS.sql.gz    (gunzip | psql ile geri yuklenir)
"""

from __future__ import annotations

import gzip
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKUP_DIR = PROJECT_ROOT / "scripts" / "backup"

PG_DUMP_FALLBACK = [
    r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe",
    r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
]


def find_pg_dump() -> str | None:
    path = shutil.which("pg_dump")
    if path:
        return path
    for p in PG_DUMP_FALLBACK:
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
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    print("HATA: DATABASE_URL bulunamadi (ortam degiskeni veya .env).")
    sys.exit(1)


def main() -> int:
    pg_dump = find_pg_dump()
    if pg_dump is None:
        print("HATA: pg_dump bulunamadi. PostgreSQL istemci araçlarini kurun:")
        print("  winget install PostgreSQL.PostgreSQL.17")
        return 1

    database_url = load_database_url()
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    base_name = f"pg_{stamp}"

    dump_path = BACKUP_DIR / f"{base_name}.dump"
    sql_path = BACKUP_DIR / f"{base_name}.sql.gz"

    print(f"Yedekleniyor: {database_url}")

    proc_custom = subprocess.run(
        [
            pg_dump,
            "-Fc",
            "--no-owner",
            "--no-privileges",
            "-f",
            str(dump_path),
            database_url,
        ],
        capture_output=True,
    )

    if proc_custom.returncode != 0:
        print(f"HATA: pg_dump (custom format) basarisiz:\n{proc_custom.stderr.decode('utf-8', errors='replace')}")
        return 1

    proc_plain = subprocess.run(
        [
            pg_dump,
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
            database_url,
        ],
        capture_output=True,
    )

    if proc_plain.returncode != 0:
        print(f"HATA: pg_dump (plain format) basarisiz:\n{proc_plain.stderr.decode('utf-8', errors='replace')}")
        dump_path.unlink(missing_ok=True)
        return 1

    with gzip.open(sql_path, "wb") as f:
        f.write(proc_plain.stdout)

    dump_size = dump_path.stat().st_size / 1024
    sql_size = sql_path.stat().st_size / 1024

    print(f"[OK] Custom format: {dump_path} ({dump_size:.1f} KB)")
    print(f"[OK] Plain format:  {sql_path} ({sql_size:.1f} KB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
