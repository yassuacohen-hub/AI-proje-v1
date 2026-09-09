"""OSTİM 1-sayfa test scrape (yaklaşık 300 firma).

Karar referansı: V10/10_ankara_osb_sentez Karar 11
"""
import json
import sys
import time
from pathlib import Path

# Proje kökünü path'e ekle
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.company_master.etl.scrapers.ostim_scraper import (
    fetch_robots, fetch_firmalar, scrape_firma_full, USER_AGENT, RATE_LIMIT_SECONDS
)

OUTPUT_DIR = ROOT / "data" / "ostim"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "firmalar_sayfa1.jsonl"

URL = "https://www.ostim.org.tr/firmalar"

print(f"[{time.strftime('%H:%M:%S')}] Basladi")
print(f"URL: {URL}")
print(f"Output: {OUTPUT_FILE}")
print()

# robots.txt kontrol
disallowed = fetch_robots()
print(f"robots.txt disallow sayisi: {len(disallowed)}")

# 1. sayfa scrape (detay sayfaları olmadan, hızlı)
print()
print("=== LISTE SAYFASI (DETAY YOK) ===")
firmalar = fetch_firmalar(URL, sayfa=1)
print(f"Bulunan firma: {len(firmalar)}")

if not firmalar:
    print("HATA: 0 firma, cikiliyor")
    sys.exit(1)

# JSONL'e yaz
written = 0
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for firma in firmalar:
        # dataclass'i dict'e cevir
        record = {
            "unvan": firma.unvan,
            "telefonler": firma.telefonler,
            "emailler": firma.emailler,
            "web_sitesi": firma.web_sitesi,
            "adres": firma.adres,
            "sosyal_medya": firma.sosyal_medya,
            "vergi_no": firma.vergi_no,
            "osb_parsel": firma.osb_parsel,
            "sektor": firma.sektor,
            "slug": firma.slug,
            "kaynak": firma.kaynak,
            "cekilme_tarihi": firma.cekilme_tarihi,
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        written += 1

print(f"Yazilan: {written}")
print(f"Dosya: {OUTPUT_FILE}")
print(f"Boyut: {OUTPUT_FILE.stat().st_size} bytes")

# Ornek kayit goster
print()
print("=== ILK 3 FIRMA ===")
for firma in firmalar[:3]:
    print(f"  Unvan    : {firma.unvan[:60]}")
    print(f"  Telefon  : {firma.telefonler}")
    print(f"  Email    : {firma.emailler}")
    print(f"  Slug     : {firma.slug}")
    print()

# Istatistik
telefonlu = sum(1 for f in firmalar if f.telefonler)
emailli = sum(1 for f in firmalar if f.emailler)
print(f"=== ISTATISTIK ===")
print(f"Toplam firma       : {len(firmalar)}")
print(f"Telefonu olan      : {telefonlu} (%{telefonlu*100/len(firmalar):.1f})")
print(f"Emaili olan        : {emailli} (%{emailli*100/len(firmalar):.1f})")
print()
print(f"[{time.strftime('%H:%M:%S')}] Bitti")
