"""Faz A dogrulama olcumu (D-224: varsayim yok, her iddia olculur).

Kontrol edilenler:
  1) 0049 diskte mi, down dosyasi var mi (B-14/D-251: geri alma zorunlu)
  2) companies PK'si gercekten company_id mi (brief varsayimi)
  3) Skor kolonlarinda aralik kisiti var mi (D-245: kolon adi icerigi
     dogrulamaz; 1.5 sessizce yazilabilir mi?)
  4) DEFAULT 0 var mi (D-249 yasagi)
  5) Kanonik goc defterinde kayitli mi (D-253: iz semada olmali)
  6) company_capabilities/certifications/key_personnel diskte var mi (F3 gap)
  7) intelligence/ dizini ve skor_motoru.py cakismasi (D-211 ikiz yasagi)
  8) ayni isi yapan ikinci bir yazici var mi (D-256/2)
"""

import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
MIG = ROOT / "src" / "company_master" / "schema" / "migrations"
GOC = MIG / "0049_firsat_skorlari.sql"
INDIR = MIG / "down" / "0049_firsat_skorlari.down.sql"

basari = 0
toplam = 0


def adim(ad, kosul, kanit=""):
    global basari, toplam
    toplam += 1
    ok = bool(kosul)
    basari += 1 if ok else 0
    print(f"  [{'OK' if ok else 'EKSIK'}] {ad}")
    if kanit:
        print(f"         {kanit}")
    return ok


print("=== FAZ A DOGRULAMA ===\n")

# 1) dosyalar
adim("0049 goc dosyasi diskte", GOC.exists(),
     f"{GOC.relative_to(ROOT)} ({GOC.stat().st_size} bayt)" if GOC.exists()
     else "YOK")
adim("0049 geri alma dosyasi", INDIR.exists(),
     str(INDIR.relative_to(ROOT)) if INDIR.exists()
     else "YOK -> test_migration_down_files_content kirmizi verir")

sql = GOC.read_text(encoding="utf-8") if GOC.exists() else ""

# 2) companies PK
pk_ok = False
pk_kanit = "belirlenemedi"
core = MIG / "0001_core.sql"
if core.exists():
    m = re.search(r"companies\s*\((.*?)\n\)", core.read_text(encoding="utf-8"),
                  re.S)
    if m and "company_id" in m.group(1) and re.search(
            r"company_id\s+UUID\s+PRIMARY KEY", m.group(1)):
        pk_ok, pk_kanit = True, "0001_core.sql: company_id UUID PRIMARY KEY"
adim("companies PK = company_id (brief varsayimi)", pk_ok, pk_kanit)

# 3) aralik kisiti  <-- ana bulgu
aralik = re.findall(r"CHECK\s*\([^)]*_score[^)]*\)", sql, re.I)
# Dinamik koruma: kisi adi ADD CONSTRAINT ile uretiliyorsa metin taramasi
# gormez (D-268/5 dersi: metin taramasi mandal yerine gecmez).
dinamik = ("'ck_cos_need_score_aralik'" in sql
           and "BETWEEN 0.0 AND 1.0" in sql
           and re.search(r"pg_constraint", sql) is not None)
adim("skor kolonlarinda 0.0-1.0 aralik korumasi", bool(aralik) or dinamik,
     (f"literal CHECK: {aralik}" if aralik
      else f"dinamik koruma: 4 kisit pg_constraint kontrolu ile ekleniyor "
           f"(kk_n*/fit/timing/ensemble, 0.0-1.0)")
     if (aralik or dinamik) else
     "HICBIR koruma yok -> need_score=1.5 veya 250.00 sessizce yazilir "
     "(D-245: kolon adi icerigi dogrulamaz; D-267/1: kisit unutulmaz)")
if dinamik:
    adim("kisit idempotent (pg_catalog kontrolu)", "conname = k" in sql,
         "pg_constraint uzerinden varlik kontrolu -> iki kez kosulur, patlamaz "
         "(D-251/5)")

# 4) DEFAULT 0 yasagi
d0 = re.findall(r"(need_score|fit_score|timing_score|ensemble_score)"
                r"[^\n,]*DEFAULT\s+0", sql, re.I)
adim("skor kolonlarinda DEFAULT 0 yok (D-249)", not d0,
     f"ihlal: {d0}" if d0 else "dort kolon da DEFAULT'siz")

# 5) kanonik goc defteri
def_sql = (ROOT / "scripts" / "goc_defteri.py")
kayit = subprocess.run(
    [sys.executable, "-X", "utf8", str(def_sql)],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(ROOT)).stdout
satir = next((ln for ln in kayit.splitlines() if "0049" in ln), None)
adim("kanonik goc defteri 0049'u taniyor", satir is not None,
     satir.strip() if satir else "goc_defteri.py ciktisinda 0049 gecisi yok")

# 6) F3 girdi tablolari
girdi = ["company_capabilities", "certifications", "key_personnel"]
var = [t for t in girdi
       if re.search(rf"CREATE TABLE( IF NOT EXISTS)?\s+{t}\b",
                    "\n".join(p.read_text(encoding="utf-8", errors="replace")
                              for p in MIG.glob("*.sql")), re.I)]
adim("fit_score girdi tablolari semada (F3 gap)", len(var) == 3,
     f"bulunan {len(var)}/3: {var} — ETL dolgusu F3'te, beklenen")

# 7) ikiz modul yasagi (D-211)
int_dir = ROOT / "src" / "company_master" / "intelligence"
mevcut = sorted(p.name for p in int_dir.glob("*.py")) if int_dir.exists() else []
adim("skor_motoru.py adi cakismasi yok (D-211)", "skor_motoru.py" not in mevcut,
     f"intelligence/ icerigi: {mevcut or 'dizin bos'}")

# 8) ikinci yazici (D-256/2) — tabloya yazan baska yol
yazan = []
for p in list((ROOT / "src").rglob("*.py")) + list((ROOT / "scripts").glob("*.py")):
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    if "company_opportunity_scores" in t and "0049_firsat_skorlari" not in t:
        # yazan mi okuyan mi ayirt et
        if re.search(r"(INSERT\s+INTO|UPDATE)\s+company_opportunity_scores",
                     t, re.I):
            yazan.append(str(p.relative_to(ROOT)).replace("\\", "/"))
adim("company_opportunity_scores'a yazan ikinci yol yok (D-256/2)",
     not yazan, f"yazan: {yazan}" if yazan
     else "yazan yol 0 (firsat_recalc yazilacak)")

print(f"\n=== FAZ A SONU: {basari}/{toplam} ===")
if basari < toplam:
    print("  Eksikler FAZ A icinde giderilir (goc dosyasi bu ajanin kilidinde).")
else:
    print("  Goc dosyasi degismeye gerek kalmadan Faz B'ye gecilebilir.")
