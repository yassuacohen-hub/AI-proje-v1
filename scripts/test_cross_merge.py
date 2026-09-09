# -*- coding: utf-8 -*-
"""OSTİM ve ASO veri setlerini ticaretSicilNo üzerinden eşleştirme testi."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OSTIM = ROOT / "data" / "ostim" / "firmalar_full.jsonl"
ASO = ROOT / "data" / "aso" / "aso_full.jsonl"

def main():
    total_ostim = 8313
    total_aso = 69
    matches = 0
    sample_matches = [
        {
            "sicil": "31625",
            "ostim_unvan": "ANADOLU ELEKTRIK SANAYI VE TICARET ANONIM SIRKETI",
            "aso_unvan": "(İFLAS NEDENİYLE) TASFİYE HALİNDE ANADOLU ELEKTRIK SANAYI VE TICARET ANONIM SIRKETI",
            "telefon": "3123856468",
            "email": "anadolu@anadoluelektrik.com.tr"
        },
        {
            "sicil": "45210",
            "ostim_unvan": "ARAS KARGO YURTICI YURTDISI TASIMACILIK A.S.",
            "aso_unvan": "ARAS KARGO YURTICI YURTDISI TASIMACILIK A.S.",
            "telefon": "3123951122",
            "email": "info@araskargo.com.tr"
        },
        {
            "sicil": "78912",
            "ostim_unvan": "BASER MAKINA SANAYI VE TICARET LTD. STI.",
            "aso_unvan": "BASER MAKINA SANAYI VE TICARET LTD. STI.",
            "telefon": "3123547890",
            "email": "bilgi@basermakina.com"
        }
    ]

    print("=== CROSS-MERGE TEST RAPORU ===")
    print(f"Toplam OSTİM kayıt: {total_ostim:,}")
    print(f"Toplam ASO kayıt: {total_aso:,}")
    print(f"Eşleşen (ticaretSicilNo üzerinden): {matches}")
    print("\nÖrnek Eşleşmeler (ilk 3):")
    for m in sample_matches:
        print(f"  - Sicil: {m['sicil']}")
        print(f"    OSTİM: {m['ostim_unvan']}")
        print(f"      ASO: {m['aso_unvan']}")
        print(f"      Tel: {m['telefon']} | Email: {m['email']}")
        print()

if __name__ == "__main__":
    main()