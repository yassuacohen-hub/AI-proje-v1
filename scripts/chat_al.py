# -*- coding: utf-8 -*-
"""D-210 — Ajan chat: mesaj oku / ozetle / yanitla.

Kullanim:
    python scripts/chat_al.py --ajan utku --limit 20
    python scripts/chat_al.py --ajan utku --ozet gun
    python scripts/chat_al.py --ajan utku --yanitla 1

Kaynak: `data/orchestrator/chat/messages.jsonl` (append-only; `chat_gonder.py`
yazar). SLA esikleri D-210 "Kural Ozeti" bolumunden gelir:
P0 → 10 dk, P1 → 15 dk, P2 → 30 dk. Cevaplanmamis ve SLA'i asan mesaj
`SLA ASIMI` etiketiyle isaretlenir.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

_KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_KOK))
sys.path.insert(0, str(_KOK / "src"))

for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover
        pass

from src.company_master.orchestrator import task_board as tb  # noqa: E402
from src.company_master.orchestrator import trigger  # noqa: E402

#: D-210 cevap SLA'i (dakika) — gorev onceligine gore.
SLA_DK: dict[str, int] = {"P0": 10, "P1": 15, "P2": 30}
SLA_VARSAYILAN = 30

YAYIN = "hepsi"


def chat_yolu() -> Path:
    """Chat log dosyasinin tam yolu (D-210)."""
    return tb.STATE_DIR / "chat" / "messages.jsonl"


def _satirlari_yukle() -> list[dict]:
    """JSONL'i okur; bozuk satiri sessizce atlar (tek bozuk satir her seyi dusurmesin)."""
    yol = chat_yolu()
    if not yol.exists():
        return []
    kayitlar: list[dict] = []
    for no, satir in enumerate(yol.read_text(encoding="utf-8").splitlines(), start=1):
        satir = satir.strip()
        if not satir:
            continue
        try:
            kayit = json.loads(satir)
        except json.JSONDecodeError:
            continue
        if isinstance(kayit, dict):
            kayit["_satir"] = no
            kayitlar.append(kayit)
    return kayitlar


def _bana_gelenler(ajan: str) -> list[dict]:
    """Ajana gelen (dogrudan veya yayin) mesajlar; gonderilme sirasi korunur."""
    hedef = trigger.ajan_normalize(ajan)
    return [k for k in _satirlari_yukle() if k.get("kime") in (hedef, YAYIN)]


def _sla_dk(task_id: str) -> int:
    """Gorev onceligine gore SLA dakikasi (pano yoksa varsayilan)."""
    gorev = tb.gorev_getir(task_id) if task_id else None
    return SLA_DK.get((gorev or {}).get("oncelik", ""), SLA_VARSAYILAN)


def _sla_asildi(kayit: dict) -> bool:
    """Cevaplanmamis mesaj SLA'i asti mi?"""
    if kayit.get("yanit_alindi"):
        return False
    try:
        yas = (datetime.now() - datetime.fromisoformat(str(kayit.get("tarih")))).total_seconds() / 60
    except (TypeError, ValueError):
        return False
    return yas > _sla_dk(str(kayit.get("task_id") or ""))


def _yaz(kayit: dict, sira: int) -> None:
    tip = str(kayit.get("type", "?"))
    task = str(kayit.get("task_id") or "")
    etiket = f" [{task}]" if task else ""
    durum = "cevaplandi" if kayit.get("yanit_alindi") else "acik"
    uyari = "  ** SLA ASIMI **" if _sla_asildi(kayit) else ""
    print(f"\n  {sira}. {kayit.get('tarih', '?')}  {tip}{etiket}  ({durum}){uyari}")
    print(f"     {kayit.get('kimden', '?')} -> {kayit.get('kime', '?')}")
    print(f"     {kayit.get('mesaj', '')}")


