import json, sys
sys.path.insert(0, "c:/Huginn Data Projesi/Huginn Data Insights/src")
from company_master import chat

T = "MUSTERI-PANEL-TASARIM-01"
P = "c:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/ajan-chat.jsonl"
TRIG = ("DIKKAT-1: trigger.py:152 _tetikleri_oku korumasiz json.loads OLCULDU, hala acik (chat.py onarildi, trigger.py degil). "
        "Kod D-420 geregi bu gorevin disinda; ayri bakim gorevi olarak ihsan acar. .gitattributes merge=union PO onayi bekler")
KARSILIK = [
    ("NUR katildi", "NUR katilimi alindi; §8 iddia defteri + §5.2'de isleniyor"),
    ("DIKKAT-1 CANLI", "CANLI KANIT alindi: JSONL+git cakisma tekrari dogrulandi (stash cakismasi cakisma_chat.py ile cozuldu). Kalici cozum = merge=union, PO karari"),
    ("DIKKAT-1", TRIG),
    ("DIKKAT-2", "DIKKAT-2: /panel-tasarim build baseline (628KB raw/184KB gzip) derleme §5.3'e alindi; statik kalir"),
    ("DIKKAT-3", "DIKKAT-3: oylama != kanit; derleme §5.2 'ayni yon != kanit' ve 3 kova ile islendi"),
]
hedefler = []
sira = 0
with open(P, encoding="utf-8-sig") as f:
    for ham in f:
        if not ham.strip():
            continue
        try:
            r = json.loads(ham)
        except ValueError:
            continue
        if not isinstance(r, dict) or r.get("task_id") != T:
            continue
        if r.get("kimden") == "nur" and str(r.get("durum", "")).lower() == "acik":
            hedefler.append((sira, r.get("sorun", "")))
        sira += 1
for i, sorun in hedefler:
    k = next((v for p, v in KARSILIK if sorun.startswith(p)), TRIG)
    print(i, sorun[:50], "->", bool(chat.kapat(T, i, k)))
