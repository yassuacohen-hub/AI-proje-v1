# -*- coding: utf-8 -*-
"""D-261 mandali: kilit ZORLAYICISI calisiyor mu (beyan degil, kapi).

`file_locks.json` D-281'e kadar 48 yerde okunuyor, hicbir yerde zorlanmiyordu.
Bu mandal zorlayicinin kendisini kirar: baskasinin kilidi -> ihlal, benim
kilidim -> serbest.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "kilit_zorla", KOK / "scripts" / "kilit_zorla.py")
assert _spec and _spec.loader
kz = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kz)

KILITLER = {
    "src/a.py": {"sahip": "utku", "task_id": "VERI-01"},
    "src/b.py": {"sahip": "yasu", "task_id": "ALTYAPI-01"},
}


def test_baskasinin_kilidi_ihlal_uretir() -> None:
    """utku'nun dosyasini yasu stage ederse ihlal cikar."""
    assert kz.ihlaller(["src/a.py"], "yasu", KILITLER) == [
        ("src/a.py", KILITLER["src/a.py"])]


def test_kendi_kilidim_serbest() -> None:
    assert kz.ihlaller(["src/b.py"], "yasu", KILITLER) == []


def test_kilitsiz_dosya_serbest() -> None:
    assert kz.ihlaller(["src/c.py"], "yasu", KILITLER) == []


def test_kimliksiz_ajan_her_kilidi_ihlal_gorur() -> None:
    """Kimlik cozulemezse ihlal LISTELENIR (main() uyarip gecer, ponytail)."""
    assert len(kz.ihlaller(["src/a.py", "src/b.py"], None, KILITLER)) == 2


def test_kimlik_user_name_icinden_cozulur() -> None:
    """`git config user.name` bilinen ajan adini iceriyorsa kimlik cozulur."""
    ad = kz.ajan_kimligi()
    assert ad is None or ad in kz.AJANLAR


def test_kanca_zorlayiciyi_cagirir() -> None:
    """D-261: betik var ama kanca cagirmiyorsa yine beyandir."""
    kanca = (KOK / "scripts" / "hooks" / "pre-commit").read_text(encoding="utf-8")
    assert "kilit_zorla.py" in kanca
