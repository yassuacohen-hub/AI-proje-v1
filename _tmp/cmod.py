"""Modul yerlesimi + maske fonksiyonlarinin gercek cagrilabilirligi."""
import importlib.util
import inspect
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CM = KOK / "src" / "company_master"

print("=== 1) company_master yapisi ===")
print("  odin_ai var mi :", (CM / "odin_ai").is_dir())
print("  alt dizinler   :", sorted(p.name for p in CM.iterdir() if p.is_dir())[:20])
print("  sunum.py var   :", (CM / "sunum.py").is_file())

print()
print("=== 2) maske fonksiyonlari (canli import) ===")
sys.path.insert(0, str(KOK / "src"))
from company_master import sunum  # noqa: E402

for ad in ("maskeleme_odin", "genel_maske", "company_master_maske"):
    f = getattr(sunum, ad, None)
    print(f"  {ad:22s} -> {inspect.signature(f) if f else 'YOK'}")

print()
print("=== 3) CANLI DAVRANIS — ham kacak ne oluyor? ===")
KACAK = "NACE kodu 74.90, VKN 1234567890, TCKN 12345678901, tel 05551112233"
for kaynak in ("V1", "V2", "V3", "maske"):
    try:
        sonuc = sunum.maskeleme_odin(KACAK, hedef="musteri", kaynak=kaynak)
        print(f"  kaynak={kaynak:6s} -> {str(sonuc)[:80]}")
    except Exception as e:
        print(f"  kaynak={kaynak:6s} -> HATA: {type(e).__name__}: {e}")

print()
print("=== 4) BOS/None davranisi ===")
for metin in ("", None):
    try:
        r = sunum.maskeleme_odin(metin, hedef="musteri", kaynak="V1")
        print(f"  {metin!r:8s} -> {r!r}")
    except Exception as e:
        print(f"  {metin!r:8s} -> HATA: {type(e).__name__}: {e}")

print()
print("=== 5) test dizini adlandirma ===")
T = KOK / "tests"
print("  ", sorted(p.name for p in T.glob("test_*.py"))[:25])