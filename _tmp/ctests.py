"""Bu dosyada HANGI testler var? sabotaj testi gercekten var mi?"""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
T = KOK / "tests" / "test_yazma_kapisi.py"

sat = T.read_text(encoding="utf-8", errors="replace").splitlines()
print(f"test_yazma_kapisi.py: {len(sat)} satir")
print("\n--- icindeki test fonksiyonlari ---")
for n, l in enumerate(sat, 1):
    if l.startswith("def test"):
        print(f"  {n}: {l.strip()[:80]}")

print("\n--- 'sabotaj' gecen satirlar ---")
bul = [(n, l) for n, l in enumerate(sat, 1) if "sabotaj" in l.lower()]
print(f"  {len(bul)} adet")
for n, l in bul:
    print(f"  {n}: {l.strip()[:90]}")

print("\n--- pytest bu dosyada ne topluyor? ---")
r = subprocess.run([sys.executable, "-m", "pytest", str(T), "--collect-only", "-q",
                    "--no-header", "-p", "no:cacheprovider"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                   cwd=str(KOK), timeout=600)
for l in (r.stdout or "").strip().splitlines():
    if "::" in l or "test" in l.lower():
        print("  " + l.strip()[:90])

print("\n--- kazima test dosyasi ---")
T2 = KOK / "tests" / "test_kazima_qwen_classify.py"
s2 = T2.read_text(encoding="utf-8", errors="replace").splitlines()
print(f"satir={len(s2)}")
for n, l in enumerate(s2, 1):
    if l.startswith("def test") or "canli" in l.lower() or "skip" in l.lower() \
            or "environ" in l or "getenv" in l:
        print(f"  {n}: {l.strip()[:95]}")