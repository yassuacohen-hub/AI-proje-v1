# -*- coding: utf-8 -*-
"""D-33 ajan adı kuralı: kanonik adlar kilo / cline / roo / merve (D-59).

"Ajan kilo", "KILO", "kilo_code", "ajancline", "Ajan roo", "roo_code"
gibi yazımlar tek posta kutusuna (kilo.jsonl / cline.jsonl / roo.jsonl) çözümlenir.
"""
from __future__ import annotations

import pytest

from company_master.orchestrator import trigger
from company_master.orchestrator.trigger import TriggerError, ajan_normalize


@pytest.mark.parametrize(
    ("ham", "beklenen"),
    [
        ("kilo", "kilo"),
        ("Kilo", "kilo"),
        ("KILO", "kilo"),
        ("Ajan kilo", "kilo"),
        ("ajan_kilo", "kilo"),
        ("ajankilo", "kilo"),
        ("kilo_code", "kilo"),
        ("kilo-code", "kilo"),
        ("kilocode", "kilo"),
        ("@kilo", "kilo"),
        ("  kilo  ", "kilo"),
        ("cline", "cline"),
        ("ajancline", "cline"),
        ("Ajan cline", "cline"),
        ("clinebot", "cline"),
        ("roo", "roo"),
        ("Ajan roo", "roo"),
        ("roo_code", "roo"),
        ("roo-code", "roo"),
        ("roocode", "roo"),
        ("orkestrator", "roo"),
        ("claude_code", "claude_code"),
        ("claude-code", "claude_code"),
        # D-59: merve = QA/Release Engineer (Continue IDE)
        ("merve", "merve"),
        ("Merve", "merve"),
        ("Ajan merve", "merve"),
        ("continue", "merve"),
        ("Continue", "merve"),
        ("continue-ide", "merve"),
        ("continue_ide", "merve"),
    ],
)
def test_ajan_normalize_kanonik_ada_cevirir(ham: str, beklenen: str) -> None:
    assert ajan_normalize(ham) == beklenen


@pytest.mark.parametrize("ham", ["", "   ", None])
def test_ajan_normalize_bos_ad_hata(ham) -> None:
    with pytest.raises(TriggerError):
        ajan_normalize(ham)


def test_tetik_yolu_varyantlar_ayni_dosyaya_gider(tmp_path) -> None:
    beklenen = tmp_path / "triggers" / "kilo.jsonl"
    for ad in ("kilo", "Ajan kilo", "KILO", "kilo_code"):
        assert trigger._tetik_yolu(ad, tmp_path) == beklenen


def test_tetik_ekle_ve_bekleyen_varyant_uyumlu(tmp_path) -> None:
    """'Ajan kilo' ile eklenen tetik 'kilo' ile okunur (tek posta kutusu)."""
    kayit = trigger.tetik_ekle("T-D33", "Ajan kilo", "isim testi", data_dir=tmp_path)
    assert kayit["ajan"] == "kilo"
    bekleyen = trigger.bekleyen_tetikler("KILO", data_dir=tmp_path)
    assert [t["task_id"] for t in bekleyen] == ["T-D33"]
