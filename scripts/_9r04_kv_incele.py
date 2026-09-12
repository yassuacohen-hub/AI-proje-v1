# -*- coding: utf-8 -*-
"""9R-04: kv tablosundaki 'tavily/firecrawl' eşleşmelerinin asıl içeriğini gösterir."""
from __future__ import annotations

import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = r"C:\Users\yasin\AppData\Roaming\9router\db\data.sqlite"
ARANAN = ("firecrawl", "tavily", "jina", "exa", "brave", "serper", "web", "search")


def main() -> int:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    kosul = " OR ".join(f"COALESCE(CAST(key AS TEXT),'') LIKE '%{a}%' OR COALESCE(CAST(value AS TEXT),'') LIKE '%{a}%'" for a in ARANAN)
    cur.execute("PRAGMA table_info(kv)")
    print("kv kolonları:", [r[1] for r in cur.fetchall()])
    try:
        rows = cur.execute(f"SELECT * FROM kv WHERE {kosul}").fetchall()
    except sqlite3.Error as exc:
        rows = []
        print(f"hata: {exc}")
    print(f"kv eşleşme sayısı: {len(rows)}")
    for r in rows:
        o = [str(x)[:400] if x is not None else "None" for x in r]
        print(" -", o)
    # kayıt sayısı
    print("toplam kv kaydı:", cur.execute("SELECT COUNT(*) FROM kv").fetchone()[0])
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())