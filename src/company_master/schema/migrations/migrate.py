# -*- coding: utf-8 -*-
"""Schema migration runner (BE-02).

Kullanim:
    python -m src.company_master.schema.migrations.migrate [--dry-run] [--version]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

MIGRATIONS_DIR = Path(__file__).resolve().parent
VERSIONS_FILE = MIGRATIONS_DIR / "schema_versions.json"


def load_versions() -> dict[str, Any]:
    with open(VERSIONS_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_current_version() -> int:
    return load_versions().get("current_version", 0)


def list_migrations() -> list[dict[str, Any]]:
    return load_versions().get("migrations", [])


def needs_migration(target: int = 15) -> bool:
    return get_current_version() < target


def run_migrations(target: int = 15, dry_run: bool = False) -> list[str]:
    """Migration defterini isaretler. SQL calistirmaz -> `apply_sql` kullanin.

    MIGRATE-EXEC-01: Bu fonksiyon yalnizca `schema_versions.json` sayacini gunceller.
    Gecmiste bu davranis 'uygulandi' sanildi; 0016-0019 SQL'leri DB'ye hic gitmedi
    ve admin login HTTP 500 verdi (UndefinedColumn/UndefinedTable). Gercek uygulama
    icin `--apply` kullanin.
    """
    versions = load_versions()
    current = versions["current_version"]
    applied = []

    for mig in versions["migrations"]:
        if mig["version"] > current and mig["version"] <= target:
            action = "DRY-RUN" if dry_run else "APPLY"
            applied.append(f"{action}: {mig['file']} (v{mig['version']})")

    if not dry_run:
        versions["current_version"] = target
        with open(VERSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(versions, f, ensure_ascii=False, indent=2)

    return applied


def apply_sql(database_url: str, target: int | None = None) -> list[str]:
    """MIGRATE-EXEC-01: Defterdeki SQL dosyalarini gercekten DB'ye uygular.

    Tum migration'lar idempotent (`IF NOT EXISTS`) oldugu icin bastan calistirilabilir;
    bu yuzden `current_version` atlanan dosyalari da kapsar.

    MIGRATE-EXEC-02: Ham DBAPI cursor kullanilir. `text()` DDL icindeki `:isim`
    dizilimini bind parametresi sanıyordu; `exec_driver_sql` ise SQL icindeki `%`
    karakterinde (orn. "96.8% improvement" yorumu) psycopg formatlamasini tetikliyordu.
    Cursor'a parametresiz verilince her iki yorumlama da devre disi kalir.
    """
    from sqlalchemy import create_engine

    engine = create_engine(database_url)
    sonuc = []
    for mig in list_migrations():
        if target is not None and mig["version"] > target:
            continue
        yol = MIGRATIONS_DIR / mig["file"]
        if not yol.exists():
            sonuc.append(f"YOK: {mig['file']}")
            continue
        try:
            with engine.begin() as conn:
                cur = conn.connection.cursor()
                cur.execute(yol.read_text(encoding="utf-8"))
            sonuc.append(f"OK: {mig['file']} (v{mig['version']})")
        except Exception as e:
            sonuc.append(f"HATA: {mig['file']} -> {str(e)[:160]}")
    return sonuc


def _database_url() -> str:
    import os

    url = os.environ.get("DATABASE_URL", "")
    if url:
        return url
    env = MIGRATIONS_DIR.parents[3] / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("DATABASE_URL") and "=" in line:
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    version = "--version" in sys.argv
    apply = "--apply" in sys.argv

    if version:
        print(f"Mevcut versiyon: {get_current_version()}")
        for mig in list_migrations():
            print(f"  v{mig['version']}: {mig['file']}")
    elif apply:
        url = _database_url()
        if not url:
            raise SystemExit("DATABASE_URL bulunamadi")
        for r in apply_sql(url):
            print(r)
    else:
        results = run_migrations(dry_run=dry)
        for r in results:
            print(r)
