"""TEHIS BETIKLERI TEMIZLIK OLCUMU (D-220 / D-266 / D-193).

KAHIN: "isleri temizle". Once olc, sonra karar (D-224).

Uc kova:
  KAL    -> tuketicisi var (test cagirir / baska kod import eder) VEYA
            teslim raporunda KANIT olarak adreslenmis (D-193)
  TEHHS  -> tek seferlik olcum; tuketicisi yok, raporda adreslenmemis
            -> yedekler/arsiv/ altina (D-242 tek cati), scripts/den cikar
  COP    -> gecici olcum artigi, hicbir sey tutmuyor

OLCUM YAPILMAMIS HIcBIR DOSYA SILINMEZ (D-002). Arsiv = tasima.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]

# --- Bu oturumda uretilen betikler ---
URETILEN = [
    "kayip_kapsam_olcumu.py",
    "kayip_kod_geri_yukle.py",
    "kodlama_ihlal_sahiplik_olcumu.py",
    "teslim_dogrulama_bes_adim.py",
    "simulasyon_hata_sahiplik_olcumu.py",
    "rapor_teslim_ayrimi_olcumu.py",
    "embedder_kirmizi_sahiplik_olcumu.py",
    "bom_temizle_sahiplikli.py",
    "bom_izleme_denetimi.py",
    "rapor_dosya_sayaci.py",
    "brif_eksik_bolum_olcumu.py",
    "uretim_kod_kaybi_olcumu.py",
    "goc_izleme_olcumu.py",
    "plan_uyusmazlik_olcumu.py",
    "kirmizi_sahiplik_olcumu.py",
    "tsg_esleme_mandal_kirma_denemesi.py",
    "tsg_kapanis_kaydi.py",
    "teslim_iddiasi_denetimi.py",
    "tetik_log_alan_cevrimi.py",
    "acik_soru_listesi.py",
    "iki_teslim_bes_adim_denetim.py",
    "tam_suit_kova_olcumu.py",
    "kodlama_uyari_kovasi.py",
    "dosya_sonu_duzelt.py",
    "rag_korpus_olcum.py",
]

TARAMA_DIZINLER = ["scripts", "tests", "src", "web_dashboard", "data/orchestrator"]

# Tarayici kendisini cagiran saymamali: bu betigin KENDI govdesi URETILEN
# listesini icerdigi icin, haric tutulmazsa listedeki HER ad icin "1 cagiran"
# bulunur ve tum kararlar KAL'a doner (D-224: yanlis pozitif tum karari bozar).
# Ilk calistirmada 19 dosyanin 19'u da "KAL" ciktinin tek sebebi buydu.
OLCUM_ARACLARI = {
    "tehis_betik_olcumu.py",   # bu dosya
    "arsiv_genis_denetim.py",  # genis kapsamli kume denetimi (ikiz arac)
}
KENDI = Path(__file__).name
assert KENDI in OLCUM_ARACLARI, (
    f"bu dosya ({KENDI}) OLCUM_ARACLARI icinde degil — tuketici taramasi "
    "kendini cagiran sayar ve tum kararlar KAL olur"
)

# teslim raporlari: kanit adresi
RAPORLAR = list((ROOT / "data" / "orchestrator").glob("*_rapor_*.md"))
rapor_metin = "\n".join(
    p.read_text(encoding="utf-8", errors="replace") for p in RAPORLAR)

print("=== 1) DOSYA VARLIK KONTROLU ===")
var, yok = [], []
for ad in URETILEN:
    (var if (ROOT / "scripts" / ad).exists() else yok).append(ad)
print(f"  mevcut : {len(var)}")
print(f"  yok    : {len(yok)} {yok}")

print("\n=== 2) TUKETICI TARAMASI (kim cagirir?) ===")
# kod tabaninda adi gecen yerler
kaynak_havuzu = []
haric_sayisi = 0
for d in TARAMA_DIZINLER:
    kok = ROOT / d
    if not kok.exists():
        continue
    for p in kok.rglob("*"):
        if p.suffix not in (".py", ".js", ".html", ".yml", ".md", ".txt"):
            continue
        if p.name in OLCUM_ARACLARI:
            haric_sayisi += 1
            continue  # olcum araci: tuketici sayilmaz
        if p.name in URETILEN and p.parent.name == "scripts":
            continue  # aday dosyanin kendisi
        kaynak_havuzu.append(p)
print(f"  taranan dosya : {len(kaynak_havuzu)}")
print(f"  haric tutulan : {haric_sayisi} (olcum araci: {', '.join(sorted(OLCUM_ARACLARI))})")

def tuketici_ara(ad):
    desen = re.compile(re.escape(ad))
    bulunan = []
    for p in kaynak_havuzu:
        if p.suffix == ".md" and "_rapor_" in p.name:
            continue  # raporlar ayrica ele alinir
        try:
            if desen.search(p.read_text(encoding="utf-8", errors="replace")):
                bulunan.append(str(p.relative_to(ROOT)).replace("\\", "/"))
        except Exception:
            continue
    return bulunan

def raporda_geciyor(ad):
    return ad in rapor_metin

print(f"  {'dosya':42} {'tuketici':>9}  {'raporda':>8}  {'karar':>7}")
print("  " + "-" * 74)
kararlar = {"KAL": [], "ARSIV": []}
for ad in var:
    t = tuketici_ara(ad)
    r = raporda_geciyor(ad)
    if t:
        karar, gerekce = "KAL", f"{len(t)} cagiran: {t[0]}"
    elif r:
        karar, gerekce = "KAL", "teslim raporunda KANIT olarak adresli"
    else:
        karar, gerekce = "ARSIV", "tuketicisi yok, raporda adresli degil"
    kararlar[karar].append(ad)
    print(f"  {ad:42} {len(t):9}  {str(r):>8}  {karar:>7}  {gerekce[:40]}")

print("\n=== 2b) KUME DENETIMI (tek tek degerlendirme yetmez) ===")
# Gecici olcum betikleri birbirini cagirir. Bu yuzden tek tek bakildiginda
# hepsi "1 cagiran" cikar ve HICBIR sey arsivlenemez — o zaman da temizlik
# calismaz. Dogru olcut birim kumedir: kumeden disariya cagri varsa KAL,
# yoksa kume tek catida arsivlenir.
#
# Ayirim onemli: kanit Defteri/kayit dosyalarinda gecen ad (bulgu_defteri.md,
# ajan-chat.jsonl, *_rapor_*.md) "cagiran" degil, KANIT adresidir (D-193) —
# KAL sayilir. Kod cagrisi (import, subprocess, shell) KAL sayilir.
KANIT_DIZINLERI = ("data/orchestrator",)

def kod_cagirisi(ad):
    """Kume disindan GERCEKTEN kod cagirisi var mi? Kanit sayilmaz."""
    desen = re.compile(re.escape(ad))
    bulanlar = []
    for p in kaynak_havuzu:
        if p.name in URETILEN or p.name in OLCUM_ARACLARI:
            continue  # adaylarin kendisi + olcum araclari kumede
        try:
            m = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        desenler = (
            f"import {ad[:-3]}", f"from {ad[:-3]}", f'"{ad}"', f"'{ad}'",
            f"python {ad}", f"scripts/{ad}", f"{ad} --",
        )
        if any(d in m for d in desenler):
            bulanlar.append(str(p.relative_to(ROOT)).replace("\\", "/"))
    return bulanlar

KUME = list(kararlar["ARSIV"])
disari = {}
for ad in KUME:
    bl = kod_cagirisi(ad)
    if bl:
        disari[ad] = bl

print(f"  kume boyutu: {len(KUME)} dosya (KAL olanlar kume disi)")
if disari:
    print("  KUME DISI KOD CAGIRISI VAR -> kume tasinmaz:")
    for ad, bl in sorted(disari.items()):
        print(f"    {ad:38} {len(bl)} -> {bl[0]}")
else:
    print("  KUME DISI KOD CAGIRISI YOK -> kume tamami arsivlenebilir.")
    for ad in KUME:
        print(f"    {ad:38} raporda kanit: {raporda_geciyor(ad)}")

print("\n=== 3) OZET ===")
print(f"  KAL   : {len(kararlar['KAL'])}")
print(f"  ARSIV : {len(kararlar['ARSIV'])}")
print("\n--- KAL (gerekce) ---")
for ad in kararlar["KAL"]:
    t = tuketici_ara(ad)
    why = (f"{len(t)} cagiran" if t else "raporda kanit")
    print(f"  {ad:42} {why}")
print("\n--- ARSIV adaylari ---")
for ad in kararlar["ARSIV"]:
    print(f"  {ad}")

print("\n=== 4) GIT DURUMU (D-193 riski) ===")
st = subprocess.run(["git", "status", "--porcelain"],
                    capture_output=True, text=True, encoding="utf-8",
                    errors="replace", cwd=str(ROOT)).stdout.splitlines()
yeni = [s for s in st if s.strip().startswith("??")]
degis = [s for s in st if not s.strip().startswith("??")]
print(f"  degistirilmis izlenen : {len(degis)}")
print(f"  yeni (izlenmeyen)     : {len(yeni)}")
if yeni:
    for s in yeni:
        print(f"    {s[3:]}")

print("\n=== 5) KARAR (D-244: yedek -> dogrula -> tasima) ===")
print("  ARSIV adayi sayisi:", len(kararlar["ARSIV"]))
print("  Hepsi icin on kosul: yedek alinir (yedekler/arsiv/ tek cati),")
print("  sonra scripts/den tasinir. SILME YOK (D-002).")
print("  Uygulayan betik YOK: tehis_betik_temizle.py diskte bulunamadi,")
print("  o yuzden bu arac yalnizca OLÇER, taşımaz. Arsiv kararini")
print("  kanonik komutu olan gorev_kutusu/bakim tarafi uygular.")
