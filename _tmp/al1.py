"""1) Postayi al  2) SORULARI oku (tam metin)  3) Tetigi baslat."""
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


print("=== 1) POSTA AL ===")
rc, c = sh("scripts/gorev_kutusu.py", "al", "--ajan", "yasu",
           "--task-id", "ALTYAPI-9ROUTER-MITM-PATCH-01")
print(f"  rc={rc} :: {c.strip()[:300]}")

print("\n=== 2) SORULARIN TAM METNI ===")
sat = [json.loads(x) for x in (O / "ajan-chat.jsonl").read_text(
    encoding="utf-8", errors="replace").splitlines() if x.strip()]
for i, r in enumerate(sat, 1):
    if r.get("ajan") == "yasu" and r.get("durum") == "acik":
        print(f"\n--- #{i} {r.get('task_id')} (onem={r.get('onem')}) ---")
        print(f"SORUN: {str(r.get('sorun'))[:400]}")
        print(f"COZUM: {str(r.get('cozum'))[:700]}")

print("\n=== 3) chat_gonder'dan bana gelen son mesajlar ===")
s2 = [json.loads(x) for x in (O / "chat" / "messages.jsonl").read_text(
    encoding="utf-8", errors="replace").splitlines() if x.strip()]
for r in s2:
    if r.get("kime") == "yasu" and not r.get("yanit_alindi"):
        print(f"\n[{r.get('kimden')}->{r.get('kime')}] {r.get('task_id')}")
        print(f"  {str(r.get('mesaj'))[:500]}")

print("\n=== 4) PANO durumu ===")
v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
for g in gs:
    if g.get("id") in ("ALTYAPI-9ROUTER-MITM-PATCH-01", "ALTYAPI-RAG-EMBEDDER-01",
                       "VERI-OSB-TAZELIK-01", "BORC-TAHSIS-ZORLAMA-01"):
        print(f"  [{g.get('durum'):9s}] {g.get('id'):<34s} ajan={g.get('ajan')}")