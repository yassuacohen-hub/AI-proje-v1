# -*- coding: utf-8 -*-
"""nur yargic gorevi: yalniz kendi dosyalarini pathspec ile commit + dosya listesi. Cikti: Insights/_tmp/yargic_commit.txt"""
import subprocess, pathlib
KOK = pathlib.Path(r"c:/Huginn Data Projesi/Huginn Data Insights")
D = "data/orchestrator/"
ADAY = ["plans/brief_nur_MUSTERI-PANEL-YARGIC-01.md", D + "task_board.json", D + "pano_yazim_kaydi.jsonl",
        D + "chat/messages.jsonl", D + "triggers/nur.jsonl", D + "gorev_panosu.md", D + "file_locks.json"]
def g(*a):
    r = subprocess.run(["git", *a], cwd=KOK, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout + r.stderr).strip()
cik = []
var = [p for p in ADAY if (KOK / p).exists()]
cik.append("var: " + ", ".join(var))
rc, st = g("status", "--short", "--", *var)
cik.append("status:\n" + st)
degisen = var if st else []  # ponytail: strip() ilk satirin bosluguni yiyordu; durum satirini ayrisitirma
if degisen:
    g("add", "--", *degisen)
    rc, o = g("commit", "-m", "chore(nur): MUSTERI-PANEL-YARGIC-01 yargic gorevi + brif + tetik + chat", "--", *degisen)
    cik.append(f"commit rc={rc}\n{o[-600:]}")
(KOK / "_tmp" / "yargic_commit.txt").write_text("\n".join(cik), encoding="utf-8")
