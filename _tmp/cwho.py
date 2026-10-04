"""KIRILMA BENIM MI? degisikligi geri al, ayni 2 testi kos."""
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
M = KOK / "scripts" / "kazima_qwen_classify.py"
TESTS = ["tests/test_yazma_kapisi.py", "tests/test_kazima_qwen_classify.py"]


def git(*a, timeout=600):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def kos(etiket):
    r = subprocess.run([sys.executable, "-m", "pytest", *TESTS, "-q",
                        "--no-header", "-p", "no:cacheprovider", "--tb=line"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(KOK), timeout=900)
    out = [l for l in (r.stdout or "").strip().splitlines() if l.strip()]
    print(f"\n  [{etiket}] rc={r.returncode}")
    for l in out[-4:]:
        print("    " + l[:110])
    for l in (r.stdout or "").splitlines():
        if l.startswith("FAILED") or l.startswith("E   "):
            print("      >> " + l.strip()[:120])
    return r.returncode


print("A) DEGISIKLIKLI HALI (benim onbellek eklenmis)")
a = kos("onbellekli")

print()
print("B) DEGISIKLIK YOK HALI (git HEAD surumu)")
yede = M.with_suffix(".py.yedek")
shutil.copy2(M, yede)
rc, c = git("show", "HEAD:scripts/kazima_qwen_classify.py")
M.write_text(c, encoding="utf-8")
print(f"  geri alindi: sha={hashlib.sha256(M.read_bytes()).hexdigest()[:16]}")
b = kos("HEAD (onbelleksiz)")

print()
print("C) KARAR")
print("=" * 60)
if a == 0:
    print("  onbellekli: YESIL -> sorun baska yerde")
elif b == 0:
    print("  !! KIRILMA BENIM _anahtar_bir DEGISIKLIGIMDEN")
else:
    print("  !! IKISI DE KIRIK -> onceden beri kirik, benim hatam degil")

shutil.copy2(yede, M)
yede.unlink(missing_ok=True)
print(f"\n  geri yuklendi: sha={hashlib.sha256(M.read_bytes()).hexdigest()[:16]}")