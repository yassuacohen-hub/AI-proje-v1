# -*- coding: utf-8 -*-
"""9R-04: 9Router SQLite veri tabanında web provider kayıtlarını tarar.

Salt-okunur sorgu: firecrawl/tavily/jina/exa gibi web provider adlarının
hangi tabloda/kolonda geçtiğini bulur; kimlik bilgilerinin gerçekten
DB'ye ulaşıp ulaşmadığını kanıtlar.
"""
from __future__ import annotations

import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = r"C:\Users\yasin\AppData\Roaming\9router\db\data.sqlite"
ARANAN = ("firecrawl", "tavily", "jina-reader", "jina", "exa", "brave", "serper")
# not: "brave" geniş eşleşebilir (brave-search vs.), sadece raporlarız.


def main() -> int:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    tablolar = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    print(f"Tablolar: {tablolar}\n")

    bulundu = False
    for t in tablolar:
        kolonlar = [r[1] for r in cur.execute(f"PRAGMA table_info({t})")]
        for c in kolonlar:
            try:
                kosul = " OR ".join(f"CAST({c} AS TEXT) LIKE '%{a}%'" for a in ARANAN)
                q = f"SELECT COUNT(*) FROM {t} WHERE {kosul}"
                n = cur.execute(q).fetchone()[0]
                if n:
                    print(f"EŞLEŞME: tablo={t} kolon={c} sayı={n}")
                    bulundu = True
            except sqlite3.Error:
                # kolon sorgulanamıyor (JSON kolon vs.) — tolere et
                pass

    if not bulundu:
        print("HİÇBİR tabloda web provider (firecrawl/tavily/jina/exa/brave/serper) geçmiyor.")
        print("=> Dashboard ekranında girilen anahtarlar bu lokal SQLite'a kaydedilmemiş.")

    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())