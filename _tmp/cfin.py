"""Commit durumu + ihsan'a devralma yazisi (bulgu defteri + ajan chat)."""
import hashlib
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"


def git(*a, timeout=300):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


print("=== COMMIT DURUMU ===")
rc, c = git("log", "--oneline", "-5")
print("  " + c.replace("\n", "\n  "))
rc, c = git("status", "--short")
print(f"\n  calisma agaci: {c.strip() or '(temiz)'}")
G = KOK / "scripts" / "gorev_kutusu.py"
C = KOK / "scripts" / "chat_gonder.py"
print(f"\n  gorev_kutusu.py sha = {hashlib.sha256(G.read_bytes()).hexdigest()[:16]}")
print(f"  chat_gonder.py  sha = {hashlib.sha256(C.read_bytes()).hexdigest()[:16]}")
print(f"  chat_gonder.py HEAD'de mi: "
      f"{'evet' if git('cat-file', '-e', 'HEAD:scripts/chat_gonder.py')[0] == 0 else 'HAYIR - commit lenmedi'}")
rc, c = git("show", "--stat", "HEAD")
print("\n  HEAD:\n    " + c[:300].replace("\n", "\n    "))