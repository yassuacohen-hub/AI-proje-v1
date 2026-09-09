"""OSTİM veri kalite analizi scripti.

JSONL dosyasını okur, kalite skoru hesaplar, rapor üretir.
"""
import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "ostim" / "firmalar_sayfa1.jsonl"
OUTPUT = ROOT / "data" / "ostim" / "kalite_raporu.md"

if not INPUT.exists():
    print(f"HATA: {INPUT} bulunamadi. Once scrape yapin.")
    sys.exit(1)

# Veriyi oku
records = []
with open(INPUT, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            records.append(json.loads(line))

print(f"Toplam kayit: {len(records)}")

# Kalite skoru
def kalite_skoru(r):
    skor = 0
    if r.get("unvan"):
        skor += 10
    if r.get("telefonler") and len(r["telefonler"]) > 0:
        skor += 20
    if r.get("emailler") and len(r["emailler"]) > 0:
        skor += 15
    if r.get("web_sitesi"):
        skor += 15
    if r.get("adres"):
        skor += 10
    if r.get("sektor"):
        skor += 10
    if r.get("sosyal_medya") and len(r["sosyal_medya"]) > 0:
        skor += 10
    if r.get("vergi_no"):
        skor += 5
    if r.get("osb_parsel"):
        skor += 5
    return min(skor, 100)

# Hesapla
for r in records:
    r["kalite_skoru"] = kalite_skoru(r)

# Istatistik
toplam = len(records)
ortalama = sum(r["kalite_skoru"] for r in records) / toplam
yuksek = sum(1 for r in records if r["kalite_skoru"] >= 80)
orta = sum(1 for r in records if 60 <= r["kalite_skoru"] < 80)
dusuk = sum(1 for r in records if 40 <= r["kalite_skoru"] < 60)
cok_dusuk = sum(1 for r in records if r["kalite_skoru"] < 40)

# Alan bazli doluluk
unvan_dolu = sum(1 for r in records if r.get("unvan"))
tel_dolu = sum(1 for r in records if r.get("telefonler") and len(r["telefonler"]) > 0)
email_dolu = sum(1 for r in records if r.get("emailler") and len(r["emailler"]) > 0)
web_dolu = sum(1 for r in records if r.get("web_sitesi"))
adres_dolu = sum(1 for r in records if r.get("adres"))
sektor_dolu = sum(1 for r in records if r.get("sektor"))

# Sektor dagilimi
sektorler = Counter(r.get("sektor") or "Boş" for r in records)

# Telefon basina ortalama
tel_sayilari = [len(r.get("telefonler", [])) for r in records]
tel_ortalama = sum(tel_sayilari) / toplam if toplam > 0 else 0
tel_toplam = sum(tel_sayilari)

# E-posta benzer
email_sayilari = [len(r.get("emailler", [])) for r in records]
email_ortalama = sum(email_sayilari) / toplam if toplam > 0 else 0
email_toplam = sum(email_sayilari)

# Rapor olustur
rapor = []
rapor.append("# OSTİM Veri Kalite Raporu")
rapor.append("")
rapor.append(f"**Tarih:** {datetime.now().isoformat(timespec='seconds')}")
rapor.append(f"**Kaynak:** `{INPUT.name}`")
rapor.append(f"**Toplam Kayıt:** {toplam:,}")
rapor.append("")
rapor.append("## 1. Genel Kalite Skoru")
rapor.append("")
rapor.append("| Metrik | Değer |")
rapor.append("|---|---:|")
rapor.append(f"| Ortalama skor | **{ortalama:.1f}** / 100 |")
rapor.append(f"| Yüksek (80-100) | {yuksek} (%{yuksek*100/toplam:.1f}) |")
rapor.append(f"| Orta (60-79)    | {orta} (%{orta*100/toplam:.1f}) |")
rapor.append(f"| Düşük (40-59)   | {dusuk} (%{dusuk*100/toplam:.1f}) |")
rapor.append(f"| Çok Düşük (0-39) | {cok_dusuk} (%{cok_dusuk*100/toplam:.1f}) |")
rapor.append("")

rapor.append("## 2. Alan Bazlı Doluluk")
rapor.append("")
rapor.append("| Alan | Dolu | Yüzde |")
rapor.append("|---|---:|---:|")
rapor.append(f"| Ünvan | {unvan_dolu} | %{unvan_dolu*100/toplam:.1f} |")
rapor.append(f"| Telefon | {tel_dolu} | %{tel_dolu*100/toplam:.1f} |")
rapor.append(f"| E-posta | {email_dolu} | %{email_dolu*100/toplam:.1f} |")
rapor.append(f"| Web Sitesi | {web_dolu} | %{web_dolu*100/toplam:.1f} |")
rapor.append(f"| Adres | {adres_dolu} | %{adres_dolu*100/toplam:.1f} |")
rapor.append(f"| Sektör | {sektor_dolu} | %{sektor_dolu*100/toplam:.1f} |")
rapor.append("")

rapor.append("## 3. Çoklu Alan İstatistikleri")
rapor.append("")
rapor.append("| Alan | Toplam | Ortalama/Firma |")
rapor.append("|---|---:|---:|")
rapor.append(f"| Telefon | {tel_toplam} | {tel_ortalama:.2f} |")
rapor.append(f"| E-posta | {email_toplam} | {email_ortalama:.2f} |")
rapor.append("")

rapor.append("## 4. Sektör Dağılımı")
rapor.append("")
rapor.append("| Sektör | Firma |")
rapor.append("|---|---:|")
for s, n in sektorler.most_common(20):
    rapor.append(f"| {s} | {n} |")
rapor.append("")

# En iyi 5 firma (kalite sirali)
rapor.append("## 5. En Yüksek Kaliteli 5 Firma")
rapor.append("")
en_iyiler = sorted(records, key=lambda r: r["kalite_skoru"], reverse=True)[:5]
for r in en_iyiler:
    tel = r.get("telefonler", [])
    em = r.get("emailler", [])
    web = r.get("web_sitesi", "")
    rapor.append(f"### {r['unvan']} (skor: {r['kalite_skoru']})")
    rapor.append(f"- Telefon: {', '.join(tel) if tel else '—'}")
    rapor.append(f"- E-posta: {', '.join(em) if em else '—'}")
    rapor.append(f"- Web: {web or '—'}")
    rapor.append("")

# En kotu 5 firma
rapor.append("## 6. En Düşük Kaliteli 5 Firma (İyileştirme Gerekli)")
rapor.append("")
en_kotuler = sorted(records, key=lambda r: r["kalite_skoru"])[:5]
for r in en_kotuler:
    tel = r.get("telefonler", [])
    em = r.get("emailler", [])
    eksikler = []
    if not tel: eksikler.append("telefon")
    if not em: eksikler.append("email")
    if not r.get("web_sitesi"): eksikler.append("web")
    if not r.get("adres"): eksikler.append("adres")
    rapor.append(f"### {r['unvan']} (skor: {r['kalite_skoru']})")
    rapor.append(f"- Eksik alanlar: {', '.join(eksikler) if eksikler else 'yok'}")
    rapor.append("")

rapor.append("## 7. Sonraki Adımlar")
rapor.append("")
rapor.append("1. **Detay sayfaları:** Liste sayfasında olmayan `web_sitesi`, `adres`, `sosyal_medya` alanları için detay scrape gerekli")
rapor.append("2. **Adres çıkarımı:** Detay sayfalarındaki 'Adres' etiketli bölüm parse edilebilir")
rapor.append("3. **Sosyal medya:** Logo/footer'dan LinkedIn, Twitter, Facebook, Instagram linkleri çıkarılabilir")
rapor.append("4. **Cross-source merge:** vergi_no birincil anahtar olarak, OSTİM + MERSİS + ASO birleştirilecek")
rapor.append("5. **Kalite iyileştirme:** 40'ın altında kalan firmalar için manuel doğrulama veya detay sayfası tekrar scrape")
rapor.append("")

# Yaz
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(rapor))

print(f"Rapor yazildi: {OUTPUT}")
print(f"Boyut: {OUTPUT.stat().st_size} bytes")
print(f"Toplam: {toplam}, Ortalama kalite: {ortalama:.1f}")