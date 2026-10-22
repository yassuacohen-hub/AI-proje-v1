# -*- coding: utf-8 -*-
"""SON-13D: SON-13 hipotezinin OLUMLENMESI (tek basina claude oneki yetmez,
kaydirma da var) + once/sonra kaniti (onek verince gorunur oldular). Tavan 700."""
from pathlib import Path

HEDEF = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\ihsan_project_context.md")
TAVAN = 700

KAYIT = """- **SON-13D (2026-10-21 ~00:52 — 'CLAUDE ONEKI' KURALI DOGRULANDI AMA TEK MEKANIZMA DEGIL: + KAYDIRMA SINIRI):** Uck ekran/config karsilastirmasi satir satir sayildi. **1. ekran (10 satir)** = config'in ilk ~13 pozisyonundan `claude` icermeyen 3'ü (**6. sıradaki `yasu-9router`, 7. `mimir-dis`, 9. `cl/nvidia/nemotron-3-ultra…:free`**) dusurulerek → 10 satır. **2. ekran (13 satir)** = config'in **ILK 13 KAYDIYLA BIREBIR AYNI SIRADA** (hepsi claude iceriyor → hicbiri dusurulmedi, 13 = pencere siniri). **ONCE/SONRA KANITI:** `claude-karma-evren` ve `claude-mimir` combo'lari acildiktan sonra ayni icerikli satirlar ekranda BELIRDI → id filtresi (adinda `claude` gecmeli) GERCEK; `claude-` onekli combo acmak dogru cozum (SON-13 hakli). **IKINCI MEKANIZMA: kaydirma/pencere siniri ~13 satir** → 14+ sıradaki kayitlar ekrana sigmiyor, SILINMIS DEGIL. Uckuncu suphe: kaybolan Qwen satirlarinin etiketindeki `⚠` (U+26A0) → `sebebe_temizle()` ile kaldirildi, sembole gerek yok. **UYGULANAN KOZMETIK+KESIN COZUM:** Qwen satirlari `ADAYLAR` listesinde **6-7-8. siraya** tasi ndi (pencere siniri icinde kalsin) → kutu 17 kayit, Qwen artik gorunur konumda; etiketler duz metin ('LİMİT (00:00 UTC'de açılır)'). **KURAL (kalici): 'model kutuda yok' ihbarinda uc olcum birden yapilir: (a) config'de kayit var mi (`--durum`), (b) gorunen satir sayisi pencere sinirina esit mi (kaydirma), (c) id'de `claude` geciyo mu + etikette sembol var mi. Korelasyon tek basina kanit degil; once/sonra deneyi şart.**
"""

metin = HEDEF.read_text(encoding="utf-8")
if "SON-13D (2026-10-21" in metin:
    print("SON-13D zaten var")
    raise SystemExit(0)
satirlar = metin.splitlines()
for i, s in enumerate(satirlar):
    if s.startswith("- **SON-13 (2026-10-21"):
        satirlar.insert(i + 1, KAYIT.rstrip("\n"))
        break
else:
    satirlar.insert(0, KAYIT.rstrip("\n"))
son = "\n".join(satirlar) + "\n"
sayi = son.count("\n")
if sayi > TAVAN:
    raise SystemExit(f"YAZILMADI: {sayi} > {TAVAN}")
HEDEF.write_text(son, encoding="utf-8")
print(f"YAZILDI · satir: {sayi}/{TAVAN}")
