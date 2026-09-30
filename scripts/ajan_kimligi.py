# -*- coding: utf-8 -*-
"""Ajan kimligi: TEK kaynak (D-306 duzeltmesi).

NEDEN AYRI BIR DOSYA?
    `git config huginn.ajan` PAYLASILAN `.git/config`e yazar. Ayni repoda
    uc ajan ayni anda calistiginda (olculdu: utku 1, ihsan 1, yasu 4 kilit)
    ucunun degeri de `yasu` olur ve HATA butun ajanlara yayilir - ayni
    hatayi bu kez komsudan almis oluruz.

    `.env` de paylasilandir. Ona da yazilamaz.

COZUM: ajan basina ayri dosya (`data/orchestrator/ajan_<ad>.json`). Her ajan
kendi dosyasini okur; paylasim yoktur, cakisma olmaz.

COZULEMEZSE: hata verilir. Mesaj yanlis adla yazilirsa alici kendi mesaji
sanip cevap vermez ve bildirim sessizce kaybolur (D-306).
"""
from __future__ import annotations

import json
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
#: D-303: kilit sistemiyle ayni kanonik ajan listesi + orchestrator.
AJANLAR: frozenset[str] = frozenset(
    {"yasu", "utku", "ihsan", "salih", "mimir", "mimar", "orkestrator"}
)

#: Kimlik dosyalarinin tutuldugu dizin.
DIZIN = KOK / "data" / "orchestrator" / "ajanlar"


def _oku(ad: str) -> str | None:
    """`ajan_<ad>.json` icindeki kimligi dondur."""
    yol = DIZIN / f"ajan_{ad}.json"
    if not yol.is_file():
        return None
    try:
        veri = json.loads(yol.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    kimlik = (veri.get("ajan") or "").strip().lower()
    return kimlik or None


def _tanimli(ad: str) -> bool:
    """Bu makinede `ad` icin kimlik dosyasi var mi?"""
    yol = DIZIN / f"ajan_{ad}.json"
    if not yol.is_file():
        return False
    try:
        veri = json.loads(yol.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return bool((veri.get("ajan") or "").strip())


def ajan_kimligi() -> str | None:
    """Bu makinenin ajan kimligi (cozulemezse None).

    Sirasiyla bakar:
        1. ``HUGINN_AJAN`` ortam degiskeni
        2. ``data/orchestrator/ajanlar/ajan_<ad>.json`` dosyalari
        3. ``git config huginn.ajan``  (paylasilan; TEK ajan varsa yeterli)
        4. ``git config user.name`` icinde gecen bilinen ajan adi
    """
    import os
    import subprocess

    if ad := (os.environ.get("HUGINN_AJAN") or "").strip().lower():
        return ad

    # 2) Ajan basina dosya: bu makinede KAC ajan tanimli?
    tanimli = [a for a in sorted(AJANLAR) if _tanimli(a)]
    if len(tanimli) == 1:
        return tanimli[0]
    if len(tanimli) > 1:
        # Birden fazla ajan bu makinede tanimli -> karisik. Hata verilmeli.
        raise KimlikBelirsiz(
            f"bu makinede {len(tanimli)} ajan tanimli: {', '.join(tanimli)}. "
            f"HUGINN_AJAN ile belirtin veya ajan_<ad>.json dosyalarini "
            f"tek taneye indirin."
        )

    def git(*a: str) -> str:
        try:
            cp = subprocess.run(["git", *a], cwd=KOK, capture_output=True,
                                text=True, errors="replace", timeout=10)
            return cp.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return ""

    if ad := git("config", "huginn.ajan").strip().lower():
        return ad
    ad = git("config", "user.name").lower()
    return next((a for a in AJANLAR if a in ad), None)


class KimlikBelirsiz(RuntimeError):
    """Kimlik tek satira cozulemiyor (birden fazla ajan ayni makinede)."""


def kimligi_yaz(ajan: str) -> Path:
    """Bu makine icin ajan kimligini kalici yaz (kurutma komutu)."""
    ad = (ajan or "").strip().lower()
    if ad not in AJANLAR:
        raise ValueError(f"gecersiz ajan: {ajan!r} — izinli: {', '.join(sorted(AJANLAR))}")
    DIZIN.mkdir(parents=True, exist_ok=True)
    yol = DIZIN / f"ajan_{ad}.json"
    yol.write_text(
        json.dumps({"ajan": ad, "kaynak": "ajan_kimligi.py",
                    "not": "bu makinede calisan ajan; paylasmaz"},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return yol


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] != "--goster":
        y = kimligi_yaz(sys.argv[1])
        print(f"KIMLIK YAZILDI: {y} -> ajan={sys.argv[1]}")
    else:
        k = ajan_kimligi()
        print("ajan_kimligi() =", repr(k))
