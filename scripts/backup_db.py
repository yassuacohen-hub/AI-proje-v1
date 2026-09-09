# -*- coding: utf-8 -*-
"""P4-6: Veritabani yedekleme otomasyonu.

pg_dump gerektirmez; SQLAlchemy ile tum tablolari CSV olarak export eder
ve backups/ altina zip'ler. SQLite ve PostgreSQL uyumlu.

Kullanim:
    python scripts/backup_db.py                 # yedek al
    python scripts/backup_db.py --list          # mevcut yedekleri listele
    python scripts/backup_db.py --keep 5        # son 5 yedek birak (retention)
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import inspect, text

from company_master.db.connection import get_database_url, get_engine

BACKUP_DIR = ROOT / "backups"


def _mask_url(url: str) -> str:
    """Sifreleri maskeleyerek URL'yi loglamaya uygun hale getirir."""
    if "@" in url and "://" in url:
        try:
            prefix, rest = url.split("://", 1)
            cred, host = rest.rsplit("@", 1)
            user = cred.split(":", 1)[0]
            return f"{prefix}://{user}:****@{host}"
        except Exception:
            pass
    return url


def list_backups() -> list[dict]:
    BACKUP_DIR.mkdir(exist_ok=True)
    items = []
    for z in sorted(BACKUP_DIR.glob("backup_*.zip"), reverse=True):
        try:
            with zipfile.ZipFile(z) as zf:
                names = zf.namelist()
                manifest = {}
                if "manifest.json" in names:
                    manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
                items.append({
                    "file": z.name,
                    "size_mb": round(z.stat().st_size / 1024 / 1024, 2),
                    "created": manifest.get("created", "-"),
                    "db": manifest.get("database", "-"),
                    "tables": manifest.get("table_counts", {}),
                })
        except Exception as e:
            items.append({"file": z.name, "error": str(e)})
    return items


def create_backup(keep: int | None = None) -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    engine = get_engine()
    insp = inspect(engine)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = BACKUP_DIR / f"backup_{stamp}.zip"

    manifest = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "database": _mask_url(get_database_url()),
        "tables": [],
        "table_counts": {},
    }

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf, engine.connect() as conn:
        for tname in sorted(insp.get_table_names()):
            if tname.startswith("_"):
                continue  # alembic vb. sistem tablolari
            try:
                cols = insp.get_columns(tname)
            except Exception as e:
                print(f"  ! {tname}: kolonlar okunamadi ({e}), atlandi")
                continue
            col_names = [c["name"] for c in cols]
            manifest["tables"].append({
                "name": tname,
                "columns": [
                    {"name": c["name"], "type": str(c["type"]), "nullable": c.get("nullable", True)}
                    for c in cols
                ],
            })
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(col_names)
            count = 0
            result = conn.execute(text(f'SELECT * FROM "{tname}"'))
            for row in result:
                writer.writerow(["" if v is None else str(v) for v in row])
                count += 1
            zf.writestr(f"data/{tname}.csv", buf.getvalue())
            manifest["table_counts"][tname] = count
            print(f"  + {tname}: {count} satir")

        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"\nYedek alindi: {zip_path.name} ({size_mb:.2f} MB)")
    print(f"Toplam tablo: {len(manifest['tables'])}, Toplam satir: {sum(manifest['table_counts'].values())}")

    if keep is not None and keep > 0:
        removed = apply_retention(keep)
        if removed:
            print(f"Retention: {removed} eski yedek silindi (son {keep} birakildi)")

    return zip_path


def apply_retention(keep: int) -> int:
    zips = sorted(BACKUP_DIR.glob("backup_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    removed = 0
    for old in zips[keep:]:
        old.unlink()
        removed += 1
    return removed


def main() -> None:
    ap = argparse.ArgumentParser(description="DB yedekleme (pg_dump gerektirmez)")
    ap.add_argument("--list", action="store_true", help="Mevcut yedekleri listele")
    ap.add_argument("--keep", type=int, default=None, help="Retention: son N yedegi birak")
    args = ap.parse_args()

    if args.list:
        for item in list_backups():
            print(json.dumps(item, ensure_ascii=False))
        return

    create_backup(keep=args.keep)


if __name__ == "__main__":
    main()
