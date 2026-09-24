#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0015: users tablosuna sifre alani (password_hash, PBKDF2).

Kullanım: python scripts/migrate_0015_password.py
"""
import os
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
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(256);
ALTER TABLE users ADD COLUMN IF NOT EXISTS tax_number VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(30);
ALTER TABLE users ADD COLUMN IF NOT EXISTS trade_name VARCHAR(200);
ALTER TABLE users ADD COLUMN IF NOT EXISTS address TEXT;
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
            print(f"SKIP: {e}")
