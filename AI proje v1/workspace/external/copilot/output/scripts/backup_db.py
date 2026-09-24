"""PostgreSQL yedekleme betiği.

`pg_dump` ile veritabanını custom format (-Fc) ile yedekler.
Rotasyon: 7 günlük, 4 haftalık, 6 aylık yedek korur.

Gereksinimler:
    - PATH'te pg_dump (PostgreSQL istemci araçları)
    - Ortam değişkeni DATABASE_URL (.env'den de okunur)

Kullanım:
    python scripts/backup_db.py
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = PROJECT_ROOT / "backups"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "backup_db.log"

PG_DUMP_FALLBACK = [
    r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe",
    r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
    r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
]

RETENTION_DAILY = 7
RETENTION_WEEKLY = 4
RETENTION_MONTHLY = 6

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


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
    logger.error("DATABASE_URL bulunamadı (ortam değişkeni veya .env).")
    sys.exit(1)


def rotate_backups() -> None:
    now = datetime.now()
    backups = sorted(BACKUP_DIR.glob("backup_*.dump"))

    keep = set()
    for period, days in [
        ("daily", RETENTION_DAILY),
        ("weekly", RETENTION_DAILY * 7 * RETENTION_WEEKLY),
        ("monthly", RETENTION_DAILY * 7 * 4 * RETENTION_MONTHLY),
    ]:
        candidates = [b for b in backups if (now - datetime.fromtimestamp(b.stat().st_mtime)).days <= days]
        if candidates:
            keep.add(max(candidates, key=lambda p: p.stat().st_mtime))

    for b in backups:
        if b not in keep:
            try:
                b.unlink()
                logger.info("Eski yedek silindi: %s", b.name)
            except OSError as exc:
                logger.error("Silme hatası %s: %s", b.name, exc)


def main() -> int:
    pg_dump = find_pg_dump()
    if pg_dump is None:
        logger.error("pg_dump bulunamadı. PostgreSQL istemci araçlarını kurun.")
        logger.error("  winget install PostgreSQL.PostgreSQL.17")
        return 1

    database_url = load_database_url()
    BACKUP_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = BACKUP_DIR / f"backup_{stamp}.dump"

    logger.info("Yedekleme başlıyor: %s", out_path.name)

    proc = subprocess.run(
        [pg_dump, "-Fc", "--no-owner", "--no-privileges", database_url],
        capture_output=True,
    )

    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace")
        logger.error("pg_dump başarısız:\n%s", stderr)
        return 1

    try:
        out_path.write_bytes(proc.stdout)
    except OSError as exc:
        logger.error("Yedek dosyası yazılamadı: %s", exc)
        return 1

    size_kb = out_path.stat().st_size / 1024
    logger.info("Yedek alındı: %s (%.1f KB)", out_path.name, size_kb)

    rotate_backups()

    return 0


if __name__ == "__main__":
    sys.exit(main())
