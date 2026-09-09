# -*- coding: utf-8 -*-
"""Kural 1-2-3 birim testleri (DB'siz, hizli).

Kaynak: AI proje v1/V10/09_kurallar_ve_promptlar/11_unvan_kisaltma_ve_tabela_kurallari.md
Kisaltmalar Turkce karakterlidir (TIC. degil TİC., STI. degil ŞTİ.).
Kural 3 karar notu: "ilk 2 hece" -> "ilk 2 KELIME" (ANA_KURALLAR.md).
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from web_app import extract_trade_name, normalize_company, normalize_company_name

# ── Kural 1+2: normalize_company_name (buyuk harf + kisaltma) ──
NORM_CASES = [
    ("Arıtes Metal Sanayi ve Ticaret Ltd. Şti.", "ARITES METAL SAN. VE TİC. LTD. ŞTİ."),
    ("ABC İnşaat Sanayi ve Ticaret Anonim Şirketi", "ABC İNŞ. SAN. TİC. A.Ş."),
    ("Dündar Elektrik Sanayi", "DÜNDAR ELEK. SAN."),
    ("Örnek Mühendislik Mimarlık Ltd. Şti.", "ÖRNEK MÜH. MİM. LTD. ŞTİ."),
    ("ABC Metal San ve Tic Ltd Sti", "ABC METAL SAN. TİC. LTD. ŞTİ."),
    ("X İthalat ve İhracat A.Ş.", "X İTH. İHR. A.Ş."),
    ("Y Turizm ve Ticaret Limited Şirketi", "Y TUR. TİC. LTD. ŞTİ."),
]

# ── Kural 3: extract_trade_name (tabela ismi = ilk 2 kelime) ──
TRADE_CASES = [
    ("DÜNDAR ELEKTRİK SANAYİ", "DÜNDAR ELEKTRİK"),
    ("ARITES METAL SANAYI VE TICARET LTD. STI.", "ARITES METAL"),
    ("GIDA SANAYI VE TICARET A.Ş.", "GIDA"),
    ("BUYUK AGAC MOB.INS.SAN. VE TIC. LTD.STI.", "BUYUK AGAC"),
    ("ZMT PTO HIDROLIK", "ZMT PTO"),
    ("ABC İNŞAAT SANAYİ VE TİCARET ANONİM ŞİRKETİ", "ABC İNŞAAT"),
    ("4N BİLİŞİM TEKNOLOJİLERİ A.Ş.", "4N BİLİŞİM"),
    ("ANKARA ELEKTRİK MALZEMELERİ SANAYİ VE TİCARET LTD. ŞTİ.", "ANKARA ELEKTRİK"),
    ("AKSU KROM PASLANMAZ ÇELIK MAK. İML. SAN VE TIC. LTD.ŞTI.", "AKSU KROM"),
    ("ANKARA MOBİLYA SANAYİ TİCARET A.Ş.", "ANKARA MOBİLYA"),
]


@pytest.mark.parametrize("giris,beklenen", NORM_CASES)
def test_kural_1_2_normalize_company_name(giris, beklenen):
    assert normalize_company_name(giris) == beklenen


@pytest.mark.parametrize("giris,beklenen", TRADE_CASES)
def test_kural_3_extract_trade_name(giris, beklenen):
    assert extract_trade_name(giris) == beklenen


def test_normalize_company_trade_yeniden_uretilir():
    """API davranisi: trade_name her zaman legal_name'den yeniden uretilir."""
    row = {"legal_name": "arıtes metal sanayi ve ticaret ltd. şti.", "trade_name": "DÜNDAR ELEK"}
    out = normalize_company(row)
    assert out["legal_name"] == "ARITES METAL SAN. VE TİC. LTD. ŞTİ."
    assert out["trade_name"] == "ARITES METAL"
