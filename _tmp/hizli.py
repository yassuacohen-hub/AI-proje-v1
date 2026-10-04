"""HIZLI: nobet + posta + chat."""
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"


def sh(*a):
    r = subprocess.run([sys.executable, *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=300)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


rc, c = sh("scripts/gorev_kutusu.py", "nobet", "--ajan", "yasu")
print(f"NOBET rc={rc} {'IS VAR' if rc == 0 else 'yok'}")
print("  " + c.strip()[:400].replace("\n", "\n  "))

v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
benim = [g for g in gs if g.get("ajan") == "yasu"]
print(f"\nPANO: ajan=yasu {len(benim)} gorev")
for g in benim:
    print(f"  [{g.get('durum'):9s}] {g.get('id')}")

sat = [json.loads(x) for x in (O / "ajan-chat.jsonl").read_text(
    encoding="utf-8", errors="replace").splitlines() if x.strip()]
acik = [r for r in sat if r.get("durum") == "acik"]
yeni = [r for r in acik if r.get("ajan") == "yasu"]
print(f"\nCHAT: acik {len(acik)} | bana yonelik {len(yeni)}")
for r in yeni[-4:]:
    print(f"  [{r.get('kimden')}->{r.get('ajan')}] {r.get('task_id')} :: {str(r.get('sorun'))[:60]}")

s2 = [json.loads(x) for x in (O / "chat" / "messages.jsonl").read_text(
    encoding="utf-8", errors="replace").splitlines() if x.strip()]
print(f"\nCHAT_GONDER son 3:")
for r in s2[-3:]:
    print(f"  [{r.get('kimden')}->{r.get('kime')}] {str(r.get('mesaj'))[:70]}")