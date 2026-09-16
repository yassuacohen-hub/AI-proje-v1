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
from datetime import datetime
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


def _kisa_tarih(iso: str | None) -> str:
    """ISO tarihi 'MM-DD HH:MM' formatina kisalir; parse edilemezse ilk 16 karakter."""
    if not iso:
        return "-"
    try:
        return datetime.fromisoformat(str(iso)).strftime("%m-%d %H:%M")
    except ValueError:
        return str(iso)[:16]


def _gorev_basligi(task_id: str | None) -> str:
    """Panodan gorev basligini getirir; gorev bulunamazsa '-'."""
    if not task_id:
        return "-"
    try:
        gorev = tb.gorev_getir(str(task_id))
    except Exception:  # noqa: BLE001 - pano ciktisi hata yuzunden cokmemeli
        return "-"
    if not gorev:
        return "-"
    return str(gorev.get("baslik") or "-")


def _kisalt(metin: str | None, limit: int) -> str:
    """Metni limit uzunlugunda keser; mumkunse kelime sinirinda keser, '…' ekler."""
    metin = (metin or "").strip()
    if len(metin) <= limit:
        return metin
    kirpik = metin[: limit - 1]
    bosluk = kirpik.rfind(" ")
    if bosluk > limit // 2:  # kelime siniri varsa orada kes
        kirpik = kirpik[:bosluk]
    return kirpik.rstrip() + "…"


def cmd_pano(args: argparse.Namespace) -> int:
    ajanlar = sorted({str(t.get("sahip") or "?") for t in tb.gorev_listesi()})
    print("== AJAN POSTALARI (bekleyen tetik) ==")
    herhangi_biri = False
    for ajan in ajanlar:
        bekleyen = trigger.bekleyen_tetikler(ajan)
        if bekleyen:
            herhangi_biri = True
            for k in bekleyen:
                task_id = str(k.get("task_id") or "?")
                baslik = _kisalt(_gorev_basligi(task_id), 28)
                print(
                    f"  [{ajan:<14}] {task_id:<10} "
                    f"({_kisa_tarih(k.get('tarih'))})  {baslik}"
                )
    if not herhangi_biri:
        print("  (bos)")
    print("\n== ONAY KUYRUGU (kontrol bekleyen teslimler) ==")
    kuyruk = trigger.onay_bekleyenler()
    if not kuyruk:
        print("  (bos)")
    else:
        for k in kuyruk:
            task_id = str(k.get("task_id") or "?")
            ajan = str(k.get("ajan") or "?")
            baslik = _kisalt(_gorev_basligi(task_id), 28)
            print(
                f"  {task_id:<10} <- {ajan:<14} "
                f"({_kisa_tarih(k.get('teslim_tarihi'))})  {baslik}"
            )
            print(f"    {_kisalt(k.get('ozet'), 50)}")
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
    # D-33 ajan adı kuralı: "Ajan kilo" / "Kilo" / "kilo_code" → "kilo".
    if getattr(args, "ajan", None):
        try:
            args.ajan = trigger.ajan_normalize(args.ajan)
        except trigger.TriggerError as exc:
            print(f"HATA: {exc}")
            return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
