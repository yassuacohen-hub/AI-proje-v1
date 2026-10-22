# -*- coding: utf-8 -*-
"""ajan-chat.jsonl dogrula (satir+json+marker) ve yalniz o dosyayi pathspec ile commit et. Sonuc: _tmp/chat_commit.txt"""
import json
import subprocess

KOK = r"c:\Huginn Data Projesi\Huginn Data Insights"
CHAT = "data/orchestrator/ajan-chat.jsonl"
cikti = []


def git(*a):
    r = subprocess.run(["git", *a], cwd=KOK, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr).strip()


with open(KOK + "\\" + CHAT.replace("/", "\\"), encoding="utf-8") as f:
    sat = [s for s in f.read().splitlines() if s.strip()]
bozuk = 0
for s in sat:
    try:
        json.loads(s)
    except ValueError:
        bozuk += 1
marker = sum(1 for s in sat if s.startswith(("<<<<<<<", ">>>>>>>", "=======")))
cikti.append(f"satir={len(sat)} bozuk={bozuk} marker={marker}")
assert bozuk == 0 and marker == 0 and len(sat) == 409, cikti
rc, out = git("commit", "-m", "chore(chat): ajan-chat.jsonl anahtar-dedupe 3726->409 + sync_push kok neden yamasi", "--", CHAT)
cikti.append(f"commit rc={rc}\n{out[-600:]}")
rc, out = git("log", "-3", "--oneline")
cikti.append(out)
with open(KOK + r"\_tmp\chat_commit.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(cikti))
