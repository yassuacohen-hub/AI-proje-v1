# -*- coding: utf-8 -*-
"""MANDAL-SAHNE-KURULUM-01 (D-301): kapi yazili olmak yetmez, KOSMALI.

Kendi hatam, ayni turda ucuncu kez ayni kokten (D-260). MANDAL-SAHNE-01'i
`.pre-commit-config.yaml`a yazdim ve "kuruldu" saydim. Olculdu:
`core.hooksPath = scripts/hooks`, yani fiilen kosan kanca `scripts/hooks/pre-commit`
ve o dosya `sahne_kapisi.py`yi cagirmiyordu. `pre_commit` modulu de kurulu degil.
Sonuc: kapi yaziliydi, **kosmuyordu** -- ve `8a25798` commit'i 24 dosyayla
kapidan gecip benim dort mandalimi da icine aldi. Tam onlemek icin kurdugum olay.

Bu test D-261'in kuralini uygular: zorlayani olmayan kayit beyandir.
"""
from __future__ import annotations

from pathlib import Path

_KOK = Path(__file__).resolve().parents[1]


def test_kanca_sahne_kapisini_cagirir() -> None:
    """Betik var ama kanca cagirmiyorsa mandal yoktur (D-261)."""
    kanca = (_KOK / "scripts" / "hooks" / "pre-commit").read_text(encoding="utf-8")
    kosan = "\n".join(s for s in kanca.splitlines() if not s.lstrip().startswith("#"))
    assert "sahne_kapisi.py" in kosan, (
        "scripts/hooks/pre-commit sahne_kapisi.py'yi cagirmiyor; `core.hooksPath` "
        "bu dizini gosterdigi icin kapi hic kosmaz (D-301'de tam bu oldu)."
    )


def test_sahne_kapisi_betigi_var() -> None:
    assert (_KOK / "scripts" / "sahne_kapisi.py").exists()
