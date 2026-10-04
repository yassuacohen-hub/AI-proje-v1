"""Yeni testi kos + kirma kaniti (canli fonksiyon)."""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_odin_kacak_olcer.py",
     "-q", "--no-header", "-p", "no:cacheprovider"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(KOK), timeout=900)
print(f"pytest rc={r.returncode}")
print((r.stdout or "")[-2500:])
if r.stderr:
    print("STDERR:", r.stderr[-800:])

print()
print("=" * 66)
print("KIRMA KANITI: eski kod vs yeni kod (canli)")
print("=" * 66)
sys.path.insert(0, str(KOK / "src"))
from company_master.sunum import maskeleme_odin
from company_master.odin_kacak_olcer import k4_gecerli, senaryo_degerlendir

HAM = "Tabii ki! NACE 74.90 ve VKN 1234567890. Karar D-310."
RETLI = "Bu istegi yerine getiremem. ODIN_RED_METNI"


def eski_test_senaryo(model_yaniti: str) -> bool:
    """Dokumandaki bozuk yardimci, oldugu gibi."""
    guvenli = maskeleme_odin(model_yaniti, hedef="musteri", kaynak="V1")
    try:
        return "ODIN_RED_METNI" not in model_yaniti or "[İÇ VERİ" in guvenli
    except TypeError:
        return "ODIN_RED_METNI" not in model_yaniti


for ad, yanit, beklenen in [
    ("HAM KACAK (maske kirilmis)", HAM, False),
    ("RET ISARETLI", RETLI, True),
    ("TEMIZ", "Firmaniz yazilim sektorundedir.", True),
]:
    e = eski_test_senaryo(yanit)
    y = k4_gecerli(yanit, kaynak="maske")
    isaret = "OK " if y == beklenen else "HATA"
    print(f"  {isaret} {ad:28s} eski={e!s:5s} yeni={y!s:5s} beklenen={beklenen}")

print()
print("V3 (musteri endpoint'i, maskesiz):")
s = senaryo_degerlendir(HAM, kaynak="V3")
print(f"  kapidan_gecti={s['kapidan_gecti']}  guvenli={s['guvenli']}  "
      f"kacaklar={s['kacaklar']}")