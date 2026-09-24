# -*- coding: utf-8 -*-
"""P4-6: Yedekten geri yukleme (backup_db.py ile uyumlu).

Kullanim:
    python scripts/restore_db.py backups/backup_YYYYMMDD_HHMMSS.zip --dry-run
    python scripts/restore_db.py backups/backup_YYYYMMDD_HHMMSS.zip            # eksik tablolari kurar
    python scripts/restore_db.py backups/backup_YYYYMMDD_HHMMSS.zip --drop     # tablolari dusurup kurar (YIKICI!)
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text

from company_master.db.connection import get_engine


def _sql_type(type_str: str, is_sqlite: bool) -> str:
    t = type_str.upper()
    if is_sqlite:
        if "INT" in t:
            return "INTEGER"
        if "NUMERIC" in t or "DECIMAL" in t or "REAL" in t or "FLOAT" in t or "DOUBLE" in t:
            return "REAL"
        return "TEXT"
    if "BIGINT" in t:
        return "BIGINT"
    if "INTEGER" in t or "INT" in t:
        return "INTEGER"
    if "BOOLEAN" in t:
        return "BOOLEAN"
    if "TIMESTAMP" in t or "DATE" in t:
        return t if "TIMEZONE" in t or "TIMESTAMP" in t else "TIMESTAMP"
    if "NUMERIC" in t or "DECIMAL" in t:
        return "NUMERIC"
    if "REAL" in t or "FLOAT" in t or "DOUBLE" in t:
        return "DOUBLE PRECISION"
    if "JSON" in t:
        return "JSONB" if "JSONB" in t else "JSON"
    if "UUID" in t:
        return "UUID"
    return "TEXT"


def _json_fix(val: str | None) -> object:
    """CSV'den gelen JSON/JSONB kolon degerini PostgreSQL'e uygun hale getirir.

    SQLite doneminde TEXT olarak yazilan Python-repr ('{'a': 1}') degerler
    PostgreSQL JSON parser'ini cokertir; dict/list formatina cevrilemeyen
    degerler NULL olur.
    """
    if val is None:
        return None
    s = val.strip()
    if not (s.startswith("{") or s.startswith("[")):
        return None
    try:
        return json.loads(s)
    except Exception:
        try:
            return json.loads(s.replace("'", '"'))
        except Exception:
            return None


try:  # psycopg3 varsa dict/list'i dogrudan JSONB'ye adap eder
    from psycopg.types.json import Json as _PgJson
except Exception:
    _PgJson = None


def _json_param(val: object) -> object:
    """JSON kolonuna gidecek degeri dbapi-uyumlu hale getirir."""
    if isinstance(val, (dict, list)):
        if _PgJson is not None:
            return _PgJson(val)
        return json.dumps(val, ensure_ascii=False)
    return val


def restore(zip_path: Path, drop: bool = False, dry_run: bool = False) -> None:
    engine = get_engine()
    is_sqlite = engine.dialect.name == "sqlite"
    url = str(engine.url)
    masked = url.split("@")[-1] if "@" in url else url

    with zipfile.ZipFile(zip_path) as zf:
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
        print(f"Yedek: {zip_path.name}")
        print(f"Alindigi tarih: {manifest.get('created')}")
        print(f"Kaynak DB: {manifest.get('database')}")
        counts = manifest.get("table_counts", {})
        total = sum(counts.values())
        print(f"Tablo sayisi: {len(manifest['tables'])}, toplam satir: {total}")
        if dry_run:
            print("\n[DRY-RUN] Hicbir degisiklik yapilmadi. Tablolar:")
            for t in manifest["tables"]:
                print(f"  - {t['name']}: {counts.get(t['name'], 0)} satir")
            return

        existing = set()
        from sqlalchemy import inspect
        with engine.connect() as conn:
            existing = set(inspect(conn).get_table_names())

        with engine.begin() as conn:
            for t in manifest["tables"]:
                tname = t["name"]
                cols = t["columns"]
                if tname in existing and drop:
                    print(f"  - {tname} dusuruluyor (--drop)")
                    conn.execute(text(f'DROP TABLE IF EXISTS "{tname}" CASCADE' if not is_sqlite
                                      else f'DROP TABLE IF EXISTS "{tname}"'))
                    existing.discard(tname)
                if tname not in existing:
                    col_defs = ", ".join(
                        f'"{c["name"]}" {_sql_type(c["type"], is_sqlite)}'
                        + ("" if c.get("nullable", True) else " NOT NULL")
                        for c in cols
                    )
                    conn.execute(text(f'CREATE TABLE "{tname}" ({col_defs})'))
                    print(f"  + {tname} tablosu olusturuldu")

            for t in manifest["tables"]:
                tname = t["name"]
                col_names = [c["name"] for c in t["columns"]]
                col_types = {c["name"]: (c.get("type") or "").upper() for c in t["columns"]}
                reader = csv.DictReader(io.StringIO(zf.read(f"data/{tname}.csv").decode("utf-8")))
                n = 0
                batch = []
                quoted_cols = ", ".join(f'"{c}"' for c in col_names)
                placeholders = ", ".join(f":c{i}" for i in range(len(col_names)))
                insert_sql = text(f'INSERT INTO "{tname}" ({quoted_cols}) VALUES ({placeholders})')
                for row in reader:
                    params = {}
                    for i, c in enumerate(col_names):
                        raw = row.get(c) or None
                        if "JSON" in col_types.get(c, ""):
                            raw = _json_param(_json_fix(raw))
                        params[f"c{i}"] = raw
                    batch.append(params)
                    n += 1
                    if len(batch) >= 500:
                        conn.execute(insert_sql, batch)
                        batch = []
                if batch:
                    conn.execute(insert_sql, batch)
                print(f"  + {tname}: {n} satir yuklendi")

    print(f"\nGeri yukleme tamamlandi -> {masked}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Yedekten geri yukleme")
    ap.add_argument("zip", type=Path, help="backup_*.zip dosyasi")
    ap.add_argument("--drop", action="store_true", help="Var olan tablolari dusurup yeniden kur (YIKICI)")
    ap.add_argument("--dry-run", action="store_true", help="Icerigi goster, degisiklik yapma")
    args = ap.parse_args()

    if not args.zip.exists():
        print(f"HATA: {args.zip} bulunamadi")
        sys.exit(1)

    restore(args.zip, drop=args.drop, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
