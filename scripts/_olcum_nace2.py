# -*- coding: utf-8 -*-
"""OLCUM-NACE-02: sozluk kalitesi (gecici betik).

Urun sahibi "kod yanina acilim koyalim" dedi. Acilim nace_codes.title'dan
gelecek. O halde once title'in kendisi olculmeli: dolu mu, tek dilde mi,
kodlama bozuk mu, sector_group kullanilabilir mi.
"""
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from company_master.db.connection import get_engine  # noqa: E402

with get_engine().connect() as c:
    print("=" * 70)
    print("C) NACE SOZLUGU (nace_codes) KULLANILABILIR MI?")
    print("=" * 70)

    n = c.execute(text("SELECT count(*) FROM nace_codes")).scalar()
    print(f"\n  toplam kod: {n}")

    print("\n  C1) title doluluk (seviye bazinda):")
    for lvl, top, bos in c.execute(text("""
        SELECT level, count(*),
               count(*) FILTER (WHERE title IS NULL OR btrim(title)='')
        FROM nace_codes GROUP BY level ORDER BY level""")):
        print(f"     level {lvl}: {top:5} kod, {bos:5} bos baslik "
              f"({100*bos//max(top,1)}%)")

    print("\n  C2) title dili: Turkce karakter iceren vs icermeyen")
    tr = c.execute(text(
        "SELECT count(*) FROM nace_codes WHERE title ~ '[çğıöşüÇĞİÖŞÜ]'")).scalar()
    print(f"     Turkce karakterli baslik: {tr}")
    print("     ornek 5 baslik (ham):")
    for (t,) in c.execute(text(
            "SELECT title FROM nace_codes WHERE title IS NOT NULL "
            "AND btrim(title)<>'' ORDER BY nace_code LIMIT 5")):
        print(f"       {t!r}")

    print("\n  C3) kodlama bozuklugu (mojibake) tarayici:")
    bozuk = c.execute(text(
        "SELECT count(*) FROM nace_codes WHERE title LIKE '%Ã%' "
        "OR title LIKE '%Ä%' OR title LIKE '%Å%' OR title LIKE '%�%'")).scalar()
    print(f"     bozuk gorunen baslik: {bozuk}")
    for (t,) in c.execute(text(
            "SELECT title FROM nace_codes WHERE title LIKE '%Ã%' "
            "OR title LIKE '%Ä%' OR title LIKE '%Å%' OR title LIKE '%�%' LIMIT 3")):
        print(f"       {t!r}")

    print("\n  C4) sector_group + is_manufacturing kullanilabilir mi:")
    for kol in ("sector_group", "is_manufacturing", "parent_code", "version"):
        dolu = c.execute(text(
            f"SELECT count(*) FROM nace_codes WHERE {kol} IS NOT NULL "
            f"AND btrim({kol}::text) <> ''")).scalar()
        farkli = c.execute(text(
            f"SELECT count(DISTINCT {kol}) FROM nace_codes")).scalar()
        print(f"     {kol:18} dolu={dolu:5} farkli={farkli}")

    print("\n  C5) 29.10 gercekten ne? (1880 firmaya atanan kod)")
    for kod, lvl, par, t in c.execute(text(
            "SELECT nace_code, level, parent_code, title FROM nace_codes "
            "WHERE nace_code IN ('29','29.1','29.10','29.10.01') "
            "ORDER BY nace_code")):
        print(f"     {kod:10} lvl={lvl} parent={par!r} title={t!r}")

    print("\n  C6) companies.nace_name'in 8 degeri (olu kolon mu?):")
    for v, adet in c.execute(text(
            "SELECT nace_name, count(*) FROM companies WHERE nace_name IS NOT NULL "
            "AND btrim(nace_name)<>'' GROUP BY 1 ORDER BY 2 DESC")):
        print(f"     {adet:4} x {v!r}")

    print("\n  C7) 'GERCEK' nace kodu olan firma var mi? (tahmin disi kaynak)")
    for s, adet in c.execute(text(
            "SELECT nace_source, count(*) FROM companies "
            "WHERE nace_code IS NOT NULL AND btrim(nace_code)<>'' "
            "GROUP BY 1 ORDER BY 2 DESC")):
        print(f"     {str(s):22} -> {adet}")

    print("\n  C8) sozlukte level 6 (en ince) kod var; biz level 4 kullaniyoruz.")
    ornek = c.execute(text(
        "SELECT count(*) FROM nace_codes WHERE level=6 "
        "AND parent_code LIKE '29.10%'")).scalar()
    print(f"     29.10 altindaki level-6 kod sayisi: {ornek}")
    for kod, t in c.execute(text(
            "SELECT nace_code, title FROM nace_codes WHERE level=6 "
            "AND nace_code LIKE '29.10%' ORDER BY nace_code LIMIT 6")):
        print(f"       {kod:12} {t!r}")
