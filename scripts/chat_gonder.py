# -*- coding: utf-8 -*-
"""D-210 — Ajan chat: mesaj gonder.

Kullanim:
    python scripts/chat_gonder.py --to utku --type hata --task-id UI-ADMIN-26 --mesaj "..."
    python scripts/chat_gonder.py --to ihsan --type koordinasyon --task-id T-1 --mesaj "..."

Mesaj `data/orchestrator/chat/messages.jsonl` dosyasina tek satir JSON olarak
eklenir (append-only). Satir semasi D-210 "Chat Log Konumu" bolumuyle aynidir:

    {"tarih": "...", "kimden": "...", "kime": "...", "type": "...",
     "task_id": "...", "mesaj": "...", "yanit_alindi": false}

Gonderen belirtilmezse `--kimden` → `HUGINN_AJAN` env sirasina bakar.
Ikisi de bos ise HATA verir (D-306): gonderen ajan baska birinin adina
yazilirsa alici mesaji kendi mesaji sanip cevap vermez.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

_KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_KOK))
sys.path.insert(0, str(_KOK / "src"))

# Windows konsolu (cp1254) Turkce karakterlerde cokmesin (gorev_kutusu.py ile ayni desen).
for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover - eski Python / yonlendirilmis akis
        pass

from src.company_master.orchestrator import task_board as tb  # noqa: E402
from src.company_master.orchestrator import trigger  # noqa: E402

#: D-303: projenin TEK kimlik kaynagi. `HUGINN_AJAN` > `git config huginn.ajan`
#: > `git config user.name` icinde gecen bilinen ajan.
#:
#: D-306: bu script KENDI kimlik zincirini kurmamalidir. Once kurdugu
#: zincir `--kimden` -> HUGINN_AJAN -> "ihsan" idi; HUGINN_AJAN tanimli
#: olmadigi icin yasu'nun mesajlari "ihsan -> ihsan" olarak dustu ve
#: orkestrator bunlari kendi mesaji sanip cevap vermedi (11 kayit).
#: Tek kaynak: scripts/kilit_zorla.ajan_kimligi()
sys.path.insert(0, str(_KOK / "scripts"))
from ajan_kimligi import ajan_kimligi  # noqa: E402

#: D-210 "Zorunlu Chat Turleri" — kabul edilen mesaj tipleri.
#: "yorum" (Mesaj 6 · liderlik+yorum tasarimi, 2026-10-03): bir mesaja
#: ekli yanit; `cevap_index` alaniyla hedef mesaji isaretler.
MESAJ_TIPLERI: tuple[str, ...] = ("hata", "soru", "koordinasyon", "rapor", "bilgi", "yorum")

#: Tum ajanlara yayin icin kullanilan alici takma adlari.
YAYIN_ALICI: tuple[str, ...] = ("hepsi", "tum", "tüm", "all")

#: D-210 mesaj govdesi ust siniri (token ve okunabilirlik siniri).
MESAJ_MAX = 1000


#: D-306 — Kim oldugunu bilmeyen ajan mesajini KENDI ADINA yazamaz.
#:
#: Bu esik daha once gercek bir hataya yol acti: `HUGINN_AJAN` tanimli
#: degilken `chat_gonder.py` varsayilan olarak `ihsan` yaziyordu; boylece
#: yasu'nun mesajlari log'a "ihsan -> ihsan" olarak dustu ve orkestrator
#: bunlari kendi mesaji sanip CEVAP VERMIYORDU (11 kayit).
#:
#: Duzeltme: gonderen belirtilmezse HATA verilir. Orkestrator kimligi
#: `ihsan` DEGIL, gonderen ajanin kendisidir (D-70: orkestrator *rol*,
#: gonderen *ajandir*; ikisi karistirilamaz).
_BOS_KIMDEN_UYARI = (
    "gonderen ajan belirtilmedi. --kimden <ajan> verin veya "
    "HUGINN_AJAN ortam degiskenini tanimlayin. "
    "Bos birakilirsa mesaj yanlis adla log'a yazilir."
)

#: Gercekten gonderen ajan olabilecek kanonik adlar.
GONDEREN_ADAY = frozenset({"yasu", "ihsan", "utku", "salih", "mimir", "mimar"})


def chat_yolu() -> Path:
    """Chat log dosyasinin tam yolu (D-210)."""
    return tb.STATE_DIR / "chat" / "messages.jsonl"


def _alici_normalize(alici: str) -> str:
    """Aliciyi kanonik ajana cevir; yayin takma adlarini oldugu gibi dondur."""
    ham = (alici or "").strip().lower()
    if ham in YAYIN_ALICI:
        return "hepsi"
    return trigger.ajan_normalize(ham)


def gonder(
    kime: str,
    tip: str,
    mesaj: str,
    task_id: str = "",
    kimden: str | None = None,
    cevap_index: int | None = None,
) -> dict:
    """Tek chat satiri yaz ve yazilan kaydi dondur.

    Kimlik sirasi (D-303 TEK KAYNAK -> scripts/ajan_kimligi.py):
        --kimden  >  HUGINN_AJAN  >  ajan_<ad>.json  >  git config
        huginn.ajan  >  git user.name
    Cozulemezse veya belirsizse HATA verilir: gonderen ajan baska birinin
    adina yazilirsa alici mesaji kendi mesaji sanip cevap vermez (D-306).
    """
    # --kimden acikca verildiyse kimlik zinciri CALISMAZ (docstring sirasi).
    # Aksi halde 3 ajan_<ad>.json olan makinede (ihsan/orkestrator) her
    # mesaj "kimlik cozulemedi" ile duser — 2026-10-03 D-335 yayininda olctu.
    ham_kimden = (kimden or "").strip()
    if not ham_kimden:
        try:
            ham_kimden = (ajan_kimligi() or "").strip()
        except Exception as exc:                 # KimlikBelirsiz dahil
            raise ValueError(f"kimlik cozulemedi: {exc}") from exc
    if not ham_kimden:
        raise ValueError(_BOS_KIMDEN_UYARI)
    g_ajan = trigger.ajan_normalize(ham_kimden)
    if g_ajan not in GONDEREN_ADAY:
        raise ValueError(
            f"gecersiz gonderen: {kimden!r} — izinli: {', '.join(sorted(GONDEREN_ADAY))}"
        )
    h_ajan = _alici_normalize(kime)
    tip = (tip or "").strip().lower()
    metin = (mesaj or "").strip()

    if tip not in MESAJ_TIPLERI:
        raise ValueError(f"gecersiz tip: {tip!r} — izinli: {', '.join(MESAJ_TIPLERI)}")
    if not metin:
        raise ValueError("mesaj bos olamaz")
    if len(metin) > MESAJ_MAX:
        raise ValueError(f"mesaj cok uzun ({len(metin)} > {MESAJ_MAX})")
    if h_ajan not in YAYIN_ALICI:
        if h_ajan not in trigger.AJANLAR:
            raise ValueError(
                f"gecersiz alici: {kime!r} — izinli: {', '.join(trigger.AJANLAR)} (veya hepsi)"
            )

    kayit = {
        "tarih": datetime.now().isoformat(timespec="seconds"),
        "kimden": g_ajan,
        "kime": h_ajan,
        "type": tip,
        "task_id": (task_id or "").strip(),
        "mesaj": metin,
        "yanit_alindi": False,
    }
    if cevap_index is not None:
        kayit["cevap_index"] = cevap_index

    yol = chat_yolu()
    yol.parent.mkdir(parents=True, exist_ok=True)
    with yol.open("a", encoding="utf-8") as f:
        f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
    return kayit


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="chat_gonder",
        description="D-210: ajanlararasi chat mesaji gonder (append-only JSONL)",
    )
    ap.add_argument("--to", "-t", required=True, help="Alici ajan (ihsan/utku/salih/yasu/hepsi)")
    ap.add_argument(
        "--type", "-y", required=True, choices=MESAJ_TIPLERI,
        help="Mesaj tipi (D-210 zorunlu chat turleri)",
    )
    ap.add_argument("--mesaj", "-m", required=True, help="Mesaj metni (max %d karakter)" % MESAJ_MAX)
    ap.add_argument("--task-id", "-i", default="", help="Ilgili gorev kimligi (opsiyonel)")
    ap.add_argument(
        "--kimden", "-k", default="",
        help="Gonderen ajan (ZORUNLU: --kimden veya HUGINN_AJAN; bos birakilamaz)",
    )
    args = ap.parse_args(argv)

    try:
        kayit = gonder(
            kime=args.to,
            tip=args.type,
            mesaj=args.mesaj,
            task_id=args.task_id,
            kimden=args.kimden or None,
        )
    except ValueError as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 1

    hedef = "" if not kayit["task_id"] else f" [{kayit['task_id']}]"
    print(
        f"GONDERILDI: {kayit['kimden']} -> {kayit['kime']} "
        f"({kayit['type']}){hedef} {kayit['tarih']}"
    )
    print(f"  log: {chat_yolu().relative_to(_KOK).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
