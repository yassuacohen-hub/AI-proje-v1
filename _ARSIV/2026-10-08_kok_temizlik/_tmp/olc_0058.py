# -*- coding: utf-8 -*-
"""0058 canli olcum + mandal kirma (D-238, D-256/4)."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

ok = True
e = get_engine()

def kolonlar(c, t):
    return c.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='public' "
                          "AND table_name=:t ORDER BY ordinal_position"), {"t": t}).scalars().all()

with e.connect() as c:
    loc = kolonlar(c, "company_locations")
    print("company_locations:", len(loc), "(beklenen 17)", "uavt_code" in loc, "address_detail" in loc)
    ok &= len(loc) == 17 and "uavt_code" in loc and "address_detail" in loc
    ev = kolonlar(c, "company_events")
    print("company_events:", len(ev), "(beklenen 15)", "tsg_pdf_hash" in ev)
    ok &= len(ev) == 15 and "tsg_pdf_hash" in ev
    lp = kolonlar(c, "company_legal_proceedings")
    print("company_legal_proceedings:", len(lp), lp, "(beklenen 11)")
    ok &= len(lp) == 11
    con = c.execute(text("SELECT contype, COUNT(*) FROM pg_constraint WHERE conrelid='public.company_legal_proceedings'::regclass GROUP BY contype ORDER BY contype")).all()
    print("legal_proceedings kisit:", con, "(beklenen c=1 f=2 p=1 u=1)")
    ok &= dict(con) == {"c": 1, "f": 2, "p": 1, "u": 1}
    idx = c.execute(text("SELECT COUNT(*) FROM pg_indexes WHERE schemaname='public' AND indexname IN "
                         "('idx_company_locations_uavt_code','idx_legal_proceedings_company','idx_company_events_tsg_pdf_hash')")).scalar()
    print("indeks:", idx, "(beklenen 3)")
    ok &= idx == 3
    df = c.execute(text("SELECT filename FROM public.schema_migrations ORDER BY filename DESC LIMIT 1")).scalar()
    print("defter son:", df, "(beklenen 0058_adres_hukuk_gazete.sql)")
    ok &= df == "0058_adres_hukuk_gazete.sql"
    n = c.execute(text("SELECT COUNT(*) FROM public.schema_migrations")).scalar()
    print("defter toplam:", n, "(beklenen 58)")
    ok &= n == 58

def kir(sql, ad):
    global ok
    with e.connect() as c:
        t = c.begin()
        try:
            c.execute(text(sql))
            print(f"{ad}: KIRILMADI (HATA)"); ok = False
        except Exception as ex:
            print(f"{ad}: kirildi (beklenen): {type(ex).__name__} {str(ex).splitlines()[0][:70]}")
        finally:
            t.rollback()

kir("UPDATE public.company_events SET tsg_pdf_hash='abc' WHERE event_id=(SELECT event_id FROM public.company_events LIMIT 1)", "CHECK tsg_pdf_hash hex64")
kir("INSERT INTO public.company_legal_proceedings(company_id, start_date, end_date) SELECT company_id, '2026-02-01', '2026-01-01' FROM public.companies LIMIT 1", "CHECK end>=start")
kir("INSERT INTO public.company_legal_proceedings(company_id) VALUES (gen_random_uuid())", "FK company_id")
kir("INSERT INTO public.company_locations(company_id, address_detail) SELECT company_id, NULL FROM public.companies LIMIT 1", "NOT NULL address_detail")
with e.connect() as c:
    print("legal_proceedings satir (rollback sonrasi):", c.execute(text("SELECT COUNT(*) FROM public.company_legal_proceedings")).scalar())
    print("tsg_pdf_hash='abc':", c.execute(text("SELECT COUNT(*) FROM public.company_events WHERE tsg_pdf_hash='abc'")).scalar())
print("OLCUM OK" if ok else "OLCUM HATA")
sys.exit(0 if ok else 1)
