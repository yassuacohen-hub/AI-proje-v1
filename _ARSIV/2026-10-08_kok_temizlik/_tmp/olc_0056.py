# -*- coding: utf-8 -*-
"""0056 sonrasi canli olcum (D-238) + mandal kirma (D-256/4)."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

BEKLENEN = {
    "tobb_company_type_group": 9, "tobb_company_type": 28, "tobb_status": 10,
    "tobb_registry_office": 238, "tobb_city": 81, "tobb_representation_type": 5,
    "tobb_representation_duty": 30, "tobb_representation_authority": 11,
}
eng = get_engine()
with eng.connect() as c:
    print("| tablo | beklenen | canli | ok |")
    print("|---|---|---|---|")
    hepsi_ok = True
    for t, n in BEKLENEN.items():
        m = c.execute(text(f"SELECT count(*) FROM public.{t}")).scalar()
        hepsi_ok &= (m == n)
        print(f"| {t} | {n} | {m} | {'OK' if m == n else 'FARK'} |")
    duty_dolu = c.execute(text("SELECT count(*) FROM public.tobb_representation_duty WHERE representation_type_code IS NOT NULL")).scalar()
    fk_kopuk = c.execute(text("""SELECT count(*) FROM public.tobb_representation_duty d
        LEFT JOIN public.tobb_representation_type t ON t.code = d.representation_type_code
        WHERE d.representation_type_code IS NOT NULL AND t.code IS NULL""")).scalar()
    kol = {r[0]: r[1] for r in c.execute(text("""SELECT table_name, count(*) FROM information_schema.columns
        WHERE table_schema='public' AND table_name IN ('company_persons','company_person_joint') GROUP BY 1"""))}
    idx = c.execute(text("SELECT count(*) FROM pg_indexes WHERE schemaname='public' AND tablename IN ('company_persons','company_person_joint')")).scalar()
    chk = c.execute(text("SELECT count(*) FROM pg_constraint WHERE conname IN ('chk_company_persons_share_pct')")).scalar()
    fk_n = c.execute(text("SELECT count(*) FROM pg_constraint WHERE contype='f' AND conrelid='public.company_persons'::regclass")).scalar()
    yorum = c.execute(text("SELECT obj_description('public.key_personnel'::regclass)")).scalar() or ""
    defter = c.execute(text("SELECT count(*) FROM public.schema_migrations WHERE filename='0056_tobb_sozluk_seed_company_persons.sql'")).scalar()
    print(f"\nduty.representation_type_code dolu: {duty_dolu}/30, kopuk FK: {fk_kopuk}")
    print(f"company_persons kolon: {kol.get('company_persons')}, company_person_joint kolon: {kol.get('company_person_joint')}")
    print(f"indeks (2 tablo, PK dahil): {idx}, share_pct CHECK: {chk}, company_persons FK sayisi: {fk_n}")
    print(f"key_personnel COMMENT PASIF: {'PASIF' in yorum}")
    print(f"defter 0056: {defter}")
    assert hepsi_ok and duty_dolu == 30 and fk_kopuk == 0 and defter == 1, "OLCUM FARK"

# Mandal kirma: share_pct 150 -> CHECK reddetmeli; rollback
with eng.connect() as c:
    tr = c.begin()
    try:
        cid = c.execute(text("SELECT company_id FROM public.companies LIMIT 1")).scalar()
        c.execute(text("INSERT INTO public.company_persons (company_id, role_group, share_pct) VALUES (:c, 'partner', 150)"), {"c": cid})
        print("MANDAL KIRILMADI (HATA)")
    except Exception as e:
        print("mandal kirildi (beklenen):", str(e).splitlines()[0][:120])
    finally:
        tr.rollback()
    tr = c.begin()
    try:
        c.execute(text("INSERT INTO public.company_persons (company_id, role_group) VALUES (:c, 'x')"), {"c": cid})
        print("MANDAL KIRILMADI (HATA)")
    except Exception as e:
        print("role_group mandal kirildi (beklenen):", str(e).splitlines()[0][:120])
    finally:
        tr.rollback()
    n = c.execute(text("SELECT count(*) FROM public.company_persons")).scalar()
    print("company_persons satir (rollback sonrasi):", n)
    assert n == 0
print("OLCUM OK")
