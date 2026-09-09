# -*- coding: utf-8 -*-
"""Kural 1-3 dogrulama testleri.

Kaynak: AI proje v1/V10/09_kurallar_ve_promptlar/11_unvan_kisaltma_ve_tabela_kurallari.md
Kisaltmalar Turkce karakterlidir (TIC. degil TİC., STI. degil ŞTİ.).
"""
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from web_app import extract_trade_name, normalize_company_name, normalize_company, tr_normalize

# ── Kural 1+2: normalize_company_name (kaynak dokuman Bolum 2) ──
NORM_CASES = [
    # (giris, beklenen)
    ("Arıtes Metal Sanayi ve Ticaret Ltd. Şti.", "ARITES METAL SAN. VE TİC. LTD. ŞTİ."),
    ("ABC İnşaat Sanayi ve Ticaret Anonim Şirketi", "ABC İNŞ. SAN. TİC. A.Ş."),
    ("Dündar Elektrik Sanayi", "DÜNDAR ELEK. SAN."),
    ("Örnek Mühendislik Mimarlık Ltd. Şti.", "ÖRNEK MÜH. MİM. LTD. ŞTİ."),
    ("ABC Metal San ve Tic Ltd Sti", "ABC METAL SAN. TİC. LTD. ŞTİ."),
    ("X İthalat ve İhracat A.Ş.", "X İTH. İHR. A.Ş."),
    ("Y Turizm ve Ticaret Limited Şirketi", "Y TUR. TİC. LTD. ŞTİ."),
]

# ── Kural 3: extract_trade_name ornekleri ──
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

fails = 0
print("=== Kural 1+2: normalize_company_name ===")
for src, want in NORM_CASES:
    got = normalize_company_name(src)
    ok = got == want
    fails += 0 if ok else 1
    print(f"  [{'OK' if ok else 'FAIL'}] {src!r}")
    if not ok:
        print(f"        beklenen: {want!r}\n        gelen   : {got!r}")

print("=== Kural 3: extract_trade_name ===")
for src, want in TRADE_CASES:
    got = extract_trade_name(src)
    ok = got == want
    fails += 0 if ok else 1
    print(f"  [{'OK' if ok else 'FAIL'}] {src} -> {got!r}")
    if not ok:
        print(f"        beklenen: {want!r}")

print("=== normalize_company (API davranisi) ===")
row = {"legal_name": "arıtes metal sanayi ve ticaret ltd. şti.", "trade_name": "DÜNDAR ELEK"}
out = normalize_company(row)
print(f"  legal : {out['legal_name']}")
print(f"  trade : {out['trade_name']}  (DB'deki eski 'DÜNDAR ELEK' unvandan yenilendi)")
if out["trade_name"] != "ARITES METAL":
    fails += 1
    print("  FAIL: trade 'ARITES METAL' bekleniyordu")

print()
print(f"SONUC: {'TUM TESTLER GECTI ✓' if fails == 0 else f'{fails} TEST KALDI ✗'}")
sys.exit(1 if fails else 0)
