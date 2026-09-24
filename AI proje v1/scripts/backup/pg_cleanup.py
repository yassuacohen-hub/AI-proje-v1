"""Eski yedekleri temizleme scripti.

scripts/backup/ altindaki yedekleri yas sinirina ve/veya maksimum dosya sayisina
gore temizler. Hem .dump hem de .sql.gz dosyalarini yonetir.

Kullanim:
    python scripts/backup/pg_cleanup.py --days 30 --keep 14

Parametreler:
    --days   X gunden eski yedekleri sil (varsayilan: 30)
    --keep   En fazla N yedek tut (varsayilan: 14)
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKUP_DIR = PROJECT_ROOT / "scripts" / "backup"


def get_backup_files() -> list[tuple[Path, datetime]]:
    files = []
    for pattern in ["pg_*.dump", "pg_*.sql.gz"]:
        for p in BACKUP_DIR.glob(pattern):
            try:
                mtime = datetime.fromtimestamp(p.stat().st_mtime)
                files.append((p, mtime))
            except OSError:
                continue
    files.sort(key=lambda x: x[1])
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Eski PostgreSQL yedeklerini temizle.")
    parser.add_argument("--days", type=int, default=30, help="Bu gunden eski yedekleri sil (varsayilan: 30)")
    parser.add_argument("--keep", type=int, default=14, help="En fazla bu kadar yedek tut (varsayilan: 14)")
    parser.add_argument("--dry-run", action="store_true", help="Silmeyi simule et, dosyalari koru")
    args = parser.parse_args()

    if not BACKUP_DIR.exists():
        print(f"UYARI: Yedek dizini bulunamadi: {BACKUP_DIR}")
        return 0

    files = get_backup_files()
    if not files:
        print("Temizlenecek yedek bulunamadi.")
        return 0

    now = datetime.now()
    cutoff = now - timedelta(days=args.days)

    to_delete: list[Path] = []

    for path, mtime in files:
        if mtime < cutoff:
            to_delete.append(path)

    if len(files) > args.keep:
        excess = len(files) - args.keep
        for path, _ in files[:excess]:
            if path not in to_delete:
                to_delete.append(path)

    to_delete = sorted(set(to_delete))

    if not to_delete:
        print("Temizlenecek yedek bulunamadi.")
        return 0

    print(f"Silinecek yedek sayisi: {len(to_delete)}")
    for path in to_delete:
        print(f"  - {path.name}")
        if not args.dry_run:
            path.unlink(missing_ok=True)

    if args.dry_run:
        print("\n(Dry-run modu: dosyalar silinmedi.)")
    else:
        print("\nTemizlik tamamlandi.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
