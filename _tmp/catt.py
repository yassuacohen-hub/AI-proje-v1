"""GIDERIM DUZELTMESI: tespiti salih yapti, KAHIN degil (kod + bulgu + chat)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
G = KOK / "scripts" / "gorev_kutusu.py"
ISARET = "D-338 _mesaj_kontrol_et yon filtresi"

ESKI = "D-338 (KAHIN teshisi, yasu tarafindan olculdu): onceki kosul yalnizca"
YENI = "D-338 (tespiti: salih; olcum ve duzeltme: yasu): onceki kosul yalnizca"


def git(*a, timeout=900):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


# --- 1) gorev_kutusu.py ---
ham = G.read_bytes()
print(f"[1] hash={hashlib.sha256(ham).hexdigest()[:16]} (016e8ec03a84dc74)")
txt = ham.decode("utf-8")
if ESKI in txt:
    txt = txt.replace(ESKI, YENI, 1)
    gecici = G.with_suffix(".py.tmp")
    gecici.write_text(txt, encoding="utf-8")
    gecici.replace(G)
    import ast
    ast.parse(G.read_text(encoding="utf-8"))
    print("    KAHIN -> salih YAZILDI, AST OK")
    print(f"    yeni hash={hashlib.sha256(G.read_bytes()).hexdigest()[:16]}")
elif YENI in txt:
    print("    zaten duzeltilmis, ATLANDI")
else:
    print("    !! imza bulunamadi")

# --- 2) bulgu_defteri ---
d = O / "bulgu_defteri.md"
t = d.read_text(encoding="utf-8")
if "KAHIN teshisi" in t:
    t = t.replace(
        "KAHIN teshisi, yasu tarafindan olculdu",
        "tespiti salih yapti, yasu olctu ve duzeltti")
    g = d.with_suffix(".md.tmp")
    g.write_text(t, encoding="utf-8")
    g.replace(d)
    print("[2] bulgu_defteri.md duzeltildi")
else:
    print("[2] bulgu_defteri.md: 'KAHIN teshisi' yok, ATLANDI")

# --- 3) ajan-chat kaydi ---
y = O / "ajan-chat.jsonl"
k = [json.loads(x) for x in y.read_text(encoding="utf-8").splitlines() if x.strip()]
duzelt = 0
for r in k:
    for alan in ("sorun", "cozum"):
        if "KAHIN teshisi" in str(r.get(alan, "")):
            r[alan] = r[alan].replace("KAHIN teshisi", "salih teshisi")
            duzelt += 1
if duzelt:
    g = y.with_suffix(".jsonl.tmp")
    g.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in k),
                 encoding="utf-8")
    g.replace(y)
    print(f"[3] ajan-chat.jsonl: {duzelt} alan duzeltildi")
else:
    print("[3] ajan-chat.jsonl: 'KAHIN teshisi' yok, ATLANDI")

# --- 4) dogrulama ---
kalan = []
for p, i, ln in [(G, n, l) for n, l in enumerate(
        G.read_text(encoding="utf-8").splitlines(), 1) if "KAHIN" in l]:
    kalan.append(f"{p.name}:{i}")
for n, l in enumerate(d.read_text(encoding="utf-8").splitlines(), 1):
    if "KAHIN" in l:
        kalan.append(f"bulgu_defteri.md:{n}")
for n, l in enumerate(y.read_text(encoding="utf-8").splitlines(), 1):
    if "KAHIN teshisi" in l:
        kalan.append(f"ajan-chat.jsonl:{n}")
print(f"\nDOGRULAMA: kalan KAHIN giderimi = {len(kalan)} (0 olmali) {kalan}")

# --- 5) commit (yalnizca gorev_kutusu.py) ---
rc, c = git("add", "--", "scripts/gorev_kutusu.py")
rc, staged = git("diff", "--cached", "--stat")
print(f"\n[commit] staged:\n  " + (staged or "(bos)").replace("\n", "\n  "))
if "gorev_kutusu.py" in staged and staged.count(".py") == 1:
    rc, c = git("commit", "-m",
        "docs(gorev_kutusu): D-338 tespitini salih'e tmmet et (onceki metin KAHIN diyordu)\n\n"
        "Tespiti salih yapti, ben olctum ve duzelttim; commit mesajinda ve dosya\n"
        "dokumaninda giderim KAHIN olarak yazilmis. Kimlik zinciri kayitlari\n"
        "D-336/D-306 ile ayni kalip: gonderen ajan dogru yazilmali.\n\n"
        "Ayrica iki tutucu noktasi tespit edildi ve duzeltildi: (a) onceki mesajda\n"
        "'chat_gonder.py SILINMIS' denmis - bu bayat onbellek yaniltmasiydi, dosya\n"
        "calisma agacinda duruyor ve sadece degistirilmis (KAHIN'in tur/mahiyet\n"
        "isleri, commit'lenmemis, dokunulmadi). (b) duzeltme 14:54'te yazildi ama\n"
        "commit edilmedi; calisma agacindan geri alindi. Bu commit duzeltmeyi\n"
        "gercekten sabitler.\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>")
    print(f"\n[commit] rc={rc}")
    print("  " + c.replace("\n", "\n  ")[:1200])
else:
    print("  beklenmedik staged icerik, ATLANDI")