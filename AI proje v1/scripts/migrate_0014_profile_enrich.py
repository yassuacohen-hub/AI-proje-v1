#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0014: users tablosuna profil zenginleştirme alanları (çalışan sayısı, sertifikalar).

Kullanım: python scripts/migrate_0014_profile_enrich.py
DATABASE_URL yoksa .env'den okur; birden fazla DATABASE_URL_X varsa hepsine uygular.
"""
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]


def load_urls() -> list[str]:
    urls = []
    if os.environ.get("DATABASE_URL"):
        urls.append(os.environ["DATABASE_URL"])
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("DATABASE_URL") and "=" in line:
                u = line.split("=", 1)[1].strip().strip('"').strip("'")
                if u and u not in urls:
                    urls.append(u)
    return urls


SQL = text("""
ALTER TABLE users ADD COLUMN IF NOT EXISTS employee_range VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS certificates TEXT;
""")

if __name__ == "__main__":
    urls = load_urls()
    if not urls:
        raise SystemExit("DATABASE_URL bulunamadi")
    for url in urls:
        try:
            eng = create_engine(url)
            with eng.begin() as conn:
                conn.execute(SQL)
            print(f"OK: {url.split('@')[-1][:60]}")
        except Exception as e:
            print(f"SKIP ({type(e).__name__}): {url.split('@')[-1][:60]} -> {e}")
