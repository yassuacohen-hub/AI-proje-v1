"""V3 maske atlama nedeni: genel_maske + kaynak dagilimi (OLC)."""
import sys
from collections import Counter
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(KOK / "src"))
S = KOK / "src" / "company_master" / "sunum.py"

sat = S.read_text(encoding="utf-8", errors="replace").splitlines()
print(f"sunum.py satir={len(sat)}")

print()
print("=" * 70)
print("1) genel_maske GOVDESI")
print("=" * 70)
bas = next((i for i, l in enumerate(sat) if "def genel_maske" in l), None)
if bas is None:
    print("  YOK")
else:
    for n in range(bas, min(bas + 45, len(sat))):
        print(f"  {n+1}: {sat[n][:105]}")

print()
print("=" * 70)
print("2) maskeleme_odin: kaynak dagiti / V3 dalı")
print("=" * 70)
bas = next((i for i, l in enumerate(sat) if "def maskeleme_odin" in l), None)
for n in range(bas, min(bas + 60, len(sat))):
    print(f"  {n+1}: {sat[n][:105]}")

print()
print("=" * 70)
print("3) KOD ICINDE 'V3' KULLANIMI (kim, nerede)")
print("=" * 70)
for p in KOK.rglob("*.py"):
    if any(x in p.parts for x in (".venv", "node_modules", ".git")):
        continue
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    if '"V3"' in t or "'V3'" in t:
        for n, l in enumerate(t.splitlines(), 1):
            if '"V3"' in l or "'V3'" in l:
                print(f"  {p.relative_to(KOK)}:{n}: {l.strip()[:90]}")

print()
print("=" * 70)
print("4) KAYNAK DEGERLERI DAGILIMI (cagirmalarda ne geciliyor?)")
print("=" * 70)
say = Counter()
for p in KOK.rglob("*.py"):
    if any(x in p.parts for x in (".venv", "node_modules", ".git")):
        continue
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    if "maskeleme_odin(" in t:
        for l in t.splitlines():
            if "maskeleme_odin(" in l:
                say[l.strip()[:95]] += 1
for l, c in say.most_common(20):
    print(f"  {c:3d}x  {l}")