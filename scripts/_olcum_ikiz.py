# -*- coding: utf-8 -*-
"""SEMA-IKIZ-01 olcumu. Gecici; is bitince silinir (BORC-SCRIPTS-01)."""
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402
from company_master.etl.kimlik_no import kimlik_dogrula  # noqa: E402

CIFTLER = [
    ("vergi_no", "tax_number"),
    ("web_sitesi", "website_domain"),
    ("adres", "address"),
    ("osb_parsel", "osb_parcel"),
    ("ip_adresi", "ip_address"),
]

satir = []
p = satir.append

with get_engine().connect() as conn:
    # ip_adresi companies'te degil; tum semada nerede oldugunu bul.
    p("Turkce kolonlarin tum semadaki yeri:")
    for r in conn.execute(
        text(
            "SELECT table_name, column_name, data_type FROM information_schema.columns"
            " WHERE table_schema='public' AND (column_name ~ '[cgiosuCGIOSU]'"
            "   AND column_name IN ('vergi_no','web_sitesi','adres','osb_parsel',"
            "                       'ip_adresi','ip_address','address','osb_parcel'))"
            " ORDER BY table_name, column_name"
        )
    ):
        p(f"  {r.table_name}.{r.column_name}  ({r.data_type})")
    p("")

    kolonlar = {
        r[0]
        for r in conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name='companies'"
            )
        )
    }
    toplam = conn.execute(text("SELECT count(*) FROM companies")).scalar()
    p(f"companies satir: {toplam}")
    p("")
    p("kolon varligi:")
    for tr, en in CIFTLER:
        p(f"  {tr:12s} {'VAR' if tr in kolonlar else 'yok':4s}   "
          f"{en:16s} {'VAR' if en in kolonlar else 'yok'}")
    p("")

    for tr, en in CIFTLER:
        p(f"=== {tr} -> {en} ===")
        if tr not in kolonlar:
            p("  kaynak kolon yok, atla")
            p("")
            continue
        if en not in kolonlar:
            n = conn.execute(
                text(f"SELECT count(*) FROM companies WHERE {tr} IS NOT NULL "
                     f"AND btrim({tr}::text) <> ''")
            ).scalar()
            p(f"  hedef kolon YOK -> duz RENAME. kaynak dolu: {n}")
            p("")
            continue
        r = conn.execute(
            text(
                f"SELECT count(*) FILTER (WHERE t IS NOT NULL AND e IS NULL) tr_only,"
                f"       count(*) FILTER (WHERE t IS NULL AND e IS NOT NULL) en_only,"
                f"       count(*) FILTER (WHERE t IS NOT NULL AND e IS NOT NULL) ikisi,"
                f"       count(*) FILTER (WHERE t IS NOT NULL) tr_dolu,"
                f"       count(*) FILTER (WHERE e IS NOT NULL) en_dolu,"
                f"       count(*) FILTER (WHERE t IS NOT NULL AND e IS NOT NULL"
                f"                        AND btrim(lower(t))=btrim(lower(e))) ayni,"
                f"       count(*) FILTER (WHERE t IS NOT NULL AND e IS NOT NULL"
                f"                        AND btrim(lower(t))<>btrim(lower(e))) farkli"
                f"  FROM (SELECT nullif(btrim({tr}::text),'') t,"
                f"               nullif(btrim({en}::text),'') e FROM companies) x"
            )
        ).one()
        p(f"  TR dolu={r.tr_dolu}  EN dolu={r.en_dolu}")
        p(f"  sadece TR={r.tr_only}  sadece EN={r.en_only}  ikisi de={r.ikisi}")
        p(f"  ikisi de dolu icinde: ayni={r.ayni}  FARKLI={r.farkli}")
        if r.farkli:
            p("  --- farkli deger tasiyan kayitlar ---")
            for row in conn.execute(
                text(
                    f"SELECT company_id, legal_name, {tr}::text t, {en}::text e"
                    f"  FROM companies"
                    f" WHERE nullif(btrim({tr}::text),'') IS NOT NULL"
                    f"   AND nullif(btrim({en}::text),'') IS NOT NULL"
                    f"   AND btrim(lower({tr}::text)) <> btrim(lower({en}::text))"
                    f" ORDER BY company_id LIMIT 40"
                )
            ):
                p(f"    id={row.company_id} | {row.legal_name}")
                p(f"       {tr}={row.t!r}")
                p(f"       {en}={row.e!r}")
        p("")

    # D-246 kapisi: vergi_no degerleri gecerli VKN/TCKN mi?
    if "vergi_no" in kolonlar:
        p("=== vergi_no D-246 kapisi (kimlik_dogrula) ===")
        rows = conn.execute(
            text("SELECT company_id, legal_name, vergi_no::text v,"
                 "       tax_number::text tn FROM companies"
                 " WHERE nullif(btrim(vergi_no::text),'') IS NOT NULL")
        ).all()
        sayac = {"vkn": 0, "tckn": 0, "gecersiz": 0}
        gecersizler = []
        for row in rows:
            no, tur = kimlik_dogrula(row.v)
            sayac[tur] += 1
            if tur == "gecersiz":
                gecersizler.append((row.company_id, row.legal_name, row.v))
            elif no != row.v.strip():
                p(f"  NORMALIZE gerekli: id={row.company_id} {row.v!r} -> {no!r}")
        p(f"  toplam={len(rows)} vkn={sayac['vkn']} tckn={sayac['tckn']} "
          f"gecersiz={sayac['gecersiz']}")
        for i, (cid, ad, v) in enumerate(gecersizler[:30]):
            p(f"    gecersiz id={cid} | {ad} | {v!r} (len={len(str(v).strip())})")
        if len(gecersizler) > 30:
            p(f"    ... +{len(gecersizler)-30} kayit daha")

rapor = "\n".join(satir)
print(rapor.encode("ascii", "replace").decode("ascii"))
(KOK / "_olcum_ikiz.txt").write_text(rapor, encoding="utf-8")
