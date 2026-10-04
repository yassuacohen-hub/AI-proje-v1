"""Commit dogrula + test sayimi dogrula + V3 gorevini ac."""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def git(*a, timeout=300):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


print("=== 1) COMMIT DOGRULAMASI ===")
rc, c = git("log", "--oneline", "-4")
print("  " + c.replace("\n", "\n  "))
rc, c = git("status", "--short")
print(f"\n  calisma agaci:\n    " + (c.strip() or "(temiz)").replace("\n", "\n    "))
rc, s = git("show", "--stat", "HEAD")
print(f"\n  HEAD --stat:\n    " + s[:400].replace("\n", "\n    "))
yeni = git("cat-file", "-e", "HEAD:src/company_master/odin_kacak_olcer.py")[0] == 0
print(f"\n  odin_kacak_olcer.py HEAD'de mi : {'EVET' if yeni else 'HAYIR'}")

print()
print("=== 2) TEST SAYIMI DOGRULAMASI ===")
r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_odin_kacak_olcer.py",
     "--collect-only", "-q", "--no-header", "-p", "no:cacheprovider"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(KOK), timeout=600)
sat = [l for l in (r.stdout or "").splitlines() if "::" in l]
print(f"  yeni dosyada toplanan test : {len(sat)}")
for l in sat:
    print(f"    {l.strip()[:70]}")

r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q",
     "--no-header", "-p", "no:cacheprovider"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(KOK), timeout=600)
toplam = len([l for l in (r.stdout or "").splitlines() if "::" in l])
print(f"  tum paket toplam test     : {toplam}")

print()
print("=== 3) gorev_kutusu ekle --help (arguman ogren) ===")
r = subprocess.run([sys.executable, "scripts/gorev_kutusu.py", "ekle", "--help"],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", cwd=str(KOK), timeout=300)
print("  " + ((r.stdout or "") + (r.stderr or ""))[:1200].replace("\n", "\n  "))