# -*- coding: utf-8 -*-
"""D-60 ajan adı kuralı: kanonik adlar ihsan / utku / salih / yasu.

Kural: araç adı = takma ad, Türkçe ad = kanonik ad.
Eski/araç adları (kilo, roo, merve, continue, cline, yasin) takma ad olarak
korunur; "Ajan kilo", "KILO", "kilo_code" gibi yazımlar tek posta kutusuna
(utku.jsonl / ihsan.jsonl / salih.jsonl / yasu.jsonl) çözümlenir.

D-61: ekrana yazılan hitap BÜYÜK HARF (`ajan_goster`).
"""
from __future__ import annotations

import pytest

from company_master.orchestrator import trigger
from company_master.orchestrator.trigger import TriggerError, ajan_goster, ajan_normalize


@pytest.mark.parametrize(
    ("ham", "beklenen"),
    [
        # utku (eski kilo)
        ("utku", "utku"),
        ("Utku", "utku"),
        ("kilo", "utku"),
        ("Kilo", "utku"),
        ("KILO", "utku"),
        ("Ajan kilo", "utku"),
        ("ajan_kilo", "utku"),
        ("ajankilo", "utku"),
        ("kilo_code", "utku"),
        ("kilo-code", "utku"),
        ("kilocode", "utku"),
        ("@kilo", "utku"),
        ("  kilo  ", "utku"),
        # yasu (araç: cline; KAHİN "yasin" de diyebilir)
        ("yasu", "yasu"),
        ("Yasu", "yasu"),
        ("cline", "yasu"),
        ("Cline", "yasu"),
        ("ajancline", "yasu"),
        ("Ajan cline", "yasu"),
        ("clinebot", "yasu"),
        ("yasin", "yasu"),
        ("Yasin", "yasu"),
        # ihsan (eski roo)
        ("ihsan", "ihsan"),
        ("roo", "ihsan"),
        ("Ajan roo", "ihsan"),
        ("roo_code", "ihsan"),
        ("roo-code", "ihsan"),
        ("roocode", "ihsan"),
        ("orkestrator", "ihsan"),
        # salih (eski merve; Continue IDE)
        ("salih", "salih"),
        ("Salih", "salih"),
        ("merve", "salih"),
        ("Merve", "salih"),
        ("Ajan merve", "salih"),
        ("continue", "salih"),
        ("Continue", "salih"),
        ("continue-ide", "salih"),
        ("continue_ide", "salih"),
        # takma adı olmayanlar aynen geçer
        ("claude_code", "claude_code"),
        ("claude-code", "claude_code"),
    ],
)
def test_ajan_normalize_kanonik_ada_cevirir(ham: str, beklenen: str) -> None:
    assert ajan_normalize(ham) == beklenen


@pytest.mark.parametrize("ham", ["", "   ", None])
def test_ajan_normalize_bos_ad_hata(ham) -> None:
    with pytest.raises(TriggerError):
        ajan_normalize(ham)


@pytest.mark.parametrize(
    ("ham", "beklenen"),
    [
        ("ihsan", "İHSAN"),
        ("roo", "İHSAN"),
        ("utku", "UTKU"),
        ("kilo", "UTKU"),
        ("salih", "SALİH"),
        ("continue", "SALİH"),
        ("yasu", "YASU"),
        ("cline", "YASU"),
        ("yasin", "YASU"),
    ],
)
def test_ajan_goster_buyuk_harf(ham: str, beklenen: str) -> None:
    """D-61: ekranda hitap BÜYÜK HARF, Türkçe i→İ."""
    assert ajan_goster(ham) == beklenen


def test_tetik_yolu_varyantlar_ayni_dosyaya_gider(tmp_path) -> None:
    beklenen = tmp_path / "triggers" / "utku.jsonl"
    for ad in ("utku", "kilo", "Ajan kilo", "KILO", "kilo_code"):
        assert trigger._tetik_yolu(ad, tmp_path) == beklenen


def test_tetik_ekle_ve_bekleyen_varyant_uyumlu(tmp_path) -> None:
    """'Ajan kilo' ile eklenen tetik 'utku' ile okunur (tek posta kutusu)."""
    kayit = trigger.tetik_ekle("T-D60", "Ajan kilo", "isim testi", data_dir=tmp_path)
    assert kayit["ajan"] == "utku"
    bekleyen = trigger.bekleyen_tetikler("KILO", data_dir=tmp_path)
    assert [t["task_id"] for t in bekleyen] == ["T-D60"]
