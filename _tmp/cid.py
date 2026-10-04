"""chat_gonder kimlik zinciri: OLC (kisim 1)."""
import inspect
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
C = KOK / "scripts" / "chat_gonder.py"
sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))

sat = C.read_text(encoding="utf-8", errors="replace").splitlines()
print(f"satir={len(sat)}")
print()
print("=== 1) ajan_kimligi() ===")
b = next((i for i, l in enumerate(sat) if "def ajan_kimligi" in l), None)
if b is not None:
    for n in range(b, min(b + 18, len(sat))):
        print(f"  {n+1}: {sat[n][:100]}")

print()
print("=== 2) 'kimden' gecien tum yerler ===")
for n, l in enumerate(sat, 1):
    if "kimden" in l:
        print(f"  {n}: {l.strip()[:100]}")

print()
print("=== 3) CANLI DAVRANIS — kim atanir? ===")
from scripts import chat_gonder as cg  # noqa: E402
for env in (None, "salih", "yasu"):
    import os
    if env is None:
        os.environ.pop("HUGINN_AJAN", None)
    else:
        os.environ["HUGINN_AJAN"] = env
    try:
        print(f"  HUGINN_AJAN={str(env):8s} -> ajan_kimligi() = {cg.ajan_kimligi()!r}")
    except Exception as e:
        print(f"  HUGINN_AJAN={str(env):8s} -> HATA {type(e).__name__}: {e}")

print()
print("=== 4) argparse varsayilani (--kimden verilmezse ne olur?) ===")
r = subprocess.run([sys.executable, "scripts/chat_gonder.py", "--help"],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", cwd=str(KOK), timeout=180)
for l in (r.stdout or "").splitlines():
    if "kimden" in l or "kime" in l:
        print("  " + l.strip()[:100])