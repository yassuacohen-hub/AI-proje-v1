# -*- coding: utf-8 -*-
"""OSTIM detay kaziyicisi web_sitesi href filtresi olcumu (D-292, VERI-OSTIM-HREF-FILTRE-01).

Doluluk != kalite: `web_sitesi` dolu olmak dogru adres olmak demek degil.
Bu betik, mevcut ciktida dolu olan her adresin **duzeltilmis filtreyi gecirip
gecirmedigini** olcer.

Neden ureticiden import eder (D-211, D-266):
    Betigin ilk hali kendi `KOTU_DESEN` regex'ini tasiyordu ve bu liste
    ureticiden kesti: `nsosyal.com` listede yoktu. Olcum 1555 dolu kaydin
    yalniz 140'ini yanlis-pozitif saydi; gercek tablo 1555/1555. Yani olcum
    aracinin **kendi** hatasini gizliyordu -- D-309/1 "aracin yesil demesi
    kanit degil". Olcum ureticinin kendi kuralini (`_is_company_website`)
    dogrudan cagirir; iki kopya olmaz, sapma olamaz.

Kullanim:
    python -X utf8 scripts/ostim_href_olc.py
    python -X utf8 scripts/ostim_href_olc.py --detay 30

Idempotent: yalniz okur, hicbir dosyaya yazmaz.
"""
import argparse
import io
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

VARSAYILAN = ROOT / "data" / "ostim" / "firmalar_detailed.jsonl"

from company_master.etl.scrapers.ostim_detail_scraper import (  # noqa: E402
    WEB_BLOCKLIST,
    _is_company_website,
)


def satirlari_oku(yol: Path) -> list[dict]:
    """JSONL okur. Bozuk/BOB satirlari atlanir ve sayilir."""
    kayitlar, bozuk = [], 0
    if not yol.exists():
        return kayitlar, 1
    with io.open(yol, encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                kayitlar.append(json.loads(line))
            except json.JSONDecodeError:
                bozuk += 1
    return kayitlar, bozuk


def olc(yol: Path) -> dict:
    kayitlar, bozuk = satirlari_oku(yol)
    dolu = [k for k in kayitlar if (k.get("web_sitesi") or "").strip()]
    kotu = [k for k in dolu if not _is_company_website(k["web_sitesi"])]
    gecen = [k for k in dolu if _is_company_website(k["web_sitesi"])]
    oran = (len(kotu) / len(dolu) * 100) if dolu else 0.0
    tekil_gecen = sorted({k["web_sitesi"] for k in gecen})
    return {
        "dosya": str(yol),
        "satir": len(kayitlar),
        "bozuk_satir": bozuk,
        "web_sitesi_dolu": len(dolu),
        "yanlis_pozitif": len(kotu),
        "oran_yuzde": round(oran, 2),
        "filtreyi_gecen": len(gecen),
        "tekil_gecen": tekil_gecen,
        "bloklist_uzunluk": len(WEB_BLOCKLIST),
        "kotu_kayitlar": kotu,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="OSTIM href filtresi olcumu")
    ap.add_argument("--dosya", default=str(VARSAYILAN), help="JSONL cikti dosyasi")
    ap.add_argument("--detay", type=int, default=10, help="ornek satir sayisi")
    a = ap.parse_args()

    r = olc(Path(a.dosya))
    print(f"dosya            : {r['dosya']}")
    print(f"satir            : {r['satir']}  (bozuk: {r['bozuk_satir']})")
    print(f"web_sitesi dolu  : {r['web_sitesi_dolu']}")
    print(f"YANLIS-POZITIF   : {r['yanlis_pozitif']}  (%{r['oran_yuzde']})")
    print(f"filtreyi gecen   : {r['filtreyi_gecen']}")
    print(f"bloklist girdisi : {r['bloklist_uzunluk']}")
    if r["tekil_gecen"]:
        print("gecen tekil adres:")
        for u in r["tekil_gecen"][: a.detay]:
            print(f"  {u}")
    if r["kotu_kayitlar"]:
        print("\n--- yanlis-pozitif ornekleri ---")
        for k in r["kotu_kayitlar"][: a.detay]:
            slug = k.get("slug") or k.get("firma_slug") or k.get("unvan") or "?"
            print(f"  {slug} | {k['web_sitesi']}")
        if len(r["kotu_kayitlar"]) > a.detay:
            print(f"  ... ve {len(r['kotu_kayitlar']) - a.detay} tane daha")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
