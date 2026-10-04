"""keyring'in SICAK YOLDA nerede okundugunu bul."""
import re
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
M = KOK / "scripts" / "kazima_qwen_classify.py"
sat = M.read_text(encoding="utf-8", errors="replace").splitlines()
print(f"satir={len(sat)}")
print("\n=== KEYRING / get_password / _env_oku cagri yerleri ===")
for n, l in enumerate(sat, 1):
    if "KEYRING" in l or "get_password" in l or "_env_oku(" in l or "_anahtar_bir(" in l:
        print(f"  {n:3d}: {l.rstrip()[:100]}")

print("\n=== sinifla_etiket GOVDESI ===")
b = next((i for i, l in enumerate(sat) if "def sinifla_etiket" in l), None)
if b:
    for n in range(b, min(b + 42, len(sat))):
        print(f"  {n+1}: {sat[n][:100]}")