"""V3 tasarim niyeti + dokumanla celiski (olc, kanit)."""
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(KOK / "src"))
from company_master.sunum import maskeleme_odin  # noqa: E402

print("=" * 70)
print("1) V3 NEDEN None? — kod yorumu")
print("=" * 70)
sat = (KOK / "src" / "company_master" / "sunum.py").read_text(
    encoding="utf-8", errors="replace").splitlines()
for n in range(38, 56):
    print(f"  {n+1}: {sat[n][:100]}")

print()
print("=" * 70)
print("2) DOKUMANIN ZORUNLU KAPISI NE YAPIYOR? (kaynak verilmeden)")
print("=" =70)
print("ARCHITECTURE.md: 'Çıkış kapısı | müşteri | maskeleme_odin(metin, "
      "hedef=\"musteri\") ZORUNLU'")
print()
MUSTERI_SORU = (
    "Firmanizin NACE kodu 74.90'dir. VKN 1234567890. "
    "Personel sayiniz 45. Musteri kodu M-01."
)
for kaynak in ("", "V1", "V2", "V3"):
    r = maskeleme_odin(MUSTERI_SORU, hedef="musteri", kaynak=kaynak)
    etiket = repr(kaynak) if kaynak else "(varsayilan / hicbir sey gecirilmiyor)"
    print(f"  kaynak={etiket:28s} -> {str(r)[:80]}")

print()
print("=" * 70)
print("3) CELISKI: musteri kendi NACE kodunu gormeli mi?")
print("=" * 70)
r = maskeleme_odin("NACE kodunuz 74.90", hedef="musteri")
print(f"  girdi : 'NACE kodunuz 74.90'")
print(f"  cikti : {r!r}")
print(f"  SONUC : NACE kodu SILINDI  -> musteri kendi kodunu goremiyor"
      if r and "74.90" not in r else "  SONUC : NACE korundu")

print()
print("=" * 70)
print("4) V3 DALININ GERCEKTEN KULLANIMI")
print("=" * 70)
import subprocess
r = subprocess.run(
    ["grep", "-rn", "--include=*.py", '"V3"', str(KOK / "src"), str(KOK / "scripts")],
    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
sat2 = [l for l in (r.stdout or "").splitlines()
        if ".venv" not in l and "node_modules" not in l]
print(f"  kaynak='V3' gecen yer: {len(sat2)}")
for l in sat2:
    print("   ", l.replace(str(KOK), "")[:95])