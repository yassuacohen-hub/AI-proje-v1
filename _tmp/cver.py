"""GERCEK fonksiyonu cagir: commit durumu + salih icin kapi acik mi?"""
import hashlib
import importlib.util
import inspect
import subprocess
import sys
import tempfile
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
G = KOK / "scripts" / "gorev_kutusu.py"


def git(*a, timeout=300):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


print("=== 1) COMMIT DURUMU ===")
rc, c = git("log", "--oneline", "-3")
print("  " + c.replace("\n", "\n  "))
rc, c = git("status", "--short", "--", "scripts/gorev_kutusu.py")
print(f"  gorev_kutusu.py: {c or '(temiz -> commit dustu)'}")
print(f"  canli sha = {hashlib.sha256(G.read_bytes()).hexdigest()[:16]}")

print()
print("=" * 70)
print("2) GERCEK FONKSIYON (imza + govde canli dosyadan)")
print("=" * 70)
spec = importlib.util.spec_from_file_location("gk_canli", G)
gk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gk)
print(f"  imza: {inspect.signature(gk._mesaj_kontrol_et)}")
i = inspect.getsourcelines(gk._mesaj_kontrol_et)[1]
print(f"  baslangic satiri: {i}")

print()
print("=" * 70)
print("3) CANLI VERI UZERINDE GERCEK CAGRI")
print("=" * 70)
import json
canli = [json.loads(x) for x in
         (O / "chat" / "messages.jsonl").read_text(encoding="utf-8").splitlines()
         if x.strip()]
for task, ajan in [("ALTYAPI-MIMIR-BAGLAM-01", "salih"),
                   ("ALTYAPI-ODIN-UYARLAMA-01", "yasu"),
                   ("ALTYAPI-MIMIR-BAGLAM-01", "ihsan"),
                   ("ALTYAPI-MIMIR-BAGLAM-01", "utku")]:
    gercek = gk._mesaj_kontrol_et(task, ajan)
    eski = [k for k in canli if k.get("task_id") == task and not k.get("yanit_alindi")]
    durum = "ACIK" if not gercek else f"{len(gercek)} ENGEL"
    print(f"  {task} / {ajan:6s}: ESKI={len(eski):2d} -> GERCEK={len(gercek):2d}  [{durum}]")
    for m in gercek[:2]:
        print(f"       engel: {m[:95]}")

print()
print("=" * 70)
print("4) KALAN SORUN TARAMASI")
print("=" * 70)
sorun = 0

# 4a: kapi gercekten gecir mi? Gecici mesajlarla uçtan uca dene.
gecici = Path(tempfile.mkdtemp()) / "chat"
gecici.mkdir(parents=True)
kayit = dict(task_id="TST", kimden="ihsan", kime="salih", yanit_alindi=False,
             tur="soru", mahiyet="teslim_bloklayici", mesaj="gercek engel")
kayit2 = dict(task_id="TST", kimden="salih", kime="ihsan", yanit_alindi=False,
              tur="bilgi", mahiyet="bilgi", mesaj="salih raporu")
(gecici / "messages.jsonl").write_text(
    "".join(json.dumps(k, ensure_ascii=False) + "\n" for k in (kayit, kayit2)),
    encoding="utf-8")

eski_yol = gk.tb.STATE_DIR
gk.tb.STATE_DIR = gecici
sonuc = gk._mesaj_kontrol_et("TST", "salih")
gk.tb.STATE_DIR = eski_yol
print(f"  4a) --blok engeli gorunuyor mu : {len(sonuc)} (1 beklenir) "
      f"{'OK' if len(sonuc) == 1 else 'SORUN'}")
if len(sonuc) != 1:
    sorun += 1

# 4b: ayni fonksiyon imzasi her cagri yerinde mi
try:
    gk._mesaj_kontrol_et("TST")                     # eski imza -> TypeError beklenir
    print("  4b) eski imza hala kabul ediliyor -> SORUN (geriye donukluk yok)")
    sorun += 1
except TypeError:
    print("  4b) eski imza TypeError veriyor -> OK (yanlis cagri sessizce gecmez)")

# 4c: kapi baska yerde de ayni hatayi tasiyor mu?
y = (O / "chat" / "messages.jsonl").read_text(encoding="utf-8")
print(f"  4c) messages.jsonl kayit = {len(y.splitlines())}")
dolu = sum(1 for ln in y.splitlines() if ln.strip() and
           ('"tur"' in ln or '"mahiyet"' in ln))
print(f"      tur/mahiyet dolu kayit = {dolu}")
if dolu == 0:
    print(f"      NOT: hicbir mesaj tur/mahiyet tasimiyor -> 2. katman TAMAMEN")
    print(f"      olu kod. Ancak chat_gonder.py bu alanlari YAZIYOR (commit'lenmemis),")
    print(f"      yani yeni mesajlar doldurunca katman 2 devreye girecek.")

# 4d: 'hepsi' gurultusu
hepsi = sum(1 for k in canli
            if k.get("kime") == "hepsi" and not k.get("yanit_alindi"))
print(f"  4d) 'hepsi' duyurusu, cevapsiz = {hepsi} -> herkesi bloklar (bilinen risk)")

print(f"\nSONUC: {'SORUN YOK' if sorun == 0 else f'{sorun} SORUN'}")