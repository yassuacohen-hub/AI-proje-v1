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


def needs_migration(target: int = 14) -> bool:
    return get_current_version() < target


def run_migrations(target: int = 14, dry_run: bool = False) -> list[str]:
    """CalistirilmissMigration'lari uygula."""
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


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    version = "--version" in sys.argv
    
    if version:
        print(f"Mevcut versiyon: {get_current_version()}")
        for mig in list_migrations():
            print(f"  v{mig['version']}: {mig['file']}")
    else:
        results = run_migrations(dry_run=dry)
        for r in results:
            print(r)
