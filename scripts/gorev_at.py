# -*- coding: utf-8 -*-
"""ORCH-08 — Orkestratör görev atama komutu.

Kullanım (repo kökünden):
    python scripts/gorev_at.py at --task-id ORCH-09 --baslik "..." --ajan kilo \
        --oncelik P1 --dosya "src/a.py,docs/b.md" --talimat "..."
    python scripts/gorev_at.py pano

`at` görevi panoya ekler (dosyaları kilitler) ve ajana tetik düşürür.
Ajan `scripts/gorev_kutusu.py bak --ajan kilo` ile postasını görür.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.company_master.orchestrator import task_board as tb  # noqa: E402
from src.company_master.orchestrator import trigger  # noqa: E402


def _ayristir_liste(deger: str | None) -> list[str]:
    if not deger:
        return []
    return [p.strip() for p in deger.split(",") if p.strip()]


def cmd_at(args: argparse.Namespace) -> int:
    try:
        gorev = tb.gorev_ekle(
            task_id=args.task_id,
            baslik=args.baslik,
            sahip=args.ajan,
            oncelik=args.oncelik,
            dosyalar=_ayristir_liste(args.dosya),
        )
    except ValueError as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 1
    except PermissionError as exc:
        print(f"HATA (kilit): {exc}", file=sys.stderr)
        print("Dosya baska bir ajanin kilidinde; farkli kapsamla atayin.", file=sys.stderr)
        return 2
    tetik = trigger.tetik_ekle(args.task_id, args.ajan, args.talimat or "")
    print(f"ATANDI  : {gorev['task_id']} -> {args.ajan} ({gorev['oncelik']})")
    print(f"BASLIK  : {gorev['baslik']}")
    if gorev["dosyalar"]:
        print(f"KILITLI : {', '.join(gorev['dosyalar'])}")
    print(f"TETIK   : {args.ajan} postasina dusecek; ajan bakarsa gorur.")
    print(f"          python scripts/gorev_kutusu.py bak --ajan {args.ajan}")
    print(f"HAZIR   : Ajana gidip sadece 'başla' veya 'go' yazmanız yeterlidir (Kural dosyası postayı otomatik okur).")

    return 0


def cmd_pano(args: argparse.Namespace) -> int:
    ajanlar = sorted({t["sahip"] for t in tb.gorev_listesi()})
    print("== AJAN POSTALARI (bekleyen tetik) ==")
    herhangi_biri = False
    for ajan in ajanlar:
        bekleyen = trigger.bekleyen_tetikler(ajan)
        if bekleyen:
            herhangi_biri = True
            for k in bekleyen:
                print(f"  [{ajan}] {k['task_id']}  ({k['tarih']})")
    if not herhangi_biri:
        print("  (bos)")
    print("\n== ONAY KUYRUGU (kontrol bekleyen teslimler) ==")
    kuyruk = trigger.onay_bekleyenler()
    if not kuyruk:
        print("  (bos)")
    else:
        for k in kuyruk:
            print(f"  {k['task_id']}  <- {k['ajan']}  ({k['teslim_tarihi']})")
            print(f"    {k['ozet']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Orkestratör görev atama (ORCH-08)")
    alt = parser.add_subparsers(dest="komut", required=True)

    p_at = alt.add_parser("at", help="Panoya görev ekle + ajana tetik düşür")
    p_at.add_argument("--task-id", required=True)
    p_at.add_argument("--baslik", required=True)
    p_at.add_argument("--ajan", required=True, help="sahip + posta kutusu (ör. kilo)")
    p_at.add_argument("--oncelik", default="P1", choices=["P0", "P1", "P2"])
    p_at.add_argument("--dosya", default=None, help="Virgülle ayrılı, otomatik kilitlenir")
    p_at.add_argument("--talimat", default="", help="Ajana kısa talimat")
    p_at.set_defaults(func=cmd_at)

    p_pano = alt.add_parser("pano", help="Tetik + onay kuyruğu özetini göster")
    p_pano.set_defaults(func=cmd_pano)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
