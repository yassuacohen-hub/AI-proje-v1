"""chat_gonder.py'yi AYRI commit et; once durum + diff incele."""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def git(*a, timeout=300):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


print("=== 1) TUM CALISMA AGACI (ne var, ne yok) ===")
rc, c = git("status", "--short")
s = [x for x in c.splitlines() if x.strip()]
print(f"  toplam: {len(s)}")
for x in s:
    print(f"    {x[:100]}")

print()
print("=" * 70)
print("2) chat_gonder.py DIFF (neyi commit ediyoruz)")
print("=" * 70)
rc, d = git("diff", "--", "scripts/chat_gonder.py")
sat = d.splitlines()
print(f"  diff satiri: {len(sat)}")
print(f"  eklenen: {sum(1 for l in sat if l.startswith('+') and not l.startswith('+++'))}"
      f"  silinen: {sum(1 for l in sat if l.startswith('-') and not l.startswith('---'))}")
for l in sat[:80]:
    print("   ", l[:100])

print()
print("=== 3) chat_gonder.py YALNIZCA MI? ===")
rc, staged = git("diff", "--cached", "--stat")
print(f"  onceden staged: {staged or '(bos)'}")