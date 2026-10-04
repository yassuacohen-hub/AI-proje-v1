# -*- coding: utf-8 -*-
"""Firma türü + KVKK kapsam etiketlerini canlı DB'ye yaz.

Tek kapı: `company_master.etl.firma_turu`. Etiketleme mantığı burada
**yoktur**; burada yalnız ölçüm → yedek → toplu yazma yapılır (D-243/D-244).

Kullanım:
    python scripts/firma_turu_etiketle.py --dene     # prova (diske yazmaz)
    python scripts/firma_turu_etiketle.py --yaz      # gerçek yazma

D-243: `--dene` hiçbir şeyi diske yazmaz ve `backup_path` None döner.
D-244: gerçek yazma önce `yedekler/` altına kanıt dosyası bırakır; yedek
satır sayısı yazılacak satır sayısına eşit değilse iş `RuntimeError` ile
İPTAL olur.
D-249/2: yazma tek SQL ifadesidir. `executemany` toplu **gönderim**dir,
toplu yazma değildir.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402
from company_master.etl.firma_turu import (  # noqa: E402
    TURLER,
    firma_turu,
    kvkk_kapsaminda,
)

KOK = Path(__file__).resolve().parents[1]
YEDEK_DIZIN = KOK / "yedekler"

# Yazılacak kolonlar. `tax_number` OKUNUR, YAZILMAZ: yedek amaçlıdır ve
# yazılırsa şahıs işletmesi TC'yi kaybeder.
OKUNAN_KOLONLAR = ("company_id", "legal_name", "tax_number",
                   "company_type", "kvkk_kapsam")


def etiketle(rows) -> list[tuple]:
    """Satır listesini (company_id, company_type, kvkk_kapsam) üçlüsüne çevir."""
    return [
        (
            r["company_id"],
            firma_turu(r.get("legal_name")),
            bool(kvkk_kapsaminda(r)),
        )
        for r in rows
    ]


def yedek_yaz(rows, kuru: bool) -> Path | None:
    """Kanıt dosyası yaz. Kuru koşuda hiçbir şey yazılmaz (D-243)."""
    if kuru:
        return None
    YEDEK_DIZIN.mkdir(parents=True, exist_ok=True)
    damga = datetime.now().strftime("%Y%m%d_%H%M%S")
    yol = YEDEK_DIZIN / f"firma_turu_etiketle_{damga}.jsonl"
    with yol.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({
                "company_id": r["company_id"],
                "legal_name": r.get("legal_name"),
                "tax_number": r.get("tax_number"),
                "company_type_onceki": r.get("company_type"),
                "kvkk_kapsam_onceki": r.get("kvkk_kapsam"),
            }, ensure_ascii=False) + "\n")
    return yol


def calistir(kuru: bool) -> dict:
    motor = get_engine()
    with motor.connect() as c:
        rows = [dict(r._mapping) for r in c.execute(text(
            "SELECT company_id, legal_name, tax_number, company_type, "
            "kvkk_kapsam FROM public.companies"
        ))]
    etiketler = etiketle(rows)
    dagilim = Counter(t for _, t, _ in etiketler)
    bilinmeyen = set(dagilim) - set(TURLER)
    if bilinmeyen:
        raise RuntimeError(
            f"Sözlükte olmayan etiket üretildi: {sorted(bilinmeyen)}. "
            "TURLER güncellenmeden yazma yapılmaz (D-251/2)."
        )

    yedek = yedek_yaz(rows, kuru)
    if not kuru:
        # D-243/D-244: yedek kanıt değilse iş yazmaz.
        satir = sum(1 for _ in yedek.open(encoding="utf-8"))
        if satir != len(rows):
            raise RuntimeError(
                f"Yedek satır sayısı ({satir}) yazılacak satır sayısına "
                f"({len(rows)}) eşit değil — yazma iptal edildi."
            )

    # Tek SQL ifadesi (D-249/2). executemany değil.
    sql = text("""
        UPDATE public.companies c
           SET company_type = v.tur,
               kvkk_kapsam  = v.kvkk
          FROM (SELECT unnest(CAST(:ids AS uuid[])),
                       unnest(CAST(:turler AS text[])),
                       unnest(CAST(:kvkkler AS boolean[]))) AS v(cid, tur, kvkk)
         WHERE c.company_id = v.cid
    """)
    if kuru:
        return {"kuru": True, "satir": len(rows), "dagilim": dict(dagilim),
                "yedek": None}

    with motor.begin() as c:
        c.execute(sql, {
            "ids": [x[0] for x in etiketler],
            "turler": [x[1] for x in etiketler],
            "kvkkler": [x[2] for x in etiketler],
        })

    # Yazma sonrası doğrulama — beyan değil, ölçüm (D-260).
    with motor.connect() as c:
        sonra_tur = dict(c.execute(text(
            "SELECT company_type, count(*) FROM public.companies "
            "GROUP BY company_type")).fetchall())
        sonra_kvkk = c.execute(text(
            "SELECT count(*) FROM public.companies "
            "WHERE kvkk_kapsam IS TRUE")).scalar()
        bos = c.execute(text(
            "SELECT count(*) FROM public.companies "
            "WHERE company_type IS NULL")).scalar()
    return {
        "kuru": False,
        "satir": len(rows),
        "dagilim": dict(dagilim),
        "yedek": str(yedek.relative_to(KOK)),
        "sonra_dagilim": sonra_tur,
        "sonra_kvkk_true": sonra_kvkk,
        "sonra_bos_tur": bos,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    kip = ap.add_mutually_exclusive_group(required=True)
    kip.add_argument("--dene", action="store_true", help="prova (diske yazmaz)")
    kip.add_argument("--yaz", action="store_true", help="gerçek yazma")
    a = ap.parse_args()

    sonuc = calistir(kuru=a.dene)
    print("=" * 64)
    print("KIP          :", "PROVA (diske yazilmadi)" if a.dene else "YAZMA")
    print("ISLENEN SATIR:", sonuc["satir"])
    print("-" * 64)
    for etiket in TURLER:
        n = sonuc["dagilim"].get(etiket, 0)
        print(f"  {etiket:<24} {n:>6}  {100*n/sonuc['satir']:>5.1f}%")
    print("-" * 64)
    if sonuc["kuru"]:
        print("Yedek        : None (prova kipi diske yazmaz - D-243)")
    else:
        print("Yedek        :", sonuc["yedek"])
        print("Sonra dagilim:", sonuc["sonra_dagilim"])
        print("kvkk_kapsam TRUE:", sonuc["sonra_kvkk_true"])
        print("company_type NULL:", sonuc["sonra_bos_tur"])
    print("=" * 64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
