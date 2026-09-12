# -*- coding: utf-8 -*-
"""ORCH-08 — Ajan posta kutusu + kontrolör onay komutu.

AJAN tarafı (oturum başında çalıştır):
    python scripts/gorev_kutusu.py bak --ajan kilo          # bekleyen işler
    python scripts/gorev_kutusu.py al --ajan kilo --task-id X
    python scripts/gorev_kutusu.py teslim --ajan kilo --task-id X --ozet "..."

KONTROLÖR tarafı (orkestratör; onaysız done geçersizdir):
    python scripts/gorev_kutusu.py onay-bekleyen
    python scripts/gorev_kutusu.py onayla --task-id X --ben orkestrator
    python scripts/gorev_kutusu.py reddet --task-id X --ben orkestrator --neden "..."
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


def _hata(exc: Exception) -> int:
    print(f"HATA: {exc}", file=sys.stderr)
    return 1


def cmd_bak(args: argparse.Namespace) -> int:
    bekleyen = trigger.bekleyen_tetikler(args.ajan)
    if not bekleyen:
        print(f"[{args.ajan}] posta kutusu bos.")
        return 0
    print(f"[{args.ajan}] {len(bekleyen)} bekleyen gorev:")
    for k in bekleyen:
        gorev = tb.gorev_getir(k["task_id"]) or {}
        print(f"\n  {k['task_id']}  ({gorev.get('oncelik', '?')})  tetik: {k['tarih']}")
        print(f"  {gorev.get('baslik', '(pano basligi yok)')}")
        if k.get("talimat"):
            print(f"  TALIMAT: {k['talimat']}")
        if gorev.get("dosyalar"):
            print(f"  KILITLI DOSYALAR: {', '.join(gorev['dosyalar'])}")
        print(f"  -> al: python scripts/gorev_kutusu.py al --ajan {args.ajan} --task-id {k['task_id']}")
    return 0


def cmd_al(args: argparse.Namespace) -> int:
    try:
        sonuc = trigger.tetik_al(args.ajan, args.task_id)
    except trigger.TriggerError as exc:
        return _hata(exc)
    print(f"ALINDI: {sonuc['task_id']} -> {args.ajan} (durum: aktif)")
    return 0


def cmd_teslim(args: argparse.Namespace) -> int:
    try:
        sonuc = trigger.teslim_et(
            args.task_id, args.ajan, args.ozet, _ayristir_liste(args.cikti)
        )
    except trigger.TriggerError as exc:
        return _hata(exc)
    print(f"TESLIM: {sonuc['task_id']} -> durum: review (onay bekliyor)")
    print("       Onaysiz done OLMAZ; kontrolor onayi sonrasi tamamlanir.")
    return 0


def cmd_onay_bekleyen(args: argparse.Namespace) -> int:
    kuyruk = trigger.onay_bekleyenler()
    if not kuyruk:
        print("Onay kuyrugu bos.")
        return 0
    print(f"{len(kuyruk)} teslim kontrol bekliyor:")
    for k in kuyruk:
        print(f"\n  {k['task_id']}  <- {k['ajan']}  ({k['teslim_tarihi']})")
        print(f"  OZET: {k['ozet']}")
        if k.get("ciktilar"):
            print(f"  CIKTILAR: {', '.join(k['ciktilar'])}")
        print(f"  -> python scripts/gorev_kutusu.py onayla --task-id {k['task_id']} --ben orkestrator")
    return 0


def cmd_onayla(args: argparse.Namespace) -> int:
    try:
        trigger.onayla(args.task_id, args.ben)
    except trigger.TriggerError as exc:
        return _hata(exc)
    print(f"ONAYLANDI: {args.task_id} -> done (kilitler otomatik dustu)")
    return 0


def cmd_reddet(args: argparse.Namespace) -> int:
    try:
        trigger.reddet(args.task_id, args.ben, args.neden)
    except trigger.TriggerError as exc:
        return _hata(exc)
    print(f"REDDEDILDI: {args.task_id} -> aktif (ajan duzeltmeye devam edecek)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Ajan posta kutusu + onay (ORCH-08)")
    alt = parser.add_subparsers(dest="komut", required=True)

    def ajanli(p: argparse.ArgumentParser) -> None:
        p.add_argument("--ajan", required=True)

    p = alt.add_parser("bak", help="Bekleyen görevlerini listele"); ajanli(p)
    p.set_defaults(func=cmd_bak)
    p = alt.add_parser("al", help="Görevi al (aktif yap)"); ajanli(p)
    p.add_argument("--task-id", required=True); p.set_defaults(func=cmd_al)
    p = alt.add_parser("teslim", help="İşi teslim et (review'a düşer)"); ajanli(p)
    p.add_argument("--task-id", required=True); p.add_argument("--ozet", required=True)
    p.add_argument("--cikti", default=None, help="Virgülle ayrılı çıktı dosyaları")
    p.set_defaults(func=cmd_teslim)
    p = alt.add_parser("onay-bekleyen", help="Onay bekleyen teslimleri listele")
    p.set_defaults(func=cmd_onay_bekleyen)
    p = alt.add_parser("onayla", help="Teslimi onayla (done)")
    p.add_argument("--task-id", required=True); p.add_argument("--ben", required=True)
    p.set_defaults(func=cmd_onayla)
    p = alt.add_parser("reddet", help="Teslimi reddet (aktife geri)")
    p.add_argument("--task-id", required=True); p.add_argument("--ben", required=True)
    p.add_argument("--neden", required=True); p.set_defaults(func=cmd_reddet)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
