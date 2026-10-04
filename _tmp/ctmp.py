"""KURULDU: scriptler _tmp/ altina. Dogrula + tasi."""
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
TMP = KOK / "_tmp"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
EVS = Path(r"C:\Users\yasin")


def git(*a, timeout=300):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


print("=== 1) _tmp/ var mi? .gitignore'da mi? ===")
print(f"  _tmp klasoru : {TMP.is_dir()}")
if TMP.is_dir():
    print(f"  icerik       : {len(list(TMP.iterdir()))} dosya")
_, ig = git("check-ignore", "-v", "_tmp/x.py")
print(f"  .gitignore    : {ig.strip() or ('KAYITLI - commitlenir!' if ig else 'yok')}")
_, gl = git("ls-files", "_tmp")
print(f"  git'te takip  : {len(gl.splitlines()) if gl else 0} dosya")

print()
print("=== 2) COMMAND_KURALLARI.md'de _tmp kurali var mi? ===")
d = KOK / "docs" / "COMMAND_KURALLARI.md"
if d.is_file():
    t = d.read_text(encoding="utf-8", errors="replace").splitlines()
    bul = [(n, l) for n, l in enumerate(t, 1) if "_tmp" in l]
    print(f"  _tmp gecen satir: {len(bul)}")
    for n, l in bul[:8]:
        print(f"    {n}: {l.strip()[:95]}")
else:
    print("  dosya yok")

print()
print("=== 3) betikleri _tmp/ altina tasi ===")
TMP.mkdir(exist_ok=True)
tasinan = 0
for f in sorted(EVS.glob("*.py")) + sorted(EVS.glob("*.bat")):
    hedef = TMP / f.name
    shutil.copy2(f, hedef)
    tasinan += 1
print(f"  {tasinan} dosya _tmp/ altina kopyalandi")
print(f"  _tmp/ icerigi: {sorted(x.name for x in TMP.iterdir())[:14]}")

print()
print("=== 4) dogrulama: _tmp/ dosyalari calisiyor mu? ===")
ornek = TMP / "cver2.py"
if ornek.is_file():
    r = subprocess.run([sys.executable, str(ornek)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(KOK), timeout=300)
    print(f"  {ornek.name}: rc={r.returncode}")
    for l in (r.stdout or "").strip().splitlines()[:6]:
        print("    " + l[:95])