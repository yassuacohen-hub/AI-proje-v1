# -*- coding: utf-8 -*-
"""API-V1-NETWORK-REPORT-01 Faz A canli olcum (D-238). entity_graph semasi + satir + derinlik."""
import sys, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"c:\Huginn Data Projesi\Huginn Data Insights\src")
sys.path.insert(0, r"c:\Huginn Data Projesi\Huginn Data Insights")
out = []
try:
    from src.company_master.db.connection import get_database_url
    from sqlalchemy import create_engine, text
    url = get_database_url()
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    eng = create_engine(url)
    with eng.connect() as c:
        cols = c.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='company_edges' ORDER BY ordinal_position")).fetchall()
        out.append("COMPANY_EDGES_KOLONLAR:")
        for col in cols:
            out.append(f"  {col[0]} | {col[1]}")
        n = c.execute(text("SELECT count(*) FROM company_edges")).scalar()
        out.append(f"TOPLAM_SATIR: {n}")
        et = c.execute(text("SELECT edge_type, count(*) FROM company_edges GROUP BY edge_type ORDER BY 2 DESC")).fetchall()
        out.append("EDGE_TYPE_DAGILIM:")
        for r in et:
            out.append(f"  {r[0]}: {r[1]}")
        # derinlik 2 en kalabalik firma (dügüm sayisi)
        kalabalik = c.execute(text("""
            WITH derece AS (
                SELECT company_a_id AS cid, count(*) AS d FROM company_edges GROUP BY company_a_id
                UNION ALL
                SELECT company_b_id AS cid, count(*) AS d FROM company_edges GROUP BY company_b_id
            )
            SELECT cid, sum(d) AS derece FROM derece GROUP BY cid ORDER BY derece DESC LIMIT 5
        """)).fetchall()
        out.append("EN_KALABALIK (derece top5):")
        for r in kalabalik:
            out.append(f"  {r[0]}: {r[1]}")
        # company_persons bag
        try:
            cp = c.execute(text("SELECT count(*) FROM company_persons")).scalar()
            out.append(f"COMPANY_PERSONS_SATIR: {cp}")
        except Exception as e:
            out.append("COMPANY_PERSONS: " + str(e)[:80])
except Exception as e:
    out.append("HATA: " + str(e)[:300])
pathlib.Path(r"c:\Huginn Data Projesi\_tmp\net_fazA.txt").write_text("\n".join(out), encoding="utf-8")
