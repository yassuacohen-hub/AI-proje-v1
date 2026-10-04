"""ACIL: chat_gonder.py silinmis mi? (git + disk)."""
import hashlib
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
C = KOK / "scripts" / "chat_gonder.py"


def git(*a, timeout=300):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


print("=== 1) chat_gonder.py diskte var mi? ===")
print(f"  is_file = {C.is_file()}")
if C.is_file():
    print(f"  boyut   = {C.stat().st_size}")
    print(f"  sha     = {hashlib.sha256(C.read_bytes()).hexdigest()[:16]}")
else:
    print("  !! DOSYA YOK - SILINMIS")

rc, c = git("status", "--short", "--", "scripts/chat_gonder.py")
print(f"\n  git status: {c!r}")

rc, c = git("log", "--oneline", "-3", "--", "scripts/chat_gonder.py")
print(f"\n  commit gecmisi:\n    " + (c or "(yok)").replace("\n", "\n    "))

rc, c = git("show", "HEAD:scripts/chat_gonder.py")
print(f"\n  HEAD surumu: {len(c.splitlines())} satir")
tur = [l for l in c.splitlines() if "mahiyet" in l or '"tur"' in l]
print(f"  HEAD'de tur/mahiyet ({len(tur)} satir):")
for l in tur[:6]:
    print(f"    {l.strip()[:90]}")

print("\n=== 2) calisma agaci ozeti ===")
rc, c = git("status", "--short")
s = c.splitlines()
print(f"  toplam degisiklik: {len(s)}")
for l in s[:15]:
    print(f"    {l[:95]}")