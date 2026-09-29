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


def test_commit_msg_kancasi_tahsisi_dogrular() -> None:
    """MANDAL-TAHSIS-01 (D-303): ayni ders, ucuncu kurban karar numarasi.

    Olcum: ayni numara UC kez iki karara gitti (D-281, D-301, D-303). Ucunde de
    commit mesaji "D-NNN" diyor ama `data/karar_tahsis/D-NNN.txt` yok -- `--al`
    hic calistirilmamis. Tahsis vardi, zorlayani yoktu (D-261).
    """
    yol = _KOK / "scripts" / "hooks" / "commit-msg"
    assert yol.exists(), (
        "scripts/hooks/commit-msg yok; commit mesajindaki D-NNN'in tahsis "
        "edildigini hicbir sey zorlamaz (D-281/D-301/D-303 boyle olustu)."
    )
    kosan = "\n".join(s for s in yol.read_text(encoding="utf-8").splitlines()
                      if not s.lstrip().startswith("#"))
    assert "karar_no.py --dogrula" in kosan, (
        "commit-msg kancasi `karar_no.py --dogrula` cagirmiyor; kapi yazili "
        "ama kosmuyor (D-302'nin dersi)."
    )


def test_dogrula_tahsissiz_numarayi_durdurur() -> None:
    """Kapinin kendisi de beyandir, kirilana kadar (D-288/D-302)."""
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("karar_no", _KOK / "scripts" / "karar_no.py")
    assert spec and spec.loader
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.dogrula("D-999: hic tahsis edilmemis")[0] == 1
    assert m.dogrula("chore: numarasiz commit")[0] == 0
