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


# BORC-GOC-IKI-DEFTER-01 (D-265): Asagidaki iki fonksiyon goc UYGULUYORDU ve
# kendi defterini (`schema_versions.json`) tutuyordu. Canli DB'nin defteri ise
# `schema_migrations` tablosu. JSON 23'te donmus, diskteki 34 gocun son 11'ini
# HIC GORMUYOR -> `--apply` bu 11'ini sessizce atlayip "OK" derdi.
# Iki defter = iki gercek. Yazma yolu kapatildi, okuma yolu (`--version`) kaldi.
TEK_KAPI = (
    "Goc uygulama kapisi: python scripts/goc_defteri.py --uygula <dosya.sql>\n"
    "Defter `schema_migrations` tablosudur; schema_versions.json tarihi kayittir."
)


def run_migrations(target: int = 15, dry_run: bool = False) -> list[str]:
    """KAPALI (D-265). SQL calistirmadan JSON sayacini yazip 'uygulandi' sanilirdi."""
    raise SystemExit(TEK_KAPI)


def apply_sql(database_url: str, target: int | None = None) -> list[str]:
    """KAPALI (D-265). JSON defteri eksik oldugu icin gocleri sessizce atliyordu."""
    raise SystemExit(TEK_KAPI)


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
    # MIGRATE-ARG-01 (D-261): taninmayan argüman sessizce `run_migrations()`e dusuyordu.
    # `up` yazan cagri SQL calistirmadan defteri 23 -> 15 geri aldi ve exit 0 verdi.
    BILINEN = {"--dry-run", "--version"}
    if yabanci := [a for a in sys.argv[1:] if a not in BILINEN]:
        raise SystemExit(
            f"Bilinmeyen argüman: {yabanci}. Gecerli: {sorted(BILINEN)}\n"
            "Tek goc uygulamak icin: python scripts/goc_defteri.py --uygula <dosya.sql>"
        )

    if "--version" in sys.argv:
        print(f"Tarihi JSON kayit, versiyon: {get_current_version()}")
        for mig in list_migrations():
            print(f"  v{mig['version']}: {mig['file']}")
        print(f"\n{TEK_KAPI}")
    else:
        raise SystemExit(TEK_KAPI)
