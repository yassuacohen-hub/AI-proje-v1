"""pull --rebase + push donguusu. ajan-chat.jsonl cakismasinda iki tarafi tutar (append-only)."""
import json
import subprocess
import sys

KOK = r"c:\Huginn Data Projesi\Huginn Data Insights"
CHAT = "data/orchestrator/ajan-chat.jsonl"
DAL = "chore/monorepo-merge"


def git(*a):
    r = subprocess.run(["git", "-c", "core.editor=true", *a], cwd=KOK, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr)


RANK = {"cozuldu": 2, "cokundurmus": 1, "acik": 0}


def anahtar_birlestir(sat):
    """Ayni (kimden,ajan,task_id,sorun) tek satir: cozuldu > cokundurmus > acik, esitse en gec timestamp.
    ponytail: iki taraf kopyasi sisirmesini (3726->409) onler; stabil satir kimligi gelirse bu gerekmez."""
    en, sira = {}, []
    for s in sat:
        if not s.strip():
            continue
        d = json.loads(s)
        k = (d.get("kimden"), d.get("ajan"), d.get("task_id"), d.get("sorun"))
        if k not in en:
            sira.append(k)
        o = (RANK.get(d.get("durum"), 0), str(d.get("timestamp", "")))
        if k not in en or o >= en[k][0]:
            en[k] = (o, s)
    return [en[k][1] if en[k][1].endswith("\n") else en[k][1] + "\n" for k in sira]


assert anahtar_birlestir(
    ['{"ajan":"a","sorun":"s","durum":"acik","timestamp":"2"}\n', '{"ajan":"a","sorun":"s","durum":"cozuldu","timestamp":"1"}\n']
) == ['{"ajan":"a","sorun":"s","durum":"cozuldu","timestamp":"1"}\n']


def cakisma_coz():
    yol = KOK + "\\" + CHAT.replace("/", "\\")
    with open(yol, encoding="utf-8", newline="") as f:
        sat = f.read().splitlines(keepends=True)
    cik = [s for s in sat if not (s.startswith(("<<<<<<< ", ">>>>>>> ")) or s.rstrip("\r\n") == "=======")]
    cik = anahtar_birlestir(cik)
    with open(yol, "w", encoding="utf-8", newline="") as f:
        f.writelines(cik)


for deneme in range(1, 6):
    rc, out = git("pull", "--rebase", "--autostash", "origin", DAL)
    print(deneme, "pull rc", rc)
    while rc != 0:
        _, un = git("diff", "--name-only", "--diff-filter=U")
        un = un.split()
        if un != [CHAT]:
            print("COZULEMEYEN CAKISMA:", un, out[-400:])
            sys.exit(1)
        cakisma_coz()
        git("add", CHAT)
        rc, out = git("rebase", "--continue")
    rc, out = git("push", "origin", f"HEAD:{DAL}")
    print("push rc", rc, out[-300:])
    if rc == 0:
        sys.exit(0)
sys.exit(2)
