# -*- coding: utf-8 -*-
"""web_app normalize fonksiyonlarinin gercek ciktilarini kesfet."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from web_app import normalize_company_name, extract_trade_name, normalize_company, tr_normalize  # noqa: E402

ORNEKLER = [
    "Arıtes Metal Sanayi ve Ticaret Ltd. Şti.",
    "DÜNDAR ELEKTRİK SANAYİ",
    "ZMT PTO HIDROLIK",
    "GIDA SANAYI VE TICARET A.Ş.",
    "BUYUK AGAC MOB.INS.SAN. VE TIC. LTD.STI.",
    "AKSU KROM PASLANMAZ ÇELIK MAK. İML. SAN VE TIC. LTD.ŞTI.",
    "4N BİLİŞİM TEKNOLOJİLERİ A.Ş.",
    "MERPAR MOTORLU ARAÇLAR YEDEK PARÇA SAN. TIC. LTD. ŞTI.",
    "ABC İNŞAAT SANAYİ VE TİCARET ANONİM ŞİRKETİ",
    "XYZ MUHENDISLIK MIMARLIK LIMITED SIRKETI",
    "Krm Metalurji ve Insaat Sanayii ve Ticareti Limited",
]

for o in ORNEKLER:
    n = normalize_company_name(o)
    t = extract_trade_name(o)
    print(f"IN : {o}")
    print(f"LEG: {n}")
    print(f"TRD: {t}")
    print()

print("tr_normalize('DÜNDAR ELEKTRİK') =", tr_normalize("DÜNDAR ELEKTRİK"))
row = {"legal_name": "arıtes test ltd", "trade_name": ""}
print("normalize_company:", normalize_company(row))
