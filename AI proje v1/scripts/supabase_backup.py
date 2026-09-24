"""Supabase → yerel tam yedek betiği.

`pg_dump` ile veritabanının tamamını (şema + veri) bilgisayardaki
`backups/` klasörüne tarih damgalı, gzip sıkıştırmalı SQL dökümü olarak indirir.

Supabase hesabı kapansa bile bu dosyayla herhangi bir PostgreSQL'e
geri yükleme yapılabilir:

    gunzip -c backups/supabase_YYYYMMDD_HHMMSS.sql.gz | psql <hedef_url>

Gereksinimler:
    - PATH'te pg_dump (PostgreSQL istemci araçları)
    - Ortam değişkeni DATABASE_URL (.env'den de okunur)

Kullanım:
    python scripts/supabase_backup.py
"""

from __future__ import annotations

import gzip
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = PROJECT_ROOT / "backups"

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
    print("HATA: DATABASE_URL bulunamadı (ortam değişkeni veya .env).")
    sys.exit(1)


def main() -> int:
    pg_dump = find_pg_dump()
    if pg_dump is None:
        print("HATA: pg_dump bulunamadı. PostgreSQL istemci araçlarını kurun:")
        print("  winget install PostgreSQL.PostgreSQL.17")
        return 1

    database_url = load_database_url()
    BACKUP_DIR.mkdir(exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = BACKUP_DIR / f"supabase_{stamp}.sql.gz"

    proc = subprocess.run(
        [pg_dump, "--clean", "--if-exists", "--no-owner", "--no-privileges", database_url],
        capture_output=True,
    )

    if proc.returncode != 0:
        print(f"HATA: pg_dump başarısız:\n{proc.stderr.decode('utf-8', errors='replace')}")
        return 1

    with gzip.open(out_path, "wb") as f:
        f.write(proc.stdout)

    size_kb = out_path.stat().st_size / 1024
    print(f"Yedek alındı: {out_path} ({size_kb:.1f} KB)")

    yedekler = sorted(BACKUP_DIR.glob("supabase_*.sql.gz"))
    for eski in yedekler[:-30]:
        eski.unlink()
        print(f"Eski yedek silindi: {eski.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
