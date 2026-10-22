# -*- coding: utf-8 -*-
"""ajan-chat.jsonl anahtar-birlestirme. Varsayilan KURU (yazmaz); --yaz yedek alip yazar.
Anahtar=(kimden,ajan,task_id,sorun). Temsilci: cozuldu > cokundurmus > acik, esitse en gec zaman.
Ilk-gorulme sirasi korunur. ponytail: indeks-tabanli guncelle() kayar; tek-kopya anahtarlar etkilenmez, cok-kopyalilar zaten bug."""
import json
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

YOL = Path(__file__).resolve().parent.parent / "Huginn Data Insights" / "data" / "orchestrator" / "ajan-chat.jsonl"
YEDEK = Path(__file__).resolve().parent / "ajan-chat.jsonl.bak_dedupe"
CIKTI = Path(__file__).resolve().parent / "chat_dedupe.txt"
RANK = {"cozuldu": 2, "cokundurmus": 1, "acik": 0}
ZAMAN = ("zaman", "ts", "tarih", "olusturma", "created_at", "timestamp")


def zaman(d):
    for k in ZAMAN:
        if d.get(k):
            return str(d[k])
    return ""


def birlestir(kayitlar):
    """kayitlar: [(ham, dict)] -> (cikis_ham_satirlar, grup_sayisi). Saf fonksiyon."""
    grup = defaultdict(list)
    sira = []
    for ham, d in kayitlar:
        k = (d.get("kimden"), d.get("ajan"), d.get("task_id"), d.get("sorun"))
        if k not in grup:
            sira.append(k)
        grup[k].append((ham, d))
    cik = [max(grup[k], key=lambda t: (RANK.get(t[1].get("durum"), 0), zaman(t[1])))[0] for k in sira]
    return cik, grup


def _selfcheck():
    a = ('{"kimden":"x","ajan":"y","task_id":"T","sorun":"s","durum":"acik","zaman":"1"}', None)
    b = ('{"kimden":"x","ajan":"y","task_id":"T","sorun":"s","durum":"cozuldu","zaman":"0"}', None)
    c = ('{"kimden":"x","ajan":"y","task_id":"U","sorun":"s","durum":"acik","zaman":"2"}', None)
    kay = [(h, json.loads(h)) for h, _ in (a, b, c, a)]
    cik, _ = birlestir(kay)
    assert cik == [b[0], c[0]], cik


_selfcheck()
satirlar = [s for s in YOL.read_text(encoding="utf-8-sig").splitlines() if s.strip()]
kayit, bozuk = [], 0
for s in satirlar:
    try:
        kayit.append((s, json.loads(s)))
    except ValueError:
        bozuk += 1
cik, grup = birlestir(kayit)
cok = [g for g in grup.values() if len(g) > 1]
boy = Counter(len(g) for g in cok)
farkli_zaman = sum(1 for g in cok if len({zaman(d) for _, d in g}) > 1)
out = [
    f"satir={len(satirlar)} bozuk={bozuk} -> cikis={len(cik)}",
    f"cok-kopyali grup={len(cok)} boyut-dagilimi={dict(sorted(boy.items()))}",
    f"  zamani farkli grup={farkli_zaman}",
    f"zaman anahtari ornegi: {[k for k in ZAMAN if k in kayit[0][1]] if kayit else '-'}; alanlar={sorted(kayit[0][1]) if kayit else '-'}",
]
if "--yaz" in sys.argv:
    if bozuk:
        out.append("BOZUK SATIR VAR: yazilmadi")
    else:
        shutil.copy2(YOL, YEDEK)
        YOL.write_text("\n".join(cik) + "\n", encoding="utf-8", newline="\n")
        out.append(f"YAZILDI; yedek={YEDEK.name}")
CIKTI.write_text("\n".join(out) + "\n", encoding="utf-8")
