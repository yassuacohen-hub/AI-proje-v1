"""D-291: Tarama ciktisinda MUKERRER kayit denetimi ve isaretleme.

KAHIN 2026-09-29: "yanlis mukerer kayit olmasin".

OLCUM (ilk 500'lik parca, canli):
  * slug tekrari        : 0
  * unvan tekrari       : 2
  * K-2 kirp            : 0
  * kaynak SHA degisimi : 0

Unvan tekrarlari GOZDEN GECIRILDI: bunlar sitede AYRI slug olarak
listelenen AYNI firmalar (orn. `...-tik` ve `...-tik-2`). Bizim
hatamiz DEGIL; ama ayni unvan iki satirda duruyorsa tekillestirme
sirasinda tek kayda indirilmelidir.

Bu arac:
  1. ayni normalize unvana sahip gruplari bulur
  2. ayni telefon/adres olanlari MUKERRER (birlesik) isaretler
  3. farkli adresi olanlari AYRI_KAYIT (korunur) isaretler
  4. kaynak dosyaya DOKUNMAZ; karar listesini raporlar

Kullanim: python scripts/ostim_mukerrer_denetimi.py
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import defaultdict
from datetime import datetime

KOK = pathlib.Path(__file__).resolve().parents[1]
KAZANIM = KOK / "data" / "ostim" / "tamamlama_2026-09-29"
GIRIS = KAZANIM / "firmalar_tamamlanmis.jsonl"
CIKTI = KAZANIM / "mukerrer_raporu.json"


def norm_unvan(u: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (u or "").upper())


def norm_telefon(t: str) -> str:
    return re.sub(r"\D", "", str(t or ""))[-9:]


def norm_adres(a: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (a or "").upper())


def main() -> int:
    if not GIRIS.is_file():
        print(f"HATA: {GIRIS} yok")
        return 1
    sat = [json.loads(x) for x in GIRIS.read_text(
        encoding="utf-8").splitlines() if x.strip()]

    gruplar: dict[str, list[dict]] = defaultdict(list)
    for s in sat:
        gruplar[norm_unvan(s.get("unvan"))].append(s)

    tekrar = {k: v for k, v in gruplar.items() if k and len(v) > 1}
    birlestir = []
    ayri_kayit = []
    for anahtar, grup in tekrar.items():
        adr = {norm_adres(g.get("adres")) for g in grup if g.get("adres")}
        tel = set()
        for g in grup:
            tel |= {norm_telefon(t) for t in (g.get("telefonler") or [])}
        # Ayni unvan + ayni telefon = kesin ayni kayit
        ayni = len(adr) <= 1 and len(tel) <= 1
        kayit = {
            "unvan": grup[0].get("unvan"),
            "adet": len(grup),
            "sluglar": [g.get("slug") for g in grup],
            "adresler": [g.get("adres") for g in grup],
            "telefonlar": sorted(x for x in tel if x),
            "karar": "MUKERRER (tek kayda indirilebilir)" if ayni
                     else "AYRI_KAYIT (ayri isletme olabilir — KORU)",
        }
        (birlestir if ayni else ayri_kayit).append(kayit)

    rapor = {
        "zaman": datetime.now().isoformat(timespec="seconds"),
        "kayit": len(sat),
        "tekil_slug": len({s.get("slug") for s in sat}),
        "mukerrer_slug": len(sat) - len({s.get("slug") for s in sat}),
        "tekil_unvan": len(gruplar),
        "mukerrer_unvan_grubu": len(tekrar),
        "birlestirilebilir": len(birlestir),
        "ayri_korunacak": len(ayri_kayit),
        "detay_birlestir": birlestir,
        "detay_ayri": ayri_kayit,
        "not": ("Kaynak dosyalara DOKUNULMADI. Bu bir denetim raporudur; "
                "tekillestirme karari ayrica verilir."),
    }
    CIKTI.write_text(json.dumps(rapor, ensure_ascii=False, indent=2),
                     encoding="utf-8")

    print(f"KAYIT            : {rapor['kayit']}")
    print(f"TEKIL SLUG       : {rapor['tekil_slug']} "
          f"(mukerrer {rapor['mukerrer_slug']})")
    print(f"TEKIL UNVAN      : {rapor['tekil_unvan']}")
    print(f"MUKERRER GRUP    : {rapor['mukerrer_unvan_grubu']}")
    print(f"  -> birlestir  : {rapor['birlestirilebilir']}")
    print(f"  -> ayri korun : {rapor['ayri_korunacak']}")
    for k in rapor["detay_birlestir"][:5]:
        print(f"   [BIRL] {k['unvan'][:52]} ({k['adet']} kayit)")
    for k in rapor["detay_ayri"][:5]:
        print(f"   [AYRI ] {k['unvan'][:52]} ({k['adet']} kayit)")
    print(f"\n{CIKTI}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
