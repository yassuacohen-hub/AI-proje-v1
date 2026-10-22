"""ajan-chat.jsonl stash cakismasini coz: upstream korunur, ayni kayit stash'te kapaliysa kapali surum alinir."""
import json
import subprocess

KOK = r"c:\Huginn Data Projesi\Huginn Data Insights"
YOL = KOK + r"\data\orchestrator\ajan-chat.jsonl"

with open(YOL, encoding="utf-8-sig", newline="") as f:
    sat = f.read().split("\n")

cikti, up, st, mod = [], [], [], None


def anahtar(s):
    r = json.loads(s)
    return (r.get("kimden"), r.get("ajan"), r.get("task_id"), r.get("sorun"))


def birlestir():
    kapali = {}
    for s in st:
        if s.strip():
            kapali[anahtar(s)] = s
    out = []
    for s in up:
        if not s.strip():
            continue
        k = anahtar(s)
        out.append(kapali.pop(k, s))
    out.extend(kapali.values())  # upstream'de olmayan stash kayitlari
    return out


for s in sat:
    ham = s.rstrip("\r")
    if ham.startswith("<<<<<<< "):
        mod, up, st = "up", [], []
    elif ham == "=======" and mod == "up":
        mod = "st"
    elif ham.startswith(">>>>>>> ") and mod == "st":
        cikti.extend(birlestir())
        mod = None
    elif mod == "up":
        up.append(ham)
    elif mod == "st":
        st.append(ham)
    else:
        cikti.append(ham)

for s in cikti:
    if s.strip():
        json.loads(s)  # bozuk satir varsa burada patlar, dosya yazilmaz

with open(YOL, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(cikti))
    if cikti and cikti[-1] != "":
        f.write("\n")
print("satir:", len(cikti))
subprocess.run(["git", "add", "data/orchestrator/ajan-chat.jsonl"], cwd=KOK, check=True)
print("git add tamam")
