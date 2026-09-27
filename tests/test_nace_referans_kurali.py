# -*- coding: utf-8 -*-
"""D-234 mandalı: NACE referansı tek kaynaktan kurulmaz, seviye kısaltılmaz.

Neden test: D-234 iki hatayı kapatıyor ve ikisi de "sonra düzeltiriz" diye
sessizce geri gelebilir —
  1. 6 haneli resmi kodu 4'e kısaltıp asılı kaybetmek,
  2. yeni resmi listeyi eskilerin YERİNE koymak (ölçüm: %45 kapsam kaybı).
Ağ ve DB gerektirmez; diskteki referans kaynaklarına bakar.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

VAULT = Path(__file__).resolve().parents[1]
NACE = VAULT / "data" / "nace"

# D-234 madde 2: dördü birden zorunlu. Yeni kaynak eskinin yerine konmaz.
ZORUNLU_KAYNAKLAR = ("turkiye_nace.json", "nace-rev-2-1.json", "nace-rev-2.json")


@pytest.mark.parametrize("ad", ZORUNLU_KAYNAKLAR)
def test_d234_eski_kaynaklar_silinmemis(ad: str) -> None:
    """Ölçüm: yalnız resmi xlsx ile eşleşme %47.7, dördü birlikte %92.9.

    Bu dosyalardan biri silinirse kapsam sessizce çöker.
    """
    assert (NACE / ad).is_file(), (
        f"{ad} yok. D-234: yeni resmi liste eskilerin YERİNE konmaz, üstüne eklenir."
    )


def test_d234_resmi_xlsx_var() -> None:
    """Esnaf/sanatkâr meslek kolları kaynağı (adı sürüm aldığı için desenle)."""
    bulunan = list(NACE.glob("sektor_meslek_nace_*_resmi.xlsx"))
    assert bulunan, "sektor_meslek_nace_*_resmi.xlsx yok — D-234 dördüncü kaynak eksik."


def test_d234_turkiye_nace_iki_seviyeyi_birlikte_tasiyor() -> None:
    """D-234 madde 1: 6 hane asıl, 4 hane türetilmiş — YAN YANA durur.

    turkiye_nace.json zaten doğru yapıda (code_6digit + code). Kural bunu icat
    etmiyor, kaybolmasını engelliyor.
    """
    kayitlar = json.loads((NACE / "turkiye_nace.json").read_text(encoding="utf-8"))
    ornek = [k for k in kayitlar if k.get("code_6digit") and k.get("code")]
    assert len(ornek) > 1000, "code_6digit/code ikilisi kaybolmuş — seviye kısaltılmış olabilir."

    for k in ornek[:200]:
        alti = str(k["code_6digit"])          # '011107' (noktasız da olabilir)
        dort = str(k["code"])                 # '01.11'
        assert re.fullmatch(r"\d{2}\.\d{2}", dort), f"4 hane bozuk: {dort!r}"
        # 4 hane, 6 hanenin önekidir — türetme ilişkisi korunmalı
        assert alti.replace(".", "").startswith(dort.replace(".", "")), (
            f"türetme kopmuş: {alti!r} -> {dort!r}"
        )


def test_d234_agents_mde_kayitli() -> None:
    """Kural vault AGENTS.md'de duruyor mu (D-168: oturum başı okunan tek kaynak)."""
    metin = (VAULT / "AGENTS.md").read_text(encoding="utf-8")
    assert "D-234" in metin
    assert "Seviye Kısaltılmaz" in metin
