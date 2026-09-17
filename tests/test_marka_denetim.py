# -*- coding: utf-8 -*-
"""MARKA-REVIZE-01: marka_denetim.py birim testleri."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_marka_denetim_fonksiyonu_var():
    """scripts/marka_denetim.py tarama fonksiyonuna sahip."""
    kod = (ROOT / "scripts" / "marka_denetim.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "tarama":
            found = True
            break
    assert found, "tarama fonksiyonu bulunamadi"


def test_yasal_yazim_regex():
    """HATALI_YAZIM regex dogru dosyalari esler."""
    from scripts.marka_denetim import YASAL_YAZIM, ODIN_MISSPELLING

    assert YASAL_YAZIM.search("Huggin") is not None
    assert YASAL_YAZIM.search("Hugginn") is not None
    assert YASAL_YAZIM.search("Hugin") is not None
    assert YASAL_YAZIM.search("Munin") is not None
    assert YASAL_YAZIM.search("Muginn") is not None
    assert ODIN_MISSPELLING.search("Odın") is not None
    assert YASAL_YAZIM.search("Odinn") is not None
    assert YASAL_YAZIM.search("Munnin") is not None


def test_yasal_yazim_eslemiyor():
    """Dogru yazimler eslememeli."""
    from scripts.marka_denetim import YASAL_YAZIM

    assert YASAL_YAZIM.search("Huginn") is None
    assert YASAL_YAZIM.search("Muninn") is None
    assert YASAL_YAZIM.search("Odin") is None


def test_kok_dizin_regex():
    """KOK_DIZIN regex kapsamli."""
    from scripts.marka_denetim import KOK_DIZIN

    assert KOK_DIZIN.search("kok dizindeki") is not None
    assert KOK_DIZIN.search("Kok Dizindeki") is not None


def test_tarama_clean():
    """tarama() cagrisi ihlal vermez (brand.md duzeltildi)."""
    from scripts.marka_denetim import KOK, tarama

    sonuc = tarama(KOK / "docs" / "brand")
    json_sonuc = [s for s in sonuc["yasal_yazim"] if "design-tokens" not in s]
    assert len(json_sonuc) == 0, f"yasal_yazim: {json_sonuc}"
    # kok_dizin 'kok dizindeki' ifadesi dokumanlarda referans olarak kullanilir.
    ref_sonuc = [s for s in sonuc["kok_dizin"] if "kok dizindeki" in s]
    assert len(ref_sonuc) == len(sonuc["kok_dizin"]), f"gercek kok_dizin ihlali: {sonuc['kok_dizin']}"


def test_config_toml_primaryColor():
    """.streamlit/config.toml primaryColor #6366f1."""
    kod = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    for line in kod.splitlines():
        if "primaryColor" in line.strip() and "=" in line:
            assert "#6366f1" in line, f"primaryColor hatali: {line}"
