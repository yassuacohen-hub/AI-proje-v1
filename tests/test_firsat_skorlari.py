# -*- coding: utf-8 -*-
"""Firsat skoru mandallari (VERI-SKOR-MOTORU-01, D-319 / K4 resmi skor seti).

SSOT: AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md
      :215-228 gate esikleri · :229-240 skor tanimlari · :241-266 ensemble

Bu dosya bir mandaldir, is yapan kod degil. Test modulu duz calisir:
    python -X utf8 tests/test_firsat_skorlari.py

Her assert'in neyi korudugu docstring'inde yazilidir (D-265/2: sayi donduran
test hicbir sey garanti etmez).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from company_master.intelligence.skor_motoru import (  # noqa: E402
    AGIRLIKLAR,
    FIELD_BONUS,
    KALIBRASYON,
    KAPI_ESIKLERI,
    SIGNAL_BONUS,
    SKORLAR,
    SURUM,
    compute_ensemble_score,
    evidence_strength,
    firsat_recalc,
    firsat_skorlari,
    fit_score,
    kapi_gecildi_mi,
    need_score,
    timing_score,
)

GOC = ROOT / "src" / "company_master" / "schema" / "migrations" / "0049_firsat_skorlari.sql"
MODUL = ROOT / "src" / "company_master" / "intelligence" / "skor_motoru.py"

basari = 0
toplam = 0


def mandal(ad: str, kosul: bool, gerekce: str = "") -> None:
    global basari, toplam
    toplam += 1
    if kosul:
        basari += 1
    print(f"  [{'OK' if kosul else 'KIRIK'}] {ad}")
    if gerekce:
        print(f"         {gerekce}")


def _skor_kolonlarinda_default(sql: str) -> list[str]:
    """Skor kolonlarinin tanim satirlarinda veren `DEFAULT` olanlari dondurur.

    Satir bazli tarama. Regex tabanli tarama burada YANLIS NEGATIF verir:
    kolon tanimi `need_score NUMERIC(5,2) DEFAULT 0` iceriyorsa
    `NUMERIC(5,2)`'deki virgul, `need_score` ile `DEFAULT` arasindaki
    karakter sinifini keser ve eslesme hic olusmaz. Mandal kirmaya
    calisildiginda ortaya cikti (D-268/5: metin taramasi mandal degildir).
    """
    supheli = []
    for satir in sql.splitlines():
        if not re.match(r"^\s*(need_score|fit_score|timing_score|"
                        r"ensemble_score)\s+\S", satir):
            continue
        if re.search(r"\bDEFAULT\b", satir, re.I):
            supheli.append(satir.strip())
    return supheli


print("=== FIRSA SKORU MANDALLARI ===\n")

# ---------------------------------------------------------------- D-249
# "Veri yok" ile "0 puan" ayri degerlerdir. Bu kararin olculebilir hali.
print("-- D-249: veri yok != 0 puan --")

mandal(
    "need_score(None) -> None (0 degil)",
    need_score(None) is None,
    "hic olculemeyen sinyal sayisi 0 sayilmaz",
)
mandal(
    "need_score(0) -> 0.0 (olculemis sifir sinyal)",
    need_score(0) == 0.0,
    "olculebilen ama sifir olan sinyal GERCEK sifirdir",
)
mandal(
    "fit_score hicbiri None -> None (F3 bos tablo senaryosu)",
    fit_score(None, None, None) is None,
    "F3 tamamlanana kadar uc girdi tablosu bos; sahte 0 uretilmez",
)
mandal(
    "fit_score(0,0,0) -> 0.0",
    fit_score(0, 0, 0) == 0.0,
    "tablolar var ama hic kayit yok: bu 'uyumsuz' degil 'olcum yok' — "
    "yine de 0.0, cunku sayim yapildi",
)
mandal(
    "timing_score(None) -> None",
    timing_score(None) is None,
)
mandal(
    "evidence_strength(None, None) -> None",
    evidence_strength(None, None) is None,
)

# ---------------------------------------------------------------- D-249/2
print("\n-- D-249/2: eksik veri firmayi cezalandirmaz --")

mandal(
    "timing yas arttikca puan azalir (monoton)",
    timing_score(0, False) > timing_score(90, False) > timing_score(365, False),
    "SSOT:236 recency — yeni kanit daha yuksek puan",
)
mandal(
    "fit kismi doluluk: tek tablo dolu 0 vermez",
    fit_score(3, None, None) > 0.0,
    "bir tablo ETL ile dolmusken puan uretilir; eksik parca 0 sayilmaz "
    "(agirlik disarida birakilir)",
)

# ---------------------------------------------------------------- SSOT:241-266
print("\n-- SSOT:241-266 ensemble formulu --")

mandal(
    "agirliklar SSOT:246-251 ile birebir",
    AGIRLIKLAR == {"need": 0.30, "fit": 0.35,
                   "timing": 0.20, "evidence": 0.15},
    f"toplam {sum(AGIRLIKLAR.values()):.2f} (SSOT 1.0)",
)
mandal(
    "agirlik toplami 1.0 (kayan nokta dahil)",
    abs(sum(AGIRLIKLAR.values()) - 1.0) < 1e-9,
)
mandal(
    "bonUS miktarlari SSOT:260-261",
    FIELD_BONUS == 0.05 and SIGNAL_BONUS == 0.03,
    "V7'deki +0.20/+0.15 V9'de kisaltildi",
)

# Elle hesaplanmis referans: 0.30*0.6 + 0.35*0.8 + 0.20*0.5 + 0.15*0.7
# = 0.18 + 0.28 + 0.10 + 0.105 = 0.665
referans = (0.30 * 0.6 + 0.35 * 0.8 + 0.20 * 0.5 + 0.15 * 0.7)
mandal(
    "ensemble elle hesaplanan degerle birebir",
    abs(compute_ensemble_score(0.6, 0.8, 0.5, 0.7) - referans) < 1e-9,
    f"referans {referans:.6f}",
)

mandal(
    "field bonusu eklenir (SSOT:260)",
    abs(compute_ensemble_score(0.6, 0.8, 0.5, 0.7,
                               is_field_verified=True) - referans - 0.05) < 1e-9,
)
mandal(
    "sinyal bonusu eklenir (SSOT:261)",
    abs(compute_ensemble_score(0.6, 0.8, 0.5, 0.7,
                               active_intent_10d=True) - referans - 0.03) < 1e-9,
)
mandal(
    "iki bonus birlikte eklenir",
    abs(compute_ensemble_score(0.6, 0.8, 0.5, 0.7,
                               is_field_verified=True,
                               active_intent_10d=True)
        - referans - 0.08) < 1e-9,
)
mandal(
    "clamp: tam puan + bonus 1.0'u asamaz (SSOT:263)",
    compute_ensemble_score(1.0, 1.0, 1.0, 1.0,
                           is_field_verified=True,
                           active_intent_10d=True) == 1.0,
)
mandal(
    "clamp alt sinir: negatif giris 0'a dayanir",
    compute_ensemble_score(-5.0, 0.0, 0.0, 0.0) == 0.0,
)
mandal(
    "bilesen None ise ensemble None (0 saymaz)",
    compute_ensemble_score(0.6, None, 0.5, 0.7) is None,
    "D-249: eksik bileseni 0 saymak 'olcduk ve sifir bulduk' olurdu",
)
mandal(
    "agirlik anahtari eksikse None (KeyError degil)",
    compute_ensemble_score(0.6, 0.8, 0.5, 0.7,
                           weights={"need": 0.5, "fit": 0.5}) is None,
)

# ---------------------------------------------------------------- SSOT:215-228
print("\n-- SSOT:215-228 opportunity gate'leri --")

mandal(
    "gate esikleri SSOT:222-225 ile birebir",
    KAPI_ESIKLERI == {"need": 0.25, "fit": 0.30,
                      "evidence": 0.20, "timing": 0.30},
)

sonuc = kapi_gecildi_mi(0.9, 0.9, 0.9, 0.9)
mandal(
    "yuksek skorlar dort gate'i de gecer",
    all(v == "gecti" for v in sonuc["durum"].values()),
)
mandal(
    "need < 0.25 ise CONTACT_NOW yasak (SSOT:227)",
    kapi_gecildi_mi(0.10, 0.9, 0.9, 0.9)["contact_now_yasak"] is True,
    "V8 hard gate'i: max INVESTIGATE",
)
mandal(
    "need >= 0.25 iken CONTACT_NOW yasak degil",
    kapi_gecildi_mi(0.30, 0.9, 0.9, 0.9)["contact_now_yasak"] is False,
)
olculmeyen = kapi_gecildi_mi(None, 0.9, 0.9, 0.9)
mandal(
    "olculemeyen gate 'kalmadi' degil 'olculmedi' der",
    olculmeyen["durum"]["need"] == "olculmedi"
    and olculmeyen["olculmeyen"] == ["need"],
    "D-249: bilinmeyen deger basarisiz sayilmaz",
)

# ---------------------------------------------------------------- D-319
print("\n-- D-319: resmi skor seti K4 --")

mandal(
    "dort skor adi SSOT:232-237 ile birebir",
    SKORLAR == ("need_score", "fit_score", "timing_score", "ensemble_score"),
    "K2'nin 8 skoru risk motorunda yasar; burasi K4",
)
mandal(
    "risk skoru adi bu modulde YOK (D-211 ikiz yasagi)",
    not any("trust" in ad or "risk" in ad or "fraud" in ad for ad in SKORLAR),
)
mandal(
    "surum tanimli (D-250/6: agirlik degisince surum artar)",
    SURUM == "v1" and len(SURUM) > 0,
)

# ---------------------------------------------------------------- D-256/2
print("\n-- D-256/2: tabloya yazan tek yol --")

kaynak = MODUL.read_text(encoding="utf-8")
yazan = re.findall(r"(INSERT\s+INTO|UPDATE)\s+company_opportunity_scores",
                   kaynak, re.I)
mandal(
    "bu modulde INSERT/UPDATE yalniz _YAZ sabitinde",
    len(yazan) == 1 and kaynak.count("INSERT INTO company_opportunity_scores") == 1,
    f"bulunan yazma ifadesi: {len(yazan)} (firsat_recalc tek kapidir)",
)

# ---------------------------------------------------------------- F3 boslugu
print("\n-- F3 bagimliligi (bos tablo senaryosu) --")

bos_kayit = firsat_skorlari({
    "sinyal_tur_sayisi": 0, "gecmis_desen": 0,
    "yetenek_sayisi": None, "sertifika_sayisi": None, "anahtar_kisi_sayisi": None,
    "kaynak_sayisi": 0, "kaynak_tur_sayisi": 0,
    "son_kaynak_zamani": None, "son_10_gun_sinyal": 0, "kimlik_tamligi": None,
})
mandal(
    "F3 bosken fit_score None",
    bos_kayit["fit_score"] is None,
)
mandal(
    "F3 bosken ensemble None (bilesen eksik)",
    bos_kayit["ensemble_score"] is None,
    "ensemble fit'e bagli; fit yoksa ensemble de olculmez",
)

# ---------------------------------------------------------------- goc
print("\n-- goc dosyasi tutarliligi --")

goc = GOC.read_text(encoding="utf-8")
mandal("goc dosyasi diskte", GOC.exists())
mandal(
    "goc dort skoru iceriyor",
    all(ad in goc for ad in SKORLAR),
)
mandal(
    "hicbir skor kolonunda DEFAULT 0 yok (D-249)",
    not _skor_kolonlarinda_default(goc),
    "satir bazli: NUMERIC(5,2) icindeki virgul metin taramasini kesiyordu — "
    "onceki regex sessizce hicbir sey gormuyordu (D-268/5: metin taramasi "
    "mandal yerine gecmez)",
)
mandal(
    "goc aralik korumasi tasiyor (0.0-1.0)",
    "BETWEEN 0.0 AND 1.0" in goc,
    "NUMERIC(5,2) tek basina araligi korumaz; CHECK/kisit gerekir (D-245)",
)

# ---------------------------------------------------------------- yazma kapisi
print("\n-- yazma kapisi --")

mandal(
    "firsat_recalc tek yazma fonksiyonu olarak export ediliyor",
    callable(firsat_recalc),
)

print(f"\n=== SONUC: {basari}/{toplam} mandal ===")
if basari != toplam:
    print("KIRIK MANDAL VAR — duzeltilmeden teslim yok.")
    sys.exit(1)
print("Tum mandallar gecti.")
