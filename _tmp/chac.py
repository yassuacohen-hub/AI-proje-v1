"""KIRMA KANITI + REGRESYON: yon filtresi dogru mu, kapi gercekten aciliyor mu?"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

spec = importlib.util.spec_from_file_location(
    "gk", KOK / "scripts" / "gorev_kutusu.py")
gk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gk)

GECICI = Path(tempfile.gettempdir()) / "mnk_kanit"
GECICI.mkdir(parents=True, exist_ok=True)


def yaz(kayitlar):
    p = GECICI / "messages.jsonl"
    p.write_text("".join(json.dumps(k, ensure_ascii=False) + "\n" for k in kayitlar),
                 encoding="utf-8")
    return p


ESKI = "9849e48a4b8a7dd7"


def eski_kural(task_id, kayitlar):
    """Duzeltmeden onceki kosul (yon bilgisi yok)."""
    return [k for k in kayitlar
            if k.get("task_id") == task_id and not k.get("yanit_alindi")]


def yeni_kural(task_id, ajan, kayitlar):
    return [k for k in kayitlar
            if k.get("task_id") == task_id and not k.get("yanit_alindi")
            and k.get("kime") in (ajan, "hepsi") and k.get("kimden") != ajan]


print("=" * 66)
print("A) KIRMA KANITI — salih'i bloklayan kendi raporlari")
print("=" * 66)
K = [
    dict(task_id="T1", kimden="salih", kime="ihsan", yanit_alindi=False,
         mesaj="V4 organizasyonu: 3 parca..."),
    dict(task_id="T1", kimden="salih", kime="ihsan", yanit_alindi=False,
         mesaj="mimir_servis.py bitti, 6/6 yesil..."),
    dict(task_id="T1", kimden="salih", kime="ihsan", yanit_alindi=False,
         mesaj="CANLI OLUM ALINDI..."),
]
e = eski_kural("T1", K)
y = yeni_kural("T1", "salih", K)
print(f"  ESKI kural -> {len(e)} engel  (salih kendi raporlariyla bloklanir)")
print(f"  YENI kural -> {len(y)} engel  (rapor soru degil)")
print(f"  KIRILDI    : {len(e) > 0 and len(y) == 0}")

print()
print("=" * 66)
print("B) KENDI KENDINE MESAJ (ihsan->ihsan) bloklamamali")
print("=" * 66)
K2 = [dict(task_id="T2", kimden="ihsan", kime="ihsan", yanit_alindi=False,
           mesaj="TSG-PILOT-20 OLCUMU BITTI")]
print(f"  ESKI -> {len(eski_kural('T2', K2))} engel")
print(f"  YENI -> {len(yeni_kural('T2', 'ihsan', K2))} engel (ihsan icin)")
print(f"  YENI -> {len(yeni_kural('T2', 'utku', K2))} engel (utku icin)")
print(f"  DOGRU   : {len(yeni_kural('T2', 'ihsan', K2)) == 0}")

print()
print("=" * 66)
print("C) GERCEK SORU HIZLA TESLIM EDILMEMELI (regresyon koruma)")
print("=" * 66)
K3 = [dict(task_id="T3", kimden="ihsan", kime="salih", yanit_alindi=False,
           mesaj="Bu kapiyi ac, aciklamaz"),
      dict(task_id="T3", kimden="ihsan", kime="hepsi", yanit_alindi=False,
           mesaj="Herkese duyuru")]
print(f"  salih'e dogrudan soru : {len(yeni_kural('T3', 'salih', K3))} engel (1 beklenir)")
print(f"  'hepsi' duyurusu      : {len(yeni_kural('T3', 'utku', K3))} engel (1 beklenir)")
print(f"  baska ajana soru      : {len(yeni_kural('T3', 'utku', K3)) - 1} ek engel (0 beklenir)")
print(f"  DOGRU   : {len(yeni_kural('T3', 'salih', K3)) == 2}")

print()
print("=" * 66)
print("D) CEVAPLANMIS MESAJ HICBIR ZAMAN BLOKLAMAZ")
print("=" * 66)
K4 = [dict(task_id="T4", kimden="ihsan", kime="salih", yanit_alindi=True,
           mesaj="cevaplandi")]
print(f"  YENI -> {len(yeni_kural('T4', 'salih', K4))} engel (0 beklenir)")
print(f"  DOGRU   : {len(yeni_kural('T4', 'salih', K4)) == 0}")

print()
print("=" * 66)
print("E) CANLI VERI UZERINDE: MIMIR gorevi icin salih bloklaniyor mu?")
print("=" * 66)
canli = [json.loads(x) for x in
         (KOK / "data" / "orchestrator" / "chat" / "messages.jsonl")
         .read_text(encoding="utf-8").splitlines() if x.strip()]
for task, ajan in [("ALTYAPI-MIMIR-BAGLAM-01", "salih"),
                   ("ALTYAPI-ODIN-UYARLAMA-01", "yasu"),
                   ("ALTYAPI-MIMIR-BAGLAM-01", "ihsan")]:
    e = eski_kural(task, canli)
    y = yeni_kural(task, ajan, canli)
    print(f"  {task} / {ajan:6s}: ESKI={len(e):2d} engel -> YENI={len(y):2d} engel")

print()
print("=" * 66)
print("F) REGRESYON: ilgili test dosyalari")
print("=" * 66)
r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-q", "-k",
     "gorev_kutusu or teslim or mesaj or chat", "--no-header", "-p", "no:cacheprovider"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(KOK), timeout=600)
print("  rc =", r.returncode)
print("  " + " | ".join((r.stdout or "").strip().splitlines()[-4:]))
"""Acik chat kayitlarini tam listeler (olcum, kalici degil)."""
"""SABLON_WEB: 24 dosyanin siniflandirmasi + kilit sahipleri (olcum)."""
import json
import pathlib
import re

KOK = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
ATLA = {".venv", ".git", "node_modules", "__pycache__", "backups",
        "_ARSIV_tek_kullanimlik", "tests"}
IZ = ("isim.org.tr", "osp.com.tr", "ostimonline", "ostimistihdam")

kilitler = json.loads(
    (KOK / "data" / "orchestrator" / "file_locks.json").read_text(
        encoding="utf-8"))

rows = []
for p in sorted(KOK.rglob("*.py")):
    if ATLA & set(p.parts) or p.name == "yazma_kapisi.py":
        continue
    try:
        m = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    if not any(i in m for i in IZ):
        continue
    rel = p.relative_to(KOK).as_posix()
    # kendi listesi var mi? (kanonik kopya sinyali)
    satirlar = m.splitlines()
    tanimli = False
    for idx, ln in enumerate(satirlar):
        if not any(i in ln for i in IZ):
            continue
        geri = satirlar[max(0, idx - 6):idx + 1]
        if any(re.match(r"^\s*[A-Z_][A-Z_0-9]{2,}\s*(:[^=]+)?=\s*[\(\[{\{]", x)
               for x in geri):
            tanimli = True
            break
    k = kilitler.get(rel)
    sahip = k.get("sahip") if k else "-"
    task = k.get("task_id") if k else "-"
    rows.append((rel, "TANIMLI" if tanimli else "kullanım", sahip, task))

print("TOPLAM:", len(rows))
print()
print(f"{'DURUM':9} {'SAHİP':9} DOSYA")
for rel, durum, sahip, task in sorted(rows, key=lambda x: (x[1], x[0])):
    print(f"{durum:9} {sahip:9} {rel}")
print()
print("TANIMLI (kopya) :", sum(1 for r in rows if r[1] == "TANIMLI"))
print("KULLANIM       :", sum(1 for r in rows if r[1] == "kullanım"))
print("KILITLI        :", sum(1 for r in rows if r[2] != "-"))