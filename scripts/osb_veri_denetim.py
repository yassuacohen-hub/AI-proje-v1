# -*- coding: utf-8 -*-
"""OSB veri seti denetim kapisi — teslim beyanini olcer (D-238, D-260).

Neden kalici: her `VERI-OSB-*` teslimi bu kapidan gecer. Beyan edilen
"N kayit, slug tekil" iddiasi burada olculur; teslim ozeti kanit degildir.

Kullanim:
    python scripts/osb_veri_denetim.py                 # rapor
    python scripts/osb_veri_denetim.py --kontrol 8987  # beyan dogrula (exit 1 = uyusmazlik)

Ilgili: [[AGENTS]] D-238 · D-260 · D-305
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

KOK = pathlib.Path(__file__).resolve().parents[1] / "data" / "osb"
KIMLIK = "company_slug"


def tara(kok: pathlib.Path = KOK) -> dict:
    """Her OSB klasorunu okur; kayit sayisi, kimlik tekilligi, mojibake dondurur."""
    osb: dict[str, dict] = {}
    slug = collections.Counter()
    kimliksiz = mojibake = 0

    for dosya in sorted(kok.glob("*/firmalar.jsonl")):
        adet = 0
        eksik = 0
        for satir in dosya.read_text(encoding="utf-8").splitlines():
            if not satir.strip():
                continue
            kayit = json.loads(satir)
            adet += 1
            deger = kayit.get(KIMLIK)
            if deger:
                slug[deger] += 1
            else:
                eksik += 1
            if "\ufffd" in (kayit.get("legal_name") or ""):
                mojibake += 1
        osb[dosya.parent.name] = {"adet": adet, "kimliksiz": eksik}
        kimliksiz += eksik

    return {
        "osb": osb,
        "toplam": sum(v["adet"] for v in osb.values()),
        "tekil": len(slug),
        "mukerrer": sum(v - 1 for v in slug.values() if v > 1),
        "kimliksiz": kimliksiz,
        "mojibake": mojibake,
    }


def yaz(s: dict) -> None:
    for ad, v in s["osb"].items():
        iz = f"  kimliksiz={v['kimliksiz']}" if v["kimliksiz"] else ""
        print(f"{ad:18s} {v['adet']:6d}{iz}")
    print(f"\nTOPLAM kayit     : {s['toplam']}")
    print(f"TEKIL {KIMLIK}: {s['tekil']}")
    print(f"MUKERRER         : {s['mukerrer']}")
    print(f"KIMLIKSIZ satir  : {s['kimliksiz']}")
    print(f"MOJIBAKE ad      : {s['mojibake']}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kontrol", type=int, help="beyan edilen toplam kayit sayisi")
    a = ap.parse_args(argv)

    s = tara()
    yaz(s)

    if a.kontrol is not None and s["toplam"] != a.kontrol:
        print(f"\nUYUSMAZLIK: beyan {a.kontrol}, olculen {s['toplam']}")
        return 1
    return 0


def _self_check() -> None:
    """Assert tabanli ic kontrol (framework yok). `python osb_veri_denetim.py --self`"""
    s = tara()
    assert s["toplam"] > 0, "hic kayit okunmadi - yol yanlis olabilir"
    assert s["tekil"] + s["mukerrer"] + s["kimliksiz"] == s["toplam"], (
        f"muhasebe tutmuyor: {s['tekil']}+{s['mukerrer']}+{s['kimliksiz']} != {s['toplam']}"
    )
    print("self-check OK")


if __name__ == "__main__":
    if "--self" in sys.argv:
        _self_check()
    else:
        raise SystemExit(main())
