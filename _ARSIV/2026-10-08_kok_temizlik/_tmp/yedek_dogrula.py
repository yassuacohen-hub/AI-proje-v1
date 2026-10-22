# -*- coding: utf-8 -*-
"""Yedek dosya ici dogrulama (D-244: dosya kanit). gzip butunluk + CREATE TABLE + COPY satir sayimi."""
import gzip, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
yol = sys.argv[1]
hedef = {"companies", "field_dictionary", "schema_migrations", "company_persons", "tobb_card_raw"}
create = 0; copy_tbl = None; sayac = {}; satir = 0
with gzip.open(yol, "rt", encoding="utf-8", errors="replace") as f:
    for ln in f:
        satir += 1
        if ln.startswith("CREATE TABLE "):
            create += 1
        elif ln.startswith("COPY public."):
            m = re.match(r"COPY public\.(\w+)", ln); copy_tbl = m.group(1); sayac[copy_tbl] = 0
        elif copy_tbl:
            if ln.startswith("\\."):
                copy_tbl = None
            else:
                sayac[copy_tbl] += 1
print(f"gzip OK, satir={satir}, CREATE TABLE={create}, COPY tablo={len(sayac)}")
for t in sorted(hedef):
    print(f"  {t}: {sayac.get(t, 'YOK')}")
assert sayac.get("companies") == 10123, sayac.get("companies")
assert sayac.get("field_dictionary") == 138, sayac.get("field_dictionary")
assert sayac.get("schema_migrations") == 59, sayac.get("schema_migrations")
print("MANDAL: 10123/138/59 TUTTU")
