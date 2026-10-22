# -*- coding: utf-8 -*-
"""0057 canli olcum + mandal kirma (D-238, D-256/4)."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

YENI = ["company_type_code", "tsm_code", "business_start_date", "closing_date",
        "tobb_status_code", "total_capital", "parent_company_id"]
ok = True
e = get_engine()
with e.connect() as c:
    cols = c.execute(text("SELECT column_name, data_type FROM information_schema.columns "
                          "WHERE table_schema='public' AND table_name='companies'")).all()
    d = dict(cols)
    print("companies kolon:", len(cols), "(beklenen 66)")
    ok &= len(cols) == 66
    for k in YENI:
        print(f"  {k:22} {d.get(k)}")
        ok &= k in d
    print("tax_office_code var mi:", "tax_office_code" in d, "(beklenen False)")
    ok &= "tax_office_code" not in d
    cap = c.execute(text("SELECT column_name FROM information_schema.columns "
                         "WHERE table_schema='public' AND table_name='company_capital' ORDER BY ordinal_position")).scalars().all()
    print("company_capital kolon:", len(cap), cap, "(beklenen 7)")
    ok &= len(cap) == 7
    fk = c.execute(text("SELECT COUNT(*) FROM pg_constraint WHERE conrelid='public.companies'::regclass "
                        "AND contype='f' AND conname LIKE 'companies_%' AND conname IN "
                        "('companies_company_type_code_fkey','companies_tsm_code_fkey','companies_tobb_status_code_fkey','companies_parent_company_id_fkey')")).scalar()
    print("companies yeni FK:", fk, "(beklenen 4)")
    ok &= fk == 4
    idx = c.execute(text("SELECT COUNT(*) FROM pg_indexes WHERE tablename='companies' AND indexname IN "
                         "('idx_companies_tobb_status_code','idx_companies_company_type_code','idx_companies_parent_company_id')")).scalar()
    print("indeks:", idx, "(beklenen 3)")
    ok &= idx == 3
    chk = c.execute(text("SELECT COUNT(*) FROM pg_constraint WHERE conrelid='public.company_capital'::regclass AND contype='c'")).scalar()
    print("company_capital CHECK:", chk, "(beklenen 4)")
    ok &= chk == 4
    cm = c.execute(text("SELECT COUNT(*) FROM pg_description d JOIN pg_attribute a ON a.attrelid=d.objoid AND a.attnum=d.objsubid "
                        "WHERE d.objoid='public.companies'::regclass AND a.attname = ANY(:k)"), {"k": YENI}).scalar()
    print("kolon COMMENT:", cm, "(beklenen 7)")
    ok &= cm == 7
    df = c.execute(text("SELECT COUNT(*) FROM public.schema_migrations WHERE filename='0057_companies_tobb_kolonlari.sql'")).scalar()
    print("defter:", df, "(beklenen 1)")
    ok &= df == 1
    # dolu sayilar (yeni kolonlar bos olmali: ETL henuz yok)
    n = c.execute(text("SELECT COUNT(*) FROM public.companies WHERE tobb_status_code IS NOT NULL OR company_type_code IS NOT NULL")).scalar()
    print("companies TOBB kodlu satir:", n, "(beklenen 0, ETL yok)")

# Mandal kirma: FK + CHECK (rollback)
def kir(sql, ad):
    global ok
    with e.connect() as c:
        t = c.begin()
        try:
            c.execute(text(sql))
            print(f"{ad}: KIRILMADI (HATA)"); ok = False
        except Exception as ex:
            print(f"{ad}: kirildi (beklenen): {type(ex).__name__.split('.')[-1]} {str(ex).splitlines()[0][:70]}")
        finally:
            t.rollback()

kir("UPDATE public.companies SET tobb_status_code = 9999 WHERE company_id = (SELECT company_id FROM public.companies LIMIT 1)", "FK tobb_status_code")
kir("UPDATE public.companies SET total_capital = -1 WHERE company_id = (SELECT company_id FROM public.companies LIMIT 1)", "CHECK total_capital")
kir("INSERT INTO public.company_capital(company_id, par_value) SELECT company_id, -0.5 FROM public.companies LIMIT 1", "CHECK par_value")
kir("INSERT INTO public.company_capital(company_id) VALUES (gen_random_uuid())", "FK company_capital.company_id")
with e.connect() as c:
    print("company_capital satir (rollback sonrasi):", c.execute(text("SELECT COUNT(*) FROM public.company_capital")).scalar())
    print("companies tobb_status_code=9999:", c.execute(text("SELECT COUNT(*) FROM public.companies WHERE tobb_status_code=9999")).scalar())
print("OLCUM OK" if ok else "OLCUM HATA")
sys.exit(0 if ok else 1)
