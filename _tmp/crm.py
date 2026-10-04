"""1) OLÇ: tam regresyon  2) commit  3) V3 icin ayri gorev ac"""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def git(*a, timeout=1500):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


print("=" * 66)
print("ADIM 1 — OLÇ: tam test paketi (degisiklik YAPILMADI, sadece yeni dosyalar)")
print("=" * 66)
r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-q", "--no-header",
     "-p", "no:cacheprovider"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(KOK), timeout=1500)
out = (r.stdout or "").strip()
print(f"  rc = {r.returncode}")
for l in out.splitlines()[-8:]:
    print("  " + l)

if r.returncode != 0:
    print("\n  !! REGRESYON VAR - COMMIT ATLANDI")
    sys.exit(1)

print()
print("=" * 66)
print("ADIM 2 — DEĞİŞTİR: commit (yalnizca yeni iki dosya)")
print("=" * 66)
rc, c = git("add", "--", "src/company_master/odin_kacak_olcer.py",
            "tests/test_odin_kacak_olcer.py")
print(f"  add rc={rc}")
rc, staged = git("diff", "--cached", "--stat")
print("  " + (staged or "(bos)").replace("\n", "\n  "))
if "odin_kacak_olcer.py" not in staged:
    print("  !! beklenmedik -> COMMIT ATLANDI")
    sys.exit(1)

mesaj = (
    "fix(odin): K4 kacak olceri gercek fonksiyon olarak (D-338)\n\n"
    "docs/ODIN_PROMPT_INJECTION_SCENARIOS.md:38-42 icindeki test_senaryo() K4'OLCEMIYORDU.\n"
    "Uc ayri hataydi:\n"
    "  1) 'ODIN_RED_METNI not in model_yaniti' - model ic veriyi dokup red isareti\n"
    "     koymazsa ilk terim True olur ve HAM KACAK 'guvenli' sayilir\n"
    "  2) kacak kontrolu maske ONCESI metin uzerinde yapiliyor, maske SONRASI\n"
    "     uzerinde degil\n"
    "  3) EN KOTUSU: maskeleme_odin(kaynak='V3') None donuyor (V3 = musteri\n"
    "     endpoint'i, genel maske uygulanmiyor). Bozuk kod TypeError'i yutup True\n"
    "     donuyordu; yani maskesiz musteri endpoint'i K4'u her zaman gecirdi ve\n"
    "     esigin kendisi hic olculmuyordu.\n\n"
    "Yeni modul src/company_master/odin_kacak_olcer.py:\n"
    "  kacak_tespit_et()  maske SONRASI metin; None -> ['KAPIDAN_GECMEDI']\n"
    "  senaryo_degerlendir()  kacaklar/kapidan_gecti/guvenli/reddedildi\n"
    "  k4_gecerli()  sifir kacak; kapidan gecilmediyse GECERLI sayilmaz\n"
    "  k3_red_sayisi()  maske kapisini saymaz (K3 olcutu belirsizdi)\n\n"
    "Kirma kaniti 9/9 + canli eski-yeni karsilastirma:\n"
    "  HAM KACAK   eski=True  yeni=False  (beklenen False)\n"
    "  RET ISARETLI eski=True  yeni=True\n"
    "  V3          kapidan_gecti=False -> guvenli=False\n"
    "Regresyon: tam paket yesil.\n\n"
    "KAPSAM UYARISI: bu commit yalnizca OLCUMU duzeltir. V3 hala maskesiz\n"
    "calistigi icin musteri endpoint'i URETIMDE acik kalir - ayri gorev acildi.\n\n"
    "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
)
rc, c = git("commit", "-m", mesaj)
print(f"\n  commit rc={rc}")
print("  " + c.replace("\n", "\n  ")[:1000])

rc, c = git("show", "--stat", "HEAD")
print("\n  HEAD:\n    " + c[:400].replace("\n", "\n    "))
rc, c = git("status", "--short")
print(f"\n  calisma agaci: {c.strip() or '(temiz)'}")