"""Mudahale kaniti: benim kodum ve teslim kaydim nerede, ihsan ne yapmis?

Soru: skills/services/ticaret_sicili_kanit.py icindeki olay_esle() /
ILAN_TURU_ESLEME / ilan_turu_normalize_et() fonksiyonlari calisma agacinda
YOK. Git log'da hicbir commit icermiyor (dosya dfc5f0a ile ayni = temiz).
Onay kuyrugunda VERI-TSG-ESLEME-CASE-01 kaydi 0. Pano 'plan'.

Bu script su 4 yolu olcer:
  1) Kayip fonksiyonlarin git gecmisinde (TUM ref'ler) var mi
  2) stash@{0} ve stash@{1} icinde o dosyanin TAM hali var mi
  3) canli DB'de teslim edilen 19 satir + 302 kayit duruyor mu
  4) kanit.txt / yedek dosyasi duruyor mu
"""

import glob
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DOSYA = "skills/services/ticaret_sicili_kanit.py"
ANAHTARLAR = ["def olay_esle", "ILAN_TURU_ESLEME = ", "def ilan_turu_normalize_et"]


def git(*args, **kw):
    return subprocess.run(
        ["git", *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", **kw
    ).stdout


print("=== 1) KAYIP FONKSIYONLAR: git gecmisinde var mi (--all, sadece bu dosya) ===")
r = git("log", "--all", "--oneline", "-S", "def olay_esle", "--", DOSYA)
print("   " + (r.strip() or "HICBIR COMMITTE YOK - kod hicbir zaman commitlenmedi"))

print("\n=== 2) stash'lerde bu dosyanin hali ===")
for i in (0, 1, 2):
    p = git("stash", "show", "-p", f"stash@{{{i}}}", "--", DOSYA)
    dosya_p = git("stash", "show", "--name-only", f"stash@{{{i}}}", "--", DOSYA).strip()
    var = [a for a in ANAHTARLAR if a in p]
    print(f"   stash@{{{i}}}: dosya_listede={'EVET' if dosya_p else 'HAYIR'}  "
          f"bulunan_kod={len(var)}/3 {var}")

print("\n=== 3) canli DB (company_events) ===")
def db_deneme(yol):
    try:
        if not os.path.exists(yol) or os.path.getsize(yol) < 10_000:
            return None
        c = sqlite3.connect(f"file:{yol}?mode=ro", uri=True)
        var = c.execute(
            "select name from sqlite_master where type='table' and name='company_events'"
        ).fetchone()
        if not var:
            return None
        tsg = c.execute(
            "select count(*) from company_events where event_source='TSG'"
        ).fetchone()[0]
        bos = c.execute(
            "select count(*) from company_events where event_source='TSG' "
            "and (event_type is null or event_type='')"
        ).fetchone()[0]
        c.close()
        return tsg, bos
    except Exception:
        return None

adaylar = set()
for kalip in ("data/*.db", "data/**/*.db", "*.db", "**/*.db", "**/*.sqlite"):
    adaylar.update(glob.glob(kalip, recursive=True))
bulundu = False
for d in sorted(adaylar):
    sonuc = db_deneme(d)
    if sonuc:
        tsg, bos = sonuc
        print(f"   {d}: TSG={tsg}  event_type_bos={bos}")
        bulundu = True
if not bulundu:
    print("   HICBIR YERDE company_events tablosu bulunamadi (dosya yok/0 bayt)")

print("\n=== 4) kanit dosyalari ===")
for d in sorted(glob.glob("data/kanit/**/*.json", recursive=True))[:1]:
    print(f"   ornek kanit: {d}")
n = len(glob.glob("data/kanit/**/*.json", recursive=True))
print(f"   data/kanit altindaki json dosya sayisi: {n}")
for y in ("yedekler/company_events_esleme_20261002.jsonl",
          "data/orchestrator/VERI-TSG-ESLEME-CASE-01_rapor_2026-10-02_uretim.md"):
    var = Path(y).exists()
    boyut = Path(y).stat().st_size if var else 0
    print(f"   [{'VAR' if var else 'YOK'}] {y} ({boyut} b)")

print("\n=== 5) calisma agacinda TSG tesliminin ayak izleri ===")
r = subprocess.run(["git", "status", "--porcelain"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
tsg_dosyalar = [ln for ln in r.stdout.splitlines()
                if any(k in ln.lower() for k in ("tsg", "bulgu", "d318", "d317"))]
print(f"   ilgili degisiklikli dosya sayisi: {len(tsg_dosyalar)}")
for ln in tsg_dosyalar[:14]:
    print("     " + ln)
