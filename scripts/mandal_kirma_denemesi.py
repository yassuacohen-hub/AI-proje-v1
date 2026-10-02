"""Mandali kirarak dogrula (D-256/4): 'yesil mandal' kanit degildir.

Uc ayri bozma denenir. Her biri icin: boz -> calistir -> KIRMIZI gormeli ->
geri al -> yesil gormeli. Tamaminda KIRMIZI gelmezse mandal o bozmayi
yakalmiyor demektir ve duzeltilmeden teslim olmaz.

Idempotenttir: script sonunda dosyalari asil haline dondurur.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "tests" / "test_firsat_skorlari.py"
GOC = ROOT / "src" / "company_master" / "schema" / "migrations" / "0049_firsat_skorlari.sql"
MODUL = ROOT / "src" / "company_master" / "intelligence" / "skor_motoru.py"
YEDEK = ROOT / "data" / "_tmp" / "mandal_kirma"

for p in (GOC, MODUL):
    YEDEK.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, YEDEK / p.name)


def kos():
    r = subprocess.run([sys.executable, "-X", "utf8", str(TEST)],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(ROOT))
    return r.returncode, r.stdout + r.stderr


def kirik_satirlar(cikti: str) -> list[str]:
    return [ln.strip() for ln in cikti.splitlines() if "[KIRIK]" in ln]


denemeler = [
    ("Migration: skor kolonuna DEFAULT 0 geri geldi (D-249 ihlali)",
     GOC, "    need_score NUMERIC(5,2),",
     "    need_score NUMERIC(5,2) DEFAULT 0,"),

    ("Motor: need agirligi 0.30 -> 0.40 (SSOT:248 ihlali)",
     MODUL, '"need": 0.30,', '"need": 0.40,'),

    ("Motor: need_score(None) artik 0.0 donuyor (D-249 en agir ihlali)",
     MODUL, "    sinyal = _sayi(sinyal_tur_sayisi)\n    if sinyal is None:\n        return None",
     "    sinyal = _sayi(sinyal_tur_sayisi)\n    if sinyal is None:\n        return 0.0"),
]

print("=== MANDAL KIRMA DENEMESI (D-256/4) ===\n")

basarili = 0
for ad, dosya, eski, yeni in denemeler:
    icerik = dosya.read_text(encoding="utf-8")
    if eski not in icerik:
        print(f"  [ATLANDI] {ad}\n           hedef metin bulunamadi")
        continue
    dosya.write_text(icerik.replace(eski, yeni, 1), encoding="utf-8")
    kod, cikti = kos()
    kirik = kirik_satirlar(cikti)
    yakaladi = kod != 0 and bool(kirik)
    print(f"  [{'YAKALADI' if yakaladi else 'KACIRDI'}] {ad}")
    print(f"           exit={kod}, kirik mandal sayisi={len(kirik)}")
    for ln in kirik[:4]:
        print(f"           -> {ln}")
    # geri al
    shutil.copy2(YEDEK / dosya.name, dosya)
    kod2, _ = kos()
    temiz = kod2 == 0
    print(f"           geri alindi, exit={kod2} ({'temiz' if temiz else 'TEMIZ DEGIL'})")
    if yakaladi and temiz:
        basarili += 1

# son kontrol
kod, _ = kos()
print(f"\n=== SONUC: {basarili}/{len(denemeler)} bozma yakalandi ===")
print(f"dosya hali temiz mi: {'EVET' if kod == 0 else 'HAYIR'}")
if basarili != len(denemeler) or kod != 0:
    print("MANDAL GUVENILIR DEGIL — duzeltilmeden teslim yok.")
    sys.exit(1)
print("Mandal gercekten durduruyor.")
