"""KIRMA KANITI: yon + tur/mahiyet (6 senaryo) + canli veri."""
import json
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def yeni(task_id, ajan, kayitlar):
    out = []
    for k in kayitlar:
        if k.get("task_id") != task_id or k.get("yanit_alindi"):
            continue
        if k.get("kime") not in (ajan, "hepsi") or k.get("kimden") == ajan:
            continue
        mahiyet = str(k.get("mahiyet") or "")
        tur = str(k.get("tur") or "")
        if mahiyet and mahiyet != "teslim_bloklayici":
            continue
        if tur == "bilgi":
            continue
        out.append(k)
    return out


def eski(task_id, kayitlar):
    return [k for k in kayitlar
            if k.get("task_id") == task_id and not k.get("yanit_alindi")]


def M(**x):
    return x


sonuc = 0
print("=" * 70)
print("KIRMA KANITI (6 senaryo)")
print("=" * 70)

K1 = [M(task_id="T1", kimden="salih", kime="ihsan", yanit_alindi=False, tur="bilgi",
         mahiyet="bilgi", mesaj="V4 3 parca"),
      M(task_id="T1", kimden="salih", kime="ihsan", yanit_alindi=False, tur="soru",
         mahiyet="bilgi", mesaj="mimir bitti"),
      M(task_id="T1", kimden="salih", kime="ihsan", yanit_alindi=False, tur="soru",
         mahiyet="bilgi", mesaj="CANLI OLUM")]
n = len(yeni("T1", "salih", K1))
t1 = not n
print(f"1) salih kendi raporlari : ESKI={len(eski('T1',K1))} YENI={n}  {'GECTI' if t1 else 'KALDI'}")
sonuc += t1

K2 = [M(task_id="T2", kimden="ihsan", kime="salih", yanit_alindi=False, tur="soru",
         mahiyet="teslim_bloklayici", mesaj="kapiyi ac"),
      M(task_id="T2", kimden="ihsan", kime="hepsi", yanit_alindi=False, tur="soru",
         mahiyet="teslim_bloklayici", mesaj="duyuru")]
n = len(yeni("T2", "salih", K2))
t2 = n == 2
print(f"2) --blok sorusu + duyuru: YENI={n} (2 beklenir)  {'GECTI' if t2 else 'KALDI'}")
sonuc += t2

K3 = [M(task_id="T3", kimden="ihsan", kime="utku", yanit_alindi=False, tur="soru",
         mahiyet="teslim_bloklayici", mesaj="sadece utku")]
n3, n3b = len(yeni("T3", "utku", K3)), len(yeni("T3", "salih", K3))
t3 = n3 == 1 and n3b == 0
print(f"3) baska ajana soru      : utku={n3} salih={n3b}  {'GECTI' if t3 else 'KALDI'}")
sonuc += t3

K4 = [M(task_id="T4", kimden="ihsan", kime="salih", yanit_alindi=True, tur="soru",
         mahiyet="teslim_bloklayici", mesaj="cevaplandi")]
t4 = not yeni("T4", "salih", K4)
print(f"4) cevaplanmis           : {len(yeni('T4','salih',K4))}  {'GECTI' if t4 else 'KALDI'}")
sonuc += t4

K5 = [M(task_id="T5", kimden="ihsan", kime="ihsan", yanit_alindi=False, tur="soru",
         mahiyet="teslim_bloklayici", mesaj="kendine")]
t5 = not yeni("T5", "ihsan", K5)
print(f"5) ihsan->ihsan          : {len(yeni('T5','ihsan',K5))}  {'GECTI' if t5 else 'KALDI'}")
sonuc += t5

K6 = [M(task_id="T6", kimden="ihsan", kime="salih", yanit_alindi=False,
         mesaj="ESKI kayit: tur/mahiyet YOK")]
n = len(yeni("T6", "salih", K6))
t6 = n == 1
print(f"6) eski kayit (alan yok) : {n} (yon kurali devrede)  {'GECTI' if t6 else 'KALDI'}")
sonuc += t6

print(f"\nSONUC: {sonuc}/6")

print()
print("=" * 70)
print("CANLI VERI")
print("=" * 70)
canli = [json.loads(x) for x in
         (KOK / "data" / "orchestrator" / "chat" / "messages.jsonl")
         .read_text(encoding="utf-8").splitlines() if x.strip()]
dolu = sum(1 for r in canli if r.get("tur") or r.get("mahiyet"))
print(f"  kayit={len(canli)}  tur/mahiyet dolu={dolu}")
for t, a in [("ALTYAPI-MIMIR-BAGLAM-01", "salih"),
             ("ALTYAPI-ODIN-UYARLAMA-01", "yasu")]:
    print(f"  {t} / {a:6s}: ESKI={len(eski(t,canli)):2d} -> YENI={len(yeni(t,a,canli)):2d}")