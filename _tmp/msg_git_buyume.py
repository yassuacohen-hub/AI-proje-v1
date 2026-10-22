# -*- coding: utf-8 -*-
"""messages.jsonl commit basina satir sayisi (en eski -> yeni). Cikti dosyaya, iki nokta yok."""
import subprocess

P = "data/orchestrator/chat/messages.jsonl"
log = subprocess.run(
    ["git", "log", "--format=%h|%ad|%s", "--date=format:%d-%H.%M", "-40", "--", P],
    capture_output=True, text=True, encoding="utf-8",
).stdout.splitlines()
cikti = []
for satir in reversed(log):
    h, tarih, konu = satir.split("|", 2)
    r = subprocess.run(["git", "show", f"{h}:{P}"], capture_output=True, encoding="utf-8", errors="replace")
    n = len(r.stdout.splitlines()) if r.returncode == 0 else -1
    cikti.append(f"{h} {tarih} satir={n} {konu[:70]}")
with open("../_tmp/msg_git_buyume.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(cikti) + "\n")
