# -*- coding: utf-8 -*-
"""DENET-7 rapor: SQLite dosyalarinin icerigi (dokumantasyon oncesi)."""
import sqlite3
from pathlib import Path

ROOT = Path.cwd()
for p in ["company_master.db", "test.db", "backups/company_master_pre_dedup_20260908_090326.db", "data/ankara_osb.db"]:
    f = ROOT / p
    if not f.exists():
        print(f, "-> YOK")
        continue
    if f.stat().st_size == 0:
        print(f, "-> BOS (0 bayt)")
        continue
    try:
        c = sqlite3.connect(str(f))
        tablolar = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        ozet = []
        for t in tablolar[:8]:
            try:
                n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            except Exception:
                n = "?"
            ozet.append(f"{t}={n}")
        print(f, f"-> {len(tablolar)} tablo | " + ", ".join(ozet))
        c.close()
    except Exception as e:
        print(f, "-> HATA:", e)