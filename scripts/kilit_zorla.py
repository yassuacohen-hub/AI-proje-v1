# -*- coding: utf-8 -*-
"""Commit aninda dosya kilidini ZORLAR (beyan degil, kapi).

`data/orchestrator/file_locks.json` D-281'e kadar yalnizca *kaydediliyordu*;
okuyan 48 yer vardi, **zorlayan yoktu** (D-261: zorlayani olmayan kayit beyandir).
Bu betik `scripts/hooks/pre-commit`ten cagrilir: staged dosya baskasinin
kilidindeyse commit durur.

Kimlik sirasi: `HUGINN_AJAN` > `git config huginn.ajan` > `user.name` icinde gecen
bilinen ajan. D-303: bu fonksiyon projedeki TEK kimlik kaynagidir; `karar_no.py`
de buradan okur (once iki ayri zincir vardi, D-301 iki ajana ayni anda verildi).
ponytail: kimlik cozulemezse UYARIR ve gecer — ucu birden bloke etmemek icin.
Yukseltme: her ajan `git config huginn.ajan <ad>` kurdugunda burasi `return 1` olur.

    python scripts/kilit_zorla.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
# D-243: yikici/durduran isin yolu enjekte edilebilir olur (prova canliya dokunmaz)
KILIT = Path(os.environ.get("HUGINN_KILIT_YOL")
             or KOK / "data" / "orchestrator" / "file_locks.json")
AJANLAR = ("yasu", "utku", "ihsan", "salih", "orkestrator")
# D-303: sahipsiz kilit olculdu (utku/nace_coklu_ata.py 2 gun acik kaldi).
# Bu yasi asan kilit dusmus sayilir — kilit sonsuza kadar agaci bloke etmez.
BAYAT_SAAT = int(os.environ.get("HUGINN_KILIT_BAYAT_SAAT", "24"))


def _git(*arg: str) -> str:
    cp = subprocess.run(["git", *arg], cwd=KOK, capture_output=True,
                        text=True, errors="replace")
    return cp.stdout.strip()


def ajan_kimligi() -> str | None:
    """Kilit sahipligiyle karsilastirilabilir ajan adi (yoksa None).

    D-303: projedeki tek kimlik kaynagi. `karar_no.py` de bunu cagirir.
    D-306: gercek cozum burada. Kimlik zinciri:

        HUGINN_AJAN  >  ajan_<ad>.json (ajan basina, PAYLASMAZ)
                     >  git config huginn.ajan  (paylasilan .git/config)
                     >  git config user.name

    Neden ajan basina dosya oncelikli? Cunku ayni makinede birden fazla
    ajan calisabiliyor (olculdu: utku/ihsan/yasu ayni anda kilitli). `.git/
    config` ve `.env` PAYLASILAN oldugu icin oraya yazilan kimlik BUTUN
    ajanlara ayni degeri bilerdi - hata bastan sona yayilir.
    """
    try:
        from ajan_kimligi import KimlikBelirsiz, ajan_kimligi as _coz
    except ImportError:                      # pragma: no cover - yedek yol
        pass
    else:
        try:
            return _coz()
        except KimlikBelirsiz:
            # Sozlesme bu fonksiyonun "cozulemezse None" demesidir, ama
            # paylasilan cozucu (ajan_kimligi.py:77-83) belirsizlikte
            # istisna firlatir. O istisna yukseltilirse main()'in
            # "kimlik yok -> uyar ve gec" dalina (satir 97-100) HIC
            # ulasilamaz ve pre-commit kancası HUGINN_AJAN tanimli
            # olmayan her ajan icin kalici olarak exit 1 verir
            # (olculdu: 3 ajan dosyali makinede, 2026-10-04).
            return None

    if ad := (os.environ.get("HUGINN_AJAN") or _git("config", "huginn.ajan")):
        return ad.strip().lower()
    adi = _git("config", "user.name").lower()
    return next((a for a in AJANLAR if a in adi), None)


def bayat(k: dict, simdi: datetime | None = None) -> bool:
    """Kilit `BAYAT_SAAT`'ten eskiyse sahipsiz sayilir."""
    try:
        t = datetime.fromisoformat(k["kilitlendi"])
    except (KeyError, TypeError, ValueError):
        return False  # zamansiz kilit: bayatlatma, sahibi dursun
    return (simdi or datetime.now()) - t > timedelta(hours=BAYAT_SAAT)


def ihlaller(staged: list[str], ben: str | None,
             kilitler: dict) -> list[tuple[str, dict]]:
    """Staged yollardan `ben` disinda bir ajanin TAZE kilidinde olanlar."""
    return [(y, kilitler[y]) for y in staged
            if y in kilitler and kilitler[y]["sahip"] != ben
            and not bayat(kilitler[y])]


def main() -> int:
    if not KILIT.is_file():
        return 0
    kilitler = json.loads(KILIT.read_text(encoding="utf-8"))
    staged = [y for y in _git("diff", "--cached", "--name-only").splitlines() if y]
    ben = ajan_kimligi()
    ihlal = ihlaller(staged, ben, kilitler)
    if not ihlal:
        return 0
    for yol, k in ihlal:
        print(f"[kilit] {yol} -> {k['sahip']} ({k['task_id']})", file=sys.stderr)
    if ben is None:
        print("[kilit] UYARI: ajan kimligi yok, gecildi. Kur: "
              "git config huginn.ajan <ad>", file=sys.stderr)
        return 0
    print(f"[kilit] DURDU: {len(ihlal)} dosya {ben} disinda bir ajanin kilidinde. "
          "Kilit sahibiyle konus veya 'orchestrator_internal.py birak' ile devret.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
