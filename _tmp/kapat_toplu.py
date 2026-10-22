import sys
sys.path.insert(0, "c:/Huginn Data Projesi/Huginn Data Insights/src")
from company_master import chat

T = "MUSTERI-PANEL-TASARIM-01"
K = "cevap/teslim ORTAK_TASARIM bolumunde var; ihsan derleme §5 (21.10) okudu, celiskiler §5.1'e islendi"
IHSAN = [12, 13, 14, 27, 28, 29] + list(range(108, 121)) + [254, 255, 256, 258] + list(range(263, 276))
NUR = {
    259: "NUR katilimi alindi; §8 iddia defteri + §5.2'de isleniyor",
    260: "DIKKAT-1: chat._jsonl_oku_dayanikli (BOM/merge isareti) kodda mevcut; .gitattributes merge=union PO onayi bekler (D-420)",
    261: "DIKKAT-2: /panel-tasarim build baseline (628KB raw/184KB gzip) derleme §5.3'e alindi; statik kalir",
    262: "DIKKAT-3: oylama != kanit; derleme §5.2 'ayni yon != kanit' ve 3 kova ile islendi",
}
for i in IHSAN:
    print(i, chat.kapat(T, i, K))
for i, k in NUR.items():
    print(i, chat.kapat(T, i, k))
