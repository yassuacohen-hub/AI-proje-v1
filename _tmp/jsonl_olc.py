# -*- coding: utf-8 -*-
"""merge=union dosyalarini olc: satir / benzersiz satir / bozuk / bayt. Yalniz okur."""
import glob
import json
import os

KOK = r"c:/Huginn Data Projesi/Huginn Data Insights"
YOLLAR = [
    "data/orchestrator/chat/messages.jsonl",
    "data/orchestrator/triggers/*.jsonl",
    "data/orchestrator/trigger_log.jsonl",
    "data/orchestrator/tetik_senk_log.jsonl",
    "data/orchestrator/decision_log.jsonl",
    "data/orchestrator/ajan-chat-bulgular.jsonl",
    "data/orchestrator/pano_yazim_kaydi.jsonl",
    "data/orchestrator/mcp_spend_log.jsonl",
    "data/orchestrator/ajan-chat.jsonl",  # kontrol: union listesinde yok
]
CIKTI = r"c:/Huginn Data Projesi/_tmp/jsonl_olc.txt"


def olc(yol):
    satir = benzersiz = bozuk = 0
    gorulen = set()
    with open(yol, "r", encoding="utf-8-sig", errors="replace") as f:
        for ham in f:
            s = ham.strip()
            if not s:
                continue
            satir += 1
            if s not in gorulen:
                gorulen.add(s)
                benzersiz += 1
            try:
                json.loads(s)
            except Exception:
                bozuk += 1
    return satir, benzersiz, bozuk, os.path.getsize(yol)


out = ["dosya\tsatir\tbenzersiz\tbozuk\tbayt"]
for p in YOLLAR:
    for yol in sorted(glob.glob(os.path.join(KOK, p))):
        ad = os.path.relpath(yol, KOK).replace("\\", "/")
        try:
            s, b, z, by = olc(yol)
            out.append(f"{ad}\t{s}\t{b}\t{z}\t{by}")
        except Exception as e:  # ponytail: okuma hatasi dosya bazli raporlanir
            out.append(f"{ad}\tHATA {e}")
    if not glob.glob(os.path.join(KOK, p)):
        out.append(f"{p}\tYOK")
with open(CIKTI, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("tamam", len(out))
