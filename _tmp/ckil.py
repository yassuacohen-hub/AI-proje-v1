"""test_senaryo duzeltmesi oncesi: kilit + maskeleme_odin gercek imzasi/eylemi."""
import hashlib
import inspect
import json
import re
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = KOK / "docs" / "ODIN_PROMPT_INJECTION_SCENARIOS.md"
S = KOK / "src" / "company_master" / "sunum.py"

print("=== 1) KILIT DURUMU ===")
kilit = json.loads((KOK / "data" / "orchestrator" / "file_locks.json").read_text(
    encoding="utf-8", errors="replace"))
for yol, k in kilit.items():
    if "ODIN" in yol or "sunum.py" in yol:
        print(f"  {yol}\n    sahip={k.get('sahip')} task={k.get('task_id')} "
              f"kilitlendi={k.get('kilitlendi')}")
bulundu = any("ODIN" in y or "sunum.py" in k for k in kilit for y in [k])
print(f"  ilgili kilit sayisi: {sum(1 for y in kilit if 'ODIN' in y or 'sunum.py' in y)}")

print()
print("=== 2) maskeleme_odin GERCEK IMZASI + GOVDE ===")
sat = S.read_text(encoding="utf-8", errors="replace").splitlines()
bas = next((i for i, l in enumerate(sat) if "def maskeleme_odin" in l), None)
if bas is None:
    print("  !! maskeleme_odin bulunamadi")
else:
    print(f"  tanim satiri: {bas + 1}")
    for n in range(bas, min(bas + 55, len(sat))):
        print(f"   {n+1}: {sat[n][:100]}")
        if re.match(r"^\s{0,4}def \w", sat[n]) and n > bas:
            break

print()
print("=== 3) IC DESENLER (maskede ne temizleniyor?) ===")
for n, l in enumerate(sat, 1):
    if "ODIN_RED_METNI" in l or "[İÇ VERİ" in l or "IC VERI" in l:
        print(f"  {n}: {l.strip()[:100]}")

print()
print("=== 4) BOZUK YARDIMCI (duzeltilecek yer) ===")
d = D.read_text(encoding="utf-8", errors="replace").splitlines()
for n, l in enumerate(d, 1):
    if "def test_senaryo" in l or "guvenli" in l or "ODIN_RED_METNI" in l:
        print(f"  {n}: {l[:100]}")
print(f"\n  dosya sha = {hashlib.sha256(D.read_bytes()).hexdigest()[:16]}")