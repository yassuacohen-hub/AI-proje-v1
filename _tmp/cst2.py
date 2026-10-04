"""Durum olcumu: git + pano + iki chat kanali + bekleyen isler."""
import json
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


print("=" * 68)
print("1) GIT")
print("=" * 68)
rc, c = git("log", "--oneline", "-6")
print("  " + c.replace("\n", "\n  "))
rc, s = git("status", "--short")
print(f"\n  calisma agaci: {len([x for x in s.splitlines() if x.strip()])} degisiklik")
for x in [x for x in s.splitlines() if x.strip()][:12]:
    print(f"    {x[:95]}")

print()
print("=" * 68)
print("2) PANO")
print("=" * 68)
v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
say = {}
for g in gs:
    say[g.get("durum")] = say.get(g.get("durum"), 0) + 1
print(f"  toplam {len(gs)} | " + " ".join(f"{k}={n}" for k, n in
                                           sorted(say.items(), key=lambda x: -x[1])))
print("\n  AKTIF/DEVAM olanlar:")
for g in gs:
    if g.get("durum") in ("aktif", "devam", "yeni", "atanmis", "atandı"):
        print(f"    [{g.get('durum'):7s}] {g.get('id'):<34s} ajan={g.get('ajan')}")

print()
print("=" * 68)
print("3) ODIN — kapinin durumu")
print("=" * 68)
for g in gs:
    if g.get("id", "").startswith("ALTYAPI-ODIN"):
        print(f"  [{g.get('durum'):8s}] {g.get('id'):<32s} ajan={g.get('ajan')}")

print()
print("=" * 68)
print("4) AJAN CHAT — son 10 (ajan-chat.jsonl)")
print("=" * 68)
sat = [json.loads(x) for x in (O / "ajan-chat.jsonl").read_text(
    encoding="utf-8", errors="replace").splitlines() if x.strip()]
print(f"  toplam {len(sat)}")
for r in sat[-10:]:
    print(f"  [{r.get('kimden'):>7s}->{r.get('ajan'):<7s}] {str(r.get('task_id'))[:26]:<26s} "
          f"{r.get('durum'):<7s} :: {str(r.get('sorun'))[:52]}")

print()
print("=" * 68)
print("5) CHAT GONDER — son 8 (messages.jsonl)")
print("=" * 68)
s2 = [json.loads(x) for x in (O / "chat" / "messages.jsonl").read_text(
    encoding="utf-8", errors="replace").splitlines() if x.strip()]
print(f"  toplam {len(s2)}")
for r in s2[-8:]:
    print(f"  [{r.get('kimden'):>7s}->{str(r.get('kime')):<7s}] "
          f"{str(r.get('task_id'))[:20]:<20s} :: {str(r.get('mesaj'))[:56]}")

print()
print("=" * 68)
print("6) tur/mahiyet dolulugu (D-338 2. katman canli mi?)")
print("=" * 68)
dolu = sum(1 for r in s2 if r.get("tur") or r.get("mahiyet"))
print(f"  {dolu}/{len(s2)} kayit tur/mahiyet tasiyor")

print()
print("=" * 68)
print("7) BEKLEDIGIM / ACIK KAYITLARIM")
print("=" * 68)
acik = [r for r in sat if r.get("kimden") == "yasu" and r.get("durum") == "acik"]
for r in acik:
    print(f"  -> {r.get('ajan'):<7s} {r.get('task_id'):<28s} onem={r.get('onem')}")
print(f"  toplam: {len(acik)}")