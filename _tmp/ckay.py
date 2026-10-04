"""Kayip mi kontolu: gorev aciklamasi + TAŞIH kaydi duruyor mu, commit'li mi?"""
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
YENI = "ALTYAPI-ODIN-MASKE-V3-01"
ISARET = "TASHIH D-338: V3 bulgusu geri cekildi, asil bulgu zorunlu kapida"


def git(*a, timeout=300):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


print("=" * 68)
print("1) GOREV ACIKLAMASI — canli dosyada ne yaziyor?")
print("=" * 68)
v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
g = next((x for x in gs if x.get("id") == YENI), None)
if not g:
    print("  !! GOREV YOK")
else:
    print(f"  durum : {g.get('durum')}  ajan={g.get('ajan')}")
    print(f"  baslik: {g.get('baslik')}")
    a = str(g.get("aciklama", ""))
    print(f"  aciklama uzunlugu: {len(a)}")
    for bayrak in ["yanlitti", "ZORUNLU", "bilincil", "hicbir cagiran yok",
                   "URUM REGRESYONU", "geri CEKTIYOM"]:
        print(f"    {'var ' if bayrak.lower() in a.lower() else 'YOK '} {bayrak!r}")

print()
print("=" * 68)
print("2) COMMIT'LI MI? (git HEAD ile karsilastir)")
print("=" * 68)
rc, head = git("show", "HEAD:data/orchestrator/task_board.json")
print(f"  HEAD'de task_board.json var mi : {bool(head)}")
if head:
    hv = json.loads(head)
    hgs = hv if isinstance(hv, list) else hv.get("gorevler", [])
    hg = next((x for x in hgs if x.get("id") == YENI), None)
    if not hg:
        print("  !! HEAD surumunde bu GOREV YOK (aciklamam commit'lenmemis)")
    else:
        ha = str(hg.get("aciklama", ""))
        print(f"  HEAD'de durum: {hg.get('durum')}")
        print(f"  HEAD aciklama uzunlugu: {len(ha)}")
        print(f"  HEAD aciklama == canli aciklama : {ha == str(g.get('aciklama',''))}")
        for bayrak in ["yanlitti", "ZORUNLU", "bilincil"]:
            print(f"    HEAD'de {bayrak!r}: {bayrak.lower() in ha.lower()}")

print()
print("=" * 68)
print("3) BULGU DEFTERI — TAŞIH kaydi duruyor mu?")
print("=" * 68)
d = (O / "bulgu_defteri.md").read_text(encoding="utf-8", errors="replace")
print(f"  ISARET sayisi: {d.count(ISARET)}")
print(f"  'geri cekildi' geciyor mu: {'geri' in d.lower()}")
rc, hd = git("show", "HEAD:data/orchestrator/bulgu_defteri.md")
print(f"  HEAD'de ISARET sayisi: {hd.count(ISARET) if hd else '(yok)'}")

print()
print("=" * 68)
print("4) AJAN CHAT — TAŞIH kaydi")
print("=" * 68)
y = (O / "ajan-chat.jsonl").read_text(encoding="utf-8", errors="replace")
print(f"  'TASHIH: V3 bulgumu geri' geciyor mu: {'TASHIH: V3 bulgumu geri' in y}")
sat = [json.loads(x) for x in y.splitlines() if x.strip()]
for r in sat[-4:]:
    print(f"  [{r.get('kimden')}->{r.get('ajan')}] {r.get('durum')} :: "
          f"{str(r.get('sorun'))[:60]}")

print()
print("=" * 68)
print("5) git durumu")
print("=" * 68)
rc, s = git("status", "--short")
print("  " + (s.strip() or "(temiz)"))
rc, c = git("log", "--oneline", "-3")
print("  " + c.replace("\n", "\n  "))