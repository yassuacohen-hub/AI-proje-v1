# -*- coding: utf-8 -*-
"""messages.jsonl kopya kok neden olcumu (salt okunur)."""
import collections
import json
import subprocess
import sys

sys.stdout = open("../_tmp/msg_kok.txt", "w", encoding="utf-8")
P = "data/orchestrator/chat/messages.jsonl"
KEY = ("tarih", "kimden", "kime", "type", "task_id", "mesaj")

satir = open(P, encoding="utf-8-sig").read().splitlines()
say = collections.Counter()
ilk = {}
for i, s in enumerate(satir):
    try:
        d = json.loads(s)
    except Exception:
        continue
    k = tuple(d.get(x) for x in KEY)
    say[k] += 1
    ilk.setdefault(k, i)
print("toplam", len(satir), "benzersiz", len(say))
dagilim = collections.Counter(min(v, 50) for v in say.values())
print("tekrar_dagilimi(>=50 birlesik)", sorted(dagilim.items())[:12], "...")
top = say.most_common(3)
for k, v in top:
    print(v, "x", k[0], k[1], "->", k[2], k[3], k[4], (k[5] or "")[:60].replace("\n", " "))
# ardisik mi? ayni anahtar bloklari halinde mi tekrar ediyor
blok = 0
onceki = None
for s in satir:
    try:
        d = json.loads(s)
    except Exception:
        continue
    k = tuple(d.get(x) for x in KEY)
    if k != onceki:
        blok += 1
    onceki = k
print("ardisik_blok_sayisi", blok)
# git gecmisi: dosya boyutu / commit sayisi
r = subprocess.run(["git", "log", "--oneline", "--", P], capture_output=True, text=True, encoding="utf-8")
print("dosyayi_degistiren_commit", len(r.stdout.splitlines()))
r = subprocess.run(["git", "check-attr", "merge", P], capture_output=True, text=True, encoding="utf-8")
print(r.stdout.strip())
