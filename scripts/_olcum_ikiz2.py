# -*- coding: utf-8 -*-
"""SEMA-IKIZ-01 ikinci olcum: vergi_no ICINDE NE VAR? Gecici betik."""
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402
from company_master.etl.kimlik_no import (  # noqa: E402
    kimlik_dogrula,
    sicil_dogrula,
)

satir = []
p = satir.append

with get_engine().connect() as conn:
    rows = conn.execute(
        text(
            "SELECT company_id, legal_name, vergi_no::text v, tax_number::text tn,"
            "       trade_registry_number::text tr FROM companies"
            " WHERE nullif(btrim(vergi_no::text),'') IS NOT NULL"
        )
    ).all()

    p(f"vergi_no dolu: {len(rows)}")
    hane = Counter()
    sicil_adayi = 0
    for r in rows:
        v = r.v.strip()
        rakam = "".join(c for c in v if c.isdigit())
        no, tur = kimlik_dogrula(v)
        if tur == "gecersiz":
            s, _ = sicil_dogrula(v)
            if s:
                sicil_adayi += 1
                hane[f"{len(rakam)} hane -> SICIL adayi"] += 1
            else:
                hane[f"{len(rakam)} hane -> siniflandirilamadi"] += 1
        else:
            hane[f"{len(rakam)} hane -> {tur.upper()} gecerli"] += 1
    p("")
    p("vergi_no icerik dagilimi:")
    for k, n in sorted(hane.items(), key=lambda x: -x[1]):
        p(f"  {n:5d}  {k}")
    p(f"  => sicil_dogrula() gecen: {sicil_adayi}")

    # trade_registry_number ile cakisma: sicil zaten dolu mu?
    p("")
    p("sicil kolonu durumu (vergi_no dolu satirlarda):")
    p(f"  trade_registry_number dolu: {sum(1 for r in rows if r.tr)}")

    # tax_number kolonunun kendi kalitesi (hedef kolon temiz mi?)
    p("")
    p("=== tax_number kolonunun kendi kalitesi ===")
    tn = conn.execute(
        text("SELECT company_id, legal_name, tax_number::text v FROM companies"
             " WHERE nullif(btrim(tax_number::text),'') IS NOT NULL")
    ).all()
    tsay = Counter()
    for r in tn:
        rakam = "".join(c for c in (r.v or "") if c.isdigit())
        _, tur = kimlik_dogrula(r.v)
        tsay[f"{len(rakam)} hane -> {tur}"] += 1
    p(f"  tax_number dolu: {len(tn)}")
    for k, n in sorted(tsay.items(), key=lambda x: -x[1]):
        p(f"  {n:5d}  {k}")

    # Tasinabilir aday: sadece TR dolu VE kimlik_dogrula geciyor
    p("")
    p("=== D-246 kapisini gecen ve tasinabilir olanlar ===")
    tasinir = []
    for r in rows:
        if r.tn:
            continue  # hedef dolu, cakisma yolu
        no, tur = kimlik_dogrula(r.v)
        if no:
            tasinir.append((r.company_id, r.legal_name, r.v, no, tur))
    p(f"  sadece vergi_no dolu + gecerli = {len(tasinir)}")
    for cid, ad, ham, no, tur in tasinir:
        p(f"    {cid} | {ad} | {ham!r} -> {no} ({tur})")

    # Cakisan (ikisi de dolu) 31 kaydin durumu
    p("")
    p("=== ikisi de dolu (31) - hangisi gecerli? ===")
    c = Counter()
    for r in rows:
        if not r.tn:
            continue
        _, t1 = kimlik_dogrula(r.v)
        _, t2 = kimlik_dogrula(r.tn)
        ayni = r.v.strip().lower() == r.tn.strip().lower()
        c[f"vergi_no={t1} / tax_number={t2} / ayni={ayni}"] += 1
    for k, n in sorted(c.items(), key=lambda x: -x[1]):
        p(f"  {n:5d}  {k}")

rapor = "\n".join(satir)
print(rapor.encode("ascii", "replace").decode("ascii"))
(KOK / "_olcum_ikiz2.txt").write_text(rapor, encoding="utf-8")
