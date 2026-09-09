# -*- coding: utf-8 -*-
"""Gercek normalize ciktilarini UTF-8 dosyaya yazar (konsol bozmasin)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from web_app import normalize_company_name

ORNEKLER = [
    "Arıtes Metal Sanayi ve Ticaret Ltd. Şti.",
    "ABC İnşaat Sanayi ve Ticaret Anonim Şirketi",
    "Dündar Elektrik Sanayi",
    "Örnek Mühendislik Mimarlık Ltd. Şti.",
    "Ankara Turizm ve Ticaret Ltd. Şti.",
    "X İthalat ve İhracat Limited Şirketi",
]

lines = []
for o in ORNEKLER:
    lines.append(f"IN : {o}")
    lines.append(f"OUT: {normalize_company_name(o)}")
    lines.append("")

out = Path(__file__).with_name("_norm_cikti.txt")
out.write_text("\n".join(lines), encoding="utf-8")
print(f"yazildi: {out.name}")
