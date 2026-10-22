# -*- coding: utf-8 -*-
"""0055-0058 yeni tablolar: RLS acik mi, anon/authenticated GRANT var mi? (D-238 canli olcum)"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

TABLOLAR = [
    "field_dictionary", "tobb_card_raw", "tobb_company_type_group", "tobb_company_type",
    "tobb_status", "tobb_registry_office", "tobb_city", "tobb_representation_duty",
    "tobb_representation_authority", "tobb_representation_type",
    "company_persons", "company_capital", "company_legal_proceedings",
]

with get_engine().connect() as c:
    rls = dict(c.execute(text(
        "SELECT relname, relrowsecurity FROM pg_class "
        "WHERE relnamespace='public'::regnamespace AND relname = ANY(:t)"), {"t": TABLOLAR}).fetchall())
    grants = c.execute(text(
        "SELECT table_name, grantee, count(*) FROM information_schema.role_table_grants "
        "WHERE table_schema='public' AND grantee IN ('anon','authenticated') AND table_name = ANY(:t) "
        "GROUP BY 1,2"), {"t": TABLOLAR}).fetchall()
    kapali = [t for t in TABLOLAR if not rls.get(t)]
    yok = [t for t in TABLOLAR if t not in rls]
    print("tablo:", len(TABLOLAR), "bulunan:", len(rls), "yok:", yok)
    print("RLS kapali:", len(kapali), kapali)
    print("anon/auth grant:", grants)
