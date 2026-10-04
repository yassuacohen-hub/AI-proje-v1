"""Tam suite kirmizilarini sahiplik kovasina ayirir (taze olcum).

D-224: hata mesaji okunmadan gowrev acilmaz; burada dosya:test adi + kaynak
KOVASI olculur. 18 kirmizinin sahipligi tek tabloda gorunur.
"""

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
RAPOR = Path(r"C:\Users\yasin\AppData\Local\Temp\kilo\tam_suit.txt")

satirlar = RAPOR.read_text(encoding="utf-8", errors="replace").splitlines()
failed = [s for s in satirlar if s.startswith("FAILED")]
ozet = next((s for s in reversed(satirlar)
             if re.search(r"\d+ failed", s)), "ozet yok")

print("=== TAM SUIT (canli olcum) ===")
print(f"  {ozet}\n")

# --- kova siniflari ---
KOVALAR = [
    ("brief sablonu (SEMA brifleri)", r"test_brief_sablon_denetim"),
    ("embedder (RAG modeli)", r"test_rag_embedder|vector/test_embedder"),
    ("pano / orkestrator", r"test_pano|test_task_board|test_gorev_kutusu|"
                           r"test_naming_audit|test_durum_sozlugu|"
                           r"test_tetik|test_dokuman_politikasi|"
                           r"test_kok_|test_mukerrer|test_hafiza"),
    ("kalite skoru / diger", r"test_kalite|test_quality|test_normalize|"
                             r"test_identity"),
]

print("=== KOVA DAGILIMI ===")
sayac = Counter()
for f in failed:
    dosya = f.split("::")[0].replace("FAILED ", "").strip()
    for ad, desen in KOVALAR:
        if re.search(desen, dosya):
            sayac[ad] += 1
            break
    else:
        sayac["siniflanmadi"] += 1

for ad, _ in KOVALAR:
    print(f"  {ad:34} {sayac[ad]:3}")
print(f"  {'siniflanmadi':34} {sayac['siniflanmadi']:3}")
print(f"  {'TOPLAM':34} {sum(sayac.values()):3}")

print("\n=== 18 KIRMIZININ TAM LİSTESİ (dosya::test) ===")
for i, f in enumerate(failed, 1):
    temiz = f.replace("FAILED ", "").split(" - ")[0]
    print(f"  {i:2}. {temiz}")

print("\n=== BU AJANIN (utku) ALANI ===")
benim = [f for f in failed
         if "tsg" in f.lower() or "ticaret_sicili" in f.lower()
         or "bulgu_defteri" in f.lower() or "brief_utku" in f]
print(f"  {len(benim)} adet")
for f in benim:
    print(f"    {f.replace('FAILED ', '').split(' - ')[0]}")

print("\n=== KARAR ===")
if not benim:
    print("  Bu ajanin alaninda KIRMIZI YOK -> teslim gerekcesi degil (D-260).")
print("  Raporlara yazilacak taban: bu sayi, rapordaki eski sayidan")
print("  guncellir; hangi kirmizin kime ait oldugu yukaridaki kova ile kanitlanir.")
