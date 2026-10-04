"""keyring cagisini bul + tek seferlik onbelleg ekle + yeniden olc."""
import hashlib
import re
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
M = KOK / "scripts" / "kazima_qwen_classify.py"
sat = M.read_text(encoding="utf-8", errors="replace").splitlines()
print(f"sha256 = {hashlib.sha256(M.read_bytes()).hexdigest()[:16]}")
print(f"satir  = {len(sat)}\n")

print("=== 1) keyring kullanimi ===")
for n, l in enumerate(sat, 1):
    if "keyring" in l or "anahtar_var" in l or "API_KEY" in l:
        print(f"  {n}: {l.strip()[:100]}")

print("\n=== 2) anahtar_var GOVDESI ===")
b = next((i for i, l in enumerate(sat) if "def anahtar_var" in l), None)
if b is None:
    b = next((i for i, l in enumerate(sat) if re.search(r"def .*anahtar", l)), None)
if b is not None:
    for n in range(b, min(b + 32, len(sat))):
        print(f"  {n+1}: {sat[n][:100]}")
        if n > b and re.match(r"^\S", sat[n]):
            break