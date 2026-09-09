# -*- coding: utf-8 -*-
"""P1-5: NACE'siz kalan firmalar icin sektor/NACE doldurma."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine
from company_master.etl.nace_mapper import nace_bul, load_nace_taxonomy

GLOBAL_FALLBACK = "62.09"
SEKTOR_SAYI = re.compile(r"\d+\s*$")


def norm_tr(s: str) -> str:
    if not s:
        return ""
    m = {"ı": "i", "İ": "i", "ş": "s", "Ş": "s", "ğ": "g", "Ğ": "g",
         "ü": "u", "Ü": "u", "ö": "o", "Ö": "o", "ç": "c", "Ç": "c"}
    return "".join(m.get(ch, ch) for ch in str(s)).lower()


def main() -> None:
    ap = argparse.ArgumentParser(description="NACE doldur (P1-5)")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    kod_isim = {r.code: r.name_tr for r in load_nace_taxonomy()}

    map_path = ROOT / "data" / "nace_to_ostim_sektor.json"
    ostim_map = json.loads(map_path.read_text(encoding="utf-8"))
    meta = ostim_map.get("_meta", {})
    default_by_sektor = {
        norm_tr(k): v for k, v in meta.get("default_nace_by_sektor", {}).items()
    }
    fallback_keywords = meta.get("fallback_keywords", {})

    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(text("SET LOCAL statement_timeout = '300s'"))

        satirlar = conn.execute(text(
            "SELECT company_id, trade_name, legal_name, source_record_id FROM companies "
            "WHERE nace_code IS NULL"
        )).fetchall()
        if args.limit:
            satirlar = satirlar[: args.limit]
        print(f"NACE'siz firma: {len(satirlar)}", flush=True)

        firma = {str(r[0]): (r[1] or r[2] or "", r[3]) for r in satirlar}

        raw_by_src: dict[str, dict] = {}
        src_ids = [str(v[1]) for v in firma.values() if v[1]]
        for i in range(0, len(src_ids), 500):
            parca = src_ids[i:i + 500]
            for s in conn.execute(
                text("SELECT source_record_id, raw_payload FROM source_records "
                     "WHERE source_record_id = ANY(:ids)"),
                {"ids": parca},
            ).fetchall():
                raw_by_src[str(s[0])] = s[1] if isinstance(s[1], dict) else {}

        guncelle: list[tuple] = []
        sayim: Counter = Counter()
        for cid, (unvan, src_id) in firma.items():
            raw = raw_by_src.get(str(src_id), {})
            nace, kaynak, isim = None, None, None

            rn = raw.get("nace_code") or raw.get("naceKod")
            if rn:
                nace = str(rn)[:12]
                kaynak = "external"
                isim = kod_isim.get(nace)

            if not nace:
                sek = raw.get("sektor") or raw.get("meslekGrubu")
                if sek:
                    sek_norm = norm_tr(SEKTOR_SAYI.sub("", str(sek)))
                    dn = default_by_sektor.get(sek_norm)
                    if dn:
                        nace = dn
                        kaynak = "sector_default"

            if not nace and unvan:
                tahminler = nace_bul(unvan)
                if tahminler:
                    nace = tahminler[0].code
                    kaynak = "predicted"
                    isim = tahminler[0].name_tr

            if not nace and unvan:
                u = norm_tr(unvan)
                for sektor_adi, kws in fallback_keywords.items():
                    if any(norm_tr(kw) in u for kw in kws):
                        dn = default_by_sektor.get(norm_tr(sektor_adi))
                        if dn:
                            nace = dn
                            kaynak = "title_default"
                            break

            if not nace:
                nace = GLOBAL_FALLBACK
                kaynak = "fallback"

            guncelle.append((cid, nace, isim, kaynak))
            sayim[kaynak] += 1

        for i in range(0, len(guncelle), 250):
            parca = guncelle[i:i + 250]
            valf = ",".join(
                "(:cid%d, :n%d, :ni%d, :k%d)" % (j, j, j, j)
                for j in range(len(parca))
            )
            p = {}
            for j, (cid, nace, isim, kaynak) in enumerate(parca):
                p["cid%d" % j] = cid
                p["n%d" % j] = nace
                p["ni%d" % j] = isim
                p["k%d" % j] = kaynak
            conn.execute(text(
                "UPDATE companies AS c SET nace_code = v.nace, "
                "nace_name = COALESCE(v.nace_name, c.nace_name), "
                "nace_source = v.kaynak, nace_validity = v.kaynak, "
                "updated_at = NOW() "
                "FROM (VALUES " + valf + ") AS v(cid, nace, nace_name, kaynak) "
                "WHERE c.company_id = v.cid::uuid"
            ), p)

    print("NACE doldurma tamamlandi:", flush=True)
    for k, v in sayim.most_common():
        print(f"  {k}: {v}", flush=True)
    print(f"  TOPLAM: {sum(sayim.values())}", flush=True)


if __name__ == "__main__":
    main()