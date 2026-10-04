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


#: D-339: "kimlik yok" (fail-open, uyar-ve-gec) ile "kimlik BELIRSIZ" (2+ ajan
#: dosyasi ayni makinede, fail-closed olmali) ayni None degerine sikisinca
#: belirsizlik de sessizce gecerdi -> kilit fiilen devre disi kalirdi.
BELIRSIZ = "__belirsiz__"


def ajan_kimligi() -> str | None:
    """Kilit sahipligiyle karsilastirilabilir ajan adi.

    Donus: gercek ad, `None` (kimlik hic yok, fail-open) veya `BELIRSIZ`
    (birden fazla ajan dosyasi var, main() bunu fail-closed isler, D-339).

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
            # D-339: eskiden burada None donuyordu -> main() bunu "kimlik yok"
            # ile ayni isleyip kilidi UYARIP GECIYORDU (utku, ihsan'in kilitli
            # dosyasini commit'e soktu, ajan_salih.json + ajan_utku.json ayni
            # makinede birlikte var oldugu icin kimlik COZULEMEDI ve kapı
            # sessizce acildi). Belirsizlik "yok" degil, "ikisi de var"dir —
            # main()'e ayri isaretle dondur, orada fail-closed islensin.
            return BELIRSIZ

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
    # D-339: BELIRSIZ ("ikisi de var") None ("hic yok") ile AYNI DEGIL —
    # ikisini de ihlaller()'e "eslesmez" olarak verip asagida ayirt ederiz.
    ben_ihlal_anahtari = None if ben == BELIRSIZ else ben
    ihlal = ihlaller(staged, ben_ihlal_anahtari, kilitler)
    if not ihlal:
        return 0
    for yol, k in ihlal:
        print(f"[kilit] {yol} -> {k['sahip']} ({k['task_id']})", file=sys.stderr)
    if ben == BELIRSIZ:
        # D-339: fail-closed. Bu dal eskiden `ben is None` ile ayni islenip
        # UYARIP GECIYORDU; utku'nun ihsan-kilitli dosyayi commit'e sokmasinin
        # kok nedeni budur. Birden fazla ajan dosyasi "kimlik yok" degil,
        # "hangisi oldugu belirsiz" demektir -> durdur.
        print("[kilit] DURDU: bu makinede birden fazla ajan_<ad>.json var, "
              "kimlik BELIRSIZ. HUGINN_AJAN ortam degiskeniyle belirtin veya "
              "data/orchestrator/ajanlar/ icinde tek dosya kalsin.",
              file=sys.stderr)
        return 1
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
