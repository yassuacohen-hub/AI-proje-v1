# -*- coding: utf-8 -*-
"""VERI-OSB-MASTER-LISTE-01 Faz A canli olcum (D-238). osbs kolonlar + satirlar + firma sayilari."""
import sys, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"c:\Huginn Data Projesi\Huginn Data Insights\src")
out = []
try:
    from company_master.db.connection import get_database_url
    url = get_database_url()
    out.append("URL_PREFIX " + url.split("://")[0])
    from sqlalchemy import create_engine, text
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    eng = create_engine(url, poolclass=None)
    with eng.connect() as c:
        cols = c.execute(text("SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name='osbs' ORDER BY ordinal_position")).fetchall()
        out.append("OSBS_KOLONLAR:")
        for col in cols:
            out.append(f"  {col[0]} | {col[1]} | null={col[2]} | def={col[3]}")
        rows = c.execute(text("SELECT name, city, district, osb_type, status, website FROM osbs ORDER BY name")).fetchall()
        out.append(f"OSBS_SATIR ({len(rows)}):")
        for r in rows:
            out.append(f"  {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}")
        try:
            fc = c.execute(text("SELECT o.name, count(c.company_id) FROM osbs o LEFT JOIN companies c ON c.osb_id=o.osb_id GROUP BY o.name ORDER BY 2 DESC")).fetchall()
            out.append("FIRMA_SAYISI (osb bazinda):")
            for r in fc:
                out.append(f"  {r[0]}: {r[1]}")
        except Exception as e2:
            out.append("FIRMA_SAYISI HATA: " + str(e2)[:150])
except Exception as e:
    out.append("HATA: " + str(e)[:300])
pathlib.Path(r"c:\Huginn Data Projesi\_tmp\osb_fazA.txt").write_text("\n".join(out), encoding="utf-8")

