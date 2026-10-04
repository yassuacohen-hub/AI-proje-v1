"""Rapor var ama teslim kaydi yok — deseni olcer ve kapatir.

Tespit: `VERI-RAG-KORPUS-01` icin
  - rapor dosyasi DISKTE VAR
  - onay kuyrugunda teslim kaydi YOK (kuyrukta sadece eski `AI-RAG-01`)
  - pano durumu `plan` (teslim edilmemis)

Bu, onceki oturumda "onaylandi ve tamamlandi" denilen isin **teslim
komutunun hic calistirilmamis** oldugunun kaniti. Ayni desen TSG'de de
yasanmisti (rapor vardi, teslim kaydi yokti).

Kural (D-55 teslim kontrol listesi + D-312): **rapor yazmak teslim degildir.**
Teslim = pano `review` + onay kuyrugunda `bekliyor` kaydi.

Bu script:
  1) "rapor var ama teslim yok" desenini tum aktif gorevler icin tarar
  2) Her biri icin kanit yazar
  3) Istatistik verir (desen tekrar mi)
"""

import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
ORCH = ROOT / "data" / "orchestrator"


def yukle_json(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(ROOT)).stdout


# --- pano ---
d = yukle_json(ORCH / "task_board.json")
gorevler = d.get("tasks", d) if isinstance(d, dict) else d
pano = {x["task_id"]: x for x in gorevler if isinstance(x, dict) and x.get("task_id")}

# --- onay kuyrugu ---
q = yukle_json(ORCH / "onay_kuyrugu.json")
kayitlar = q if isinstance(q, list) else (q or {}).get("kayitlar", [])
teslim_var = set()
for k in kayitlar:
    if isinstance(k, dict) and k.get("task_id"):
        teslim_var.add(k["task_id"])

# --- rapor dosyalari (gorev id -> rapor yollari) ---
raporlar = {}
for p in ORCH.glob("*_rapor_*.md"):
    stem = p.name.split("_rapor_")[0]
    raporlar.setdefault(stem, []).append(p)

print("=== 1) 'RAPOR VAR, TESLIM YOK' DESENI ===\n")
AKTIF = ("plan", "aktif", "todo", "review", "in_progress")
desen = []
for tid, g in pano.items():
    if g.get("durum") not in AKTIF:
        continue
    if tid in teslim_var:
        continue
    rapor = raporlar.get(tid)
    if not rapor:
        continue
    desen.append((tid, g.get("durum"), g.get("sahip"), rapor[0].name))

if not desen:
    print("  Desen bulunamadi (aktif + teslim kaydi yok + rapor var olan gorev yok).")
else:
    for tid, durum, sahip, rapor in desen:
        print(f"  {tid}")
        print(f"     durum={durum}  sahip={sahip}")
        print(f"     rapor  = {rapor}")

print(f"\n  TOPLAM: {len(desen)} gorev")

# --- 2) istatistik: bu tekrar mi ---
print("\n=== 2) DESEN TEKRAR MI ===")
if len(desen) == 0:
    print("  Hayir - tek vaka.")
elif len(desen) == 1:
    print("  Tek vaka ama TSG'de de ayni sey olmustu -> 2 kez -> tekrar.")
else:
    print(f"  EVET - {len(desen)} kez tekrar etmis. Kural degistirilmeli.")

# --- 3) stash kontrolu: teslim kaydi da stash'a gitmis olabilir mi ---
print("\n=== 3) TESLIM KAYDI STASH'TA MI (kayip hipotezi) ===")
for tid, *_ in desen:
    kayitli = tid in teslim_var
    if kayitli:
        continue
    # onay_kuyrugu icinde task_id gecen mi (teslim kaydi sarti olmasa da)
    ham = git("show", "stash@{0}:data/orchestrator/onay_kuyrugu.json")
    var_stashta = f'"{tid}"' in ham
    print(f"  {tid}: kuyrukta={False}, stash@0'te={var_stashta}")

# --- 4) teslim icin gerekenler ---
print("\n=== 4) KAPANMA YOLU ===")
if desen:
    print("  Her gorev icin kanonik teslim komutu (rapor DIKKAT: teslim degil):")
    for tid, *_ in desen:
        print(f"    python scripts/gorev_kutusu.py teslim --ajan <sahip> "
              f"--task-id {tid} --ozet \"...\"")
    print("\n  Iptal: gorev gercekten bitmediyse teslim etme; onay kuyrugunu")
    print("  kirletmek, hicbir kayit birakmaktan kotudur (D-66).")
else:
    print("  Kapatilacak teslim yok.")

raise SystemExit(0)
