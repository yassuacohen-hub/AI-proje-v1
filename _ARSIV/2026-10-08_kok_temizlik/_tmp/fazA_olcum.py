# -*- coding: utf-8 -*-
"""Faz A — canli DB olcumu (D-238). Cikti: _tmp/tobb_havuz_canli_olcum.txt (D-244 kanit)."""
import sys as _s; _s.stdout.reconfigure(encoding="utf-8", errors="replace")
import sys, re
from pathlib import Path
ROOT = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.path.insert(0, str(ROOT / "src"))
from sqlalchemy import text
from company_master.db.connection import get_engine, get_database_url

OUT = ROOT / "_tmp" / "tobb_havuz_canli_olcum.txt"
L = []
def p(*a):
    s = " ".join(str(x) for x in a); print(s); L.append(s)

url = get_database_url()
p("DB:", re.sub(r"//.*@", "//***@", url))
e = get_engine()
with e.connect() as c:
    q = lambda sql, **k: c.execute(text(sql), k).fetchall()

    p("\n== TABLOLAR (public) ==")
    tablolar = [r[0] for r in q("select table_name from information_schema.tables where table_schema='public' order by 1")]
    p(len(tablolar), "tablo")
    for t in ["companies","sources","source_records","key_personnel","job_postings","company_risk_scores",
              "company_opportunity_scores","company_edges","company_locations","company_events","api_analytics",
              "alan_sozlugu","tobb_kart_ham","company_persons","company_capital","company_legal_proceedings"]:
        p(f"  {t:28s}", "VAR" if t in tablolar else "YOK")
    p("  patent*:", [t for t in tablolar if "patent" in t] or "YOK")
    p("  tobb_*:", [t for t in tablolar if t.startswith("tobb_")] or "YOK")

    def d(t):
        p(f"\n== \\d {t} ==")
        rows = q("select column_name,data_type,is_nullable,column_default from information_schema.columns "
                 "where table_schema='public' and table_name=:t order by ordinal_position", t=t)
        for r in rows: p(f"  {r[0]:34s} {r[1]:28s} null={r[2]} def={r[3]}")
        pk = q("select kcu.column_name from information_schema.table_constraints tc join information_schema.key_column_usage kcu "
               "on tc.constraint_name=kcu.constraint_name where tc.table_name=:t and tc.constraint_type='PRIMARY KEY'", t=t)
        p("  PK:", [r[0] for r in pk])
        p("  satir:", q(f'select count(*) from "{t}"')[0][0])

    for t in ["companies","source_records","sources","key_personnel","job_postings","company_risk_scores",
              "company_opportunity_scores","company_edges","company_locations","company_events"]:
        if t in tablolar: d(t)

    p("\n== 0025 dil / ikiz kolon ==")
    cols = {r[0] for r in q("select column_name from information_schema.columns where table_name='companies'")}
    for a, b in [("vergi_dairesi","tax_office"),("vergi_no","tax_id"),("mersis_no","mersis_number"),("unvan","name")]:
        p(f"  {a}={a in cols}  {b}={b in cols}")
    p("  0057 hedef kolonlari zaten var mi:", sorted(cols & {"tobb_status_code","parent_company_id","company_type_code",
                                                          "tsm_code","tax_office_code","business_start_date","closing_date","total_capital"}))

    p("\n== goc defteri (canli) ==")
    for t in ("schema_migrations","schema_versions","migrations","alembic_version"):
        if t in tablolar:
            p(f"  {t}:", q(f'select * from "{t}" order by 1 desc limit 5'))
    p("  api_analytics kolonlari (0054 uygulandi mi?):",
      [r[0] for r in q("select column_name from information_schema.columns where table_name='api_analytics' order by ordinal_position")])

    p("\n== RLS ==")
    p(q("select tablename, rowsecurity from pg_tables where schemaname='public' and tablename in "
        "('companies','source_records','key_personnel','api_analytics') order by 1"))

OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
p("\nyazildi:", OUT)