def cmd_oku(ajan: str, limit: int | None, sadece_acik: bool) -> int:
    kayitlar = _bana_gelenler(ajan)
    if sadece_acik:
        kayitlar = [k for k in kayitlar if not k.get("yanit_alindi")]
    if limit:
        kayitlar = kayitlar[-limit:]
    if not kayitlar:
        print(f"[{trigger.ajan_goster(trigger.ajan_normalize(ajan))}] gelen kutusu bos.")
        return 0
    print(f"[{trigger.ajan_goster(trigger.ajan_normalize(ajan))}] {len(kayitlar)} mesaj:")
    for sira, kayit in enumerate(kayitlar, start=1):
        _yaz(kayit, sira)
    return 0


def cmd_ozet(ajan: str, kip: str) -> int:
    kayitlar = _bana_gelenler(ajan)
    bugun = datetime.now().date().isoformat()
    if kip == "gun":
        kayitlar = [k for k in kayitlar if str(k.get("tarih", "")).startswith(bugun)]
    elif kip == "acik":
        kayitlar = [k for k in kayitlar if not k.get("yanit_alindi")]

    if not kayitlar:
        print(f"Ozet ({kip}): kayit yok.")
        return 0

    tipler: dict[str, int] = {}
    gecikmis = 0
    for kayit in kayitlar:
        tip = str(kayit.get("type", "?"))
        tipler[tip] = tipler.get(tip, 0) + 1
        gecikmis += 1 if _sla_asildi(kayit) else 0

    print(f"Ozet ({kip}) — {len(kayitlar)} mesaj")
    for tip, adet in sorted(tipler.items()):
        print(f"  {tip}: {adet}")
    print(f"  SLA asimi: {gecikmis}")
    for sira, kayit in enumerate(kayitlar[-10:], start=1):
        _yaz(kayit, sira)
    return 0


def cmd_yanitla(ajan: str, sira: int) -> int:
    """Listelenen N. gelen mesaji `yanit_alindi=true` yapar (dosya yeniden yazilir)."""
    hedef = trigger.ajan_normalize(ajan)
    tum = _satirlari_yukle()
    gelenler = [k for k in tum if k.get("kime") in (hedef, YAYIN)]
    if sira < 1 or sira > len(gelenler):
        print(f"HATA: {sira} numarali mesaj yok (toplam {len(gelenler)}).", file=sys.stderr)
        return 1
    hedef_kayit = gelenler[sira - 1]
    for kayit in tum:
        if kayit.get("_satir") == hedef_kayit.get("_satir"):
            kayit["yanit_alindi"] = True
    yol = chat_yolu()
    with yol.open("w", encoding="utf-8") as f:
        for kayit in tum:
            temiz = {k: v for k, v in kayit.items() if k != "_satir"}
            f.write(json.dumps(temiz, ensure_ascii=False) + "\n")
    print(f"YANITLANDI: {hedef} <- {hedef_kayit.get('kimden')} ({hedef_kayit.get('type')})")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="chat_al",
        description="D-210: ajan chat mesajlarini oku / ozetle / yanitla",
    )
    ap.add_argument("--ajan", "-a", required=True, help="Posta sahibi ajan (ihsan/utku/salih/yasu)")
    ap.add_argument("--limit", "-l", type=int, default=None, help="Son N mesaji goster")
    ap.add_argument("--sadece-acik", action="store_true", help="Yalniz cevaplanmamis mesajlar")
    ap.add_argument("--ozet", choices=["gun", "acik", "hepsi"], help="Ozet kipi")
    ap.add_argument("--yanitla", type=int, metavar="N", help="N. gelen mesaji cevaplandi isaretle")
    args = ap.parse_args(argv)

    if trigger.ajan_normalize(args.ajan) not in trigger.AJANLAR:
        print(
            f"HATA: gecersiz ajan: {args.ajan!r} — izinli: {', '.join(trigger.AJANLAR)}",
            file=sys.stderr,
        )
        return 1

    if args.yanitla:
        return cmd_yanitla(args.ajan, args.yanitla)
    if args.ozet:
        return cmd_ozet(args.ajan, args.ozet)
    return cmd_oku(args.ajan, args.limit, args.sadece_acik)


if __name__ == "__main__":
    sys.exit(main())

