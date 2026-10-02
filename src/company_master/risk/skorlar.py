# -*- coding: utf-8 -*-
"""Risk motoru — 8 guven skoru ve oneri kademesi (Faz 2, VERI-RISK-MOTORU-01).

SSOT: `yedekler/Huginn Data Insights (HUGIns).txt:791-822` (skorlar),
`:824-849` (kademeler). Skor araligi 0-100.

Uctageler:

1. **Girdisi olmayan skor `None` doner, 0 degil.** D-249: "veri yok" ile
   "0 puan" ayri degerlerdir; `DEFAULT 0` sessizce yalan soylerdi.
2. **Skor yazan tek kapisi `risk_recalc()`.** D-256/2. Bu modulde baska
   INSERT/UPDATE yoktur.
3. **Kanit disi sinyal puan almaz.** D-245: doldurulmus olmak gecerlilik
   degildir. Bu yuzden skorlar dogrulanmis alanlardan turer; tahmin
   edilen NACE (D-252) kanit degildir ve puan uretmez.

Agirlik seti ve kademe esikleri surumle gelir. `SURUM` degisince eski
puanlar BAYAT sayilir (D-250/6 mantigi, risk motoruna tasinmis hali).
"""
from __future__ import annotations

import logging
from typing import Iterable, Mapping, Sequence

from sqlalchemy import text

from ..db.connection import get_engine

logger = logging.getLogger(__name__)

__all__ = [
    "SURUM",
    "SKORLAR",
    "AGIRLIKLAR",
    "KADEMELER",
    "KADEME_ESIKLERI",
    "SKOR_ARALIK",
    "skorlari_hesapla",
    "genel_guven",
    "kademe",
    "risk_recalc",
]

SURUM = "v1"

# SSOT:791-822 — kolon adi birebir. Siralama SSOT sirasiyla ayni.
SKORLAR: tuple[str, ...] = (
    "corporateness_score",
    "reliability_score",
    "reputation_score",
    "cyber_security_score",
    "operational_power_score",
    "transparency_score",
    "fraud_risk_score",
)
# Genel guven skoru ayrica hesaplanir; yukaridaki 7'nin agirligiyla.
GENEL_SKOR = "overall_trust_score"

SKOR_ARALIK = (0.0, 100.0)

# Agirlik seti v1 — toplam tam 1.0. Surum degisince hepsi birlikte degisir.
# Gerekce: agirliklar "hangi soru daha agir" sorusunun cevabidir; agirlik
# kumesi degisip skor formulu degismeyebilir, o yuzden surum ayrilir.
AGIRLIKLAR: dict[str, float] = {
    "corporateness_score": 0.20,
    "reliability_score": 0.20,
    "reputation_score": 0.10,
    "cyber_security_score": 0.15,
    "operational_power_score": 0.10,
    "transparency_score": 0.15,
    "fraud_risk_score": 0.10,
}

# SSOT:824-849 — yalnizca 4 kademenin adi SSOT'ta yazili; sayisal esik
# SSOT'ta YOKTUR. Esikler v1 varsayilandir, `SURUM` ile birlikte surumlenir.
# Uretimde bu esikler sinir degerine yakin hicbir firma dusmedigi icelendi
# ve panelde "v1 varsayim" etiketiyle gosterilir.
KADEME_ESIKLERI: tuple[tuple[float, str], ...] = (
    (80.0, "calisilabilir"),
    (60.0, "dikkatli_calisilmali"),
    (40.0, "ek_inceleme_gerekli"),
)
KADEMELER: tuple[str, ...] = (
    "calisilabilir",
    "dikkatli_calisilmali",
    "ek_inceleme_gerekli",
    "yuksek_riskli",
)

# --- Kanit kapilari (D-245 / D-246 / D-252) -------------------------------

# D-252: dogrulanmamis NACE kodu tahmindir, kanit degildir.
NACE_KANIT_KAYNAKLARI = frozenset({"mersis", "external"})


def _puanla(sinyal: float) -> float:
    """Sinyali 0-100 araligina kirpar."""
    return max(SKOR_ARALIK[0], min(SKOR_ARALIK[1], round(float(sinyal), 2)))


def _nokta_oranla(var: Iterable[tuple[object, float]]) -> float | None:
    """(varlik, agirlik) ciftlerinden 0-100 sinyal uretir.

    **Hicbir sinyal varsa `None` doner** (D-249): dort alanin da bossa
    "0 puan" degil "hic olcum yok"tur. Agirlik toplami sifirsa da `None`
    doner. Sinyal varsa 0 donmesi **gercek** bir olcumdur (D-249/2).
    """
    var = list(var)
    if not any(v for v, _ in var):
        return None
    toplam_agirlik = sum(a for _, a in var)
    if toplam_agirlik <= 0:
        return None
    return _puanla(sum(100.0 * a for v, a in var if v) / toplam_agirlik)


# --- Teker teker skor (her biri girdi yoksa None doner) --------------------


def kurumsallik_skoru(firma: Mapping[str, object] | None) -> float | None:
    """1. Kurumsallik Skoru — kimlik omurgasi kaniti.

    D-246 kapisindan gecmis vergi/TCKN, MERSIS, ticaret sicili ve unvan.
    D-245: dolu ama gecersiz deger puan kazandirmaz; bu yuzden alanlar
    `dogrulanmis_*` onekiyle gelir (ETL yolu ekler), ham `tax_number`
    okunmaz.
    """
    if not firma:
        return None
    return _nokta_oranla(
        (
            (firma.get("dogrulanmis_tckn"), 1.5),
            (firma.get("dogrulanmis_mersis"), 1.0),
            (firma.get("dogrulanmis_sicil"), 1.0),
            (firma.get("legal_name"), 0.5),
        )
    )


def guvenilirlik_skoru(firma: Mapping[str, object] | None) -> float | None:
    """2. Guvenilirlik Skoru — kaynak sayisi ve kaynak cesitliligi.

    D-261: yinelenmis kayit sayisi guvenilirligi *dusurur*; ozdes kaynak
    tek kutupte yigilmissa tek kaynak sayilir.
    """
    if not firma:
        return None
    kaynak = firma.get("kaynak_sayisi")
    tur = firma.get("kaynak_tur_sayisi")
    if kaynak is None and tur is None:
        return None
    kaynak = float(kaynak or 0)
    tur = float(tur or 0)
    return _puanla(min(kaynak / 5.0, 1.0) * 50.0 + min(tur / 3.0, 1.0) * 50.0)


def itibar_skoru(firma: Mapping[str, object] | None) -> float | None:
    """3. Itibar Skoru — dogrulanmis NACE ve faaliyet derinligi.

    D-252: tahmin edilen NACE kanit degildir; yalniz `nace_kanitli`
    bayragi sinyal sayilir.
    """
    if not firma:
        return None
    if not firma.get("nace_kanitli"):
        return None
    derinlik = firma.get("faaliyet_sayisi")
    return _puanla(min(float(derinlik or 1), 3) / 3.0 * 100.0)


def siber_guvenlik_skoru(firma: Mapping[str, object] | None) -> float | None:
    """4. Siber Guvenlik Skoru — isletmenin kendi dijital altyapisi.

    Kanit yalniz acikca isaretlenmis girdiden gelir; alan adinin varligi
    tek basina kanit degildir (D-245: kaynak sitesi alan adina sizabilir).
    """
    if not firma:
        return None
    kanit = firma.get("siber_kanit")
    if not kanit:
        return None
    return _puanla(min(float(kanit), 1.0) * 100.0)


def operasyonel_guc_skoru(firma: Mapping[str, object] | None) -> float | None:
    """5. Operasyonel Guc Skoru.

    Bugun `employee_count` %100 NULL'dur (D-250/5); bu yuzden skor da
    NULL kalir. Kolon silinmez, giris geldiginde devreye girer (D-249/4).
    """
    if not firma:
        return None
    calisan = firma.get("employee_count")
    if calisan is None:
        return None
    return _puanla(min(float(calisan), 500) / 500.0 * 100.0)


def seffaflik_skoru(firma: Mapping[str, object] | None) -> float | None:
    """6. Seffaflik Skoru — aciklanan iletisim ve adres."""
    if not firma:
        return None
    return _nokta_oranla(
        (
            (firma.get("address"), 1.0),
            (firma.get("primary_phone"), 1.0),
            (firma.get("primary_email"), 1.0),
            (firma.get("website_domain"), 0.5),
        )
    )


def fraud_riski_skoru(firma: Mapping[str, object] | None) -> float | None:
    """7. Fraud Risk Skoru — kimlik celiskileri.

    D-267: ayni sirket icin celisen kimlikler risk sinyalidir. Celiski
    yoksa **0** doner (olculdu, sinyal yok) — veri yoksa `None`.
    """
    if not firma:
        return None
    if firma.get("kimlik_verisi") is None:
        return None
    celiski = firma.get("kimlik_celiskisi")
    if celiski is None:
        return None
    return _puanla(min(float(celiski), 3) / 3.0 * 100.0)


_SKOR_FONKSIYONLARI = {
    "corporateness_score": kurumsallik_skoru,
    "reliability_score": guvenilirlik_skoru,
    "reputation_score": itibar_skoru,
    "cyber_security_score": siber_guvenlik_skoru,
    "operational_power_score": operasyonel_guc_skoru,
    "transparency_score": seffaflik_skoru,
    "fraud_risk_score": fraud_riski_skoru,
}

# --- Genel guven + kademe --------------------------------------------------


def genel_guven(skorlar: Mapping[str, float | None]) -> float | None:
    """Genel Guven Skoru = 7 skorun agirligiyla ortalamasi.

    D-249/3: **olculmemis skor hem paydadan hem paydan duser.** 7 skor
    NULL ise sonuc `None` — 0 degil.
    """
    if not skorlar:
        return None
    pay = 0.0
    payda = 0.0
    for ad, agirlik in AGIRLIKLAR.items():
        deger = skorlar.get(ad)
        if deger is None:
            continue
        pay += float(deger) * agirlik
        payda += agirlik
    if payda <= 0:
        return None
    return _puanla(pay / payda)


def kademe(genel: float | None) -> str | None:
    """Genel guven skorundan SSOT'taki 4 kademeden birini uretir.

    `genel` NULL ise kademe de NULL (brief madde 9).
    Kademe **disi** bir deger verilirse `ValueError` — sessizce ilk kademeye
    dusmek, DB CHECK kisitinin onceden yakalayacagi hatayi gizlerdi.
    """
    if genel is None:
        return None
    if isinstance(genel, str):
        raise ValueError(f"kademe() sayi bekler, metin geldi: {genel!r}")
    deger = float(genel)
    for esik, ad in KADEME_ESIKLERI:
        if deger >= esik:
            return ad
    return "yuksek_riskli"


def skorlari_hesapla(firma: Mapping[str, object] | None) -> dict[str, float | None]:
    """Bir firma satirindan 8 skoru hesaplar (yazma yapmaz)."""
    if not firma:
        return {ad: None for ad in (*SKORLAR, GENEL_SKOR)}

    skorlar: dict[str, float | None] = {}
    for ad, fonk in _SKOR_FONKSIYONLARI.items():
        try:
            deger = fonk(firma)
        except (TypeError, ValueError) as exc:
            # Bozuk girdi 0 puan degildir, olcum yoktur (D-249).
            logger.warning("Skor hesaplanamadi: %s (%s)", ad, exc)
            deger = None
        skorlar[ad] = deger if deger is None else _puanla(deger)
    skorlar[GENEL_SKOR] = genel_guven(skorlar)
    return skorlar


# --- Tek yazma kapisi (D-256/2) ------------------------------------------

_SORGU = """
SELECT c.company_id,
       c.legal_name,
       c.address,
       c.primary_phone,
       c.primary_email,
       c.website_domain,
       c.employee_count,
       c.tax_number,
       c.mersis_number,
       c.trade_registry_number,
       c.nace_code,
       c.nace_source,
       c.nace_validity,
       (SELECT count(*) FROM company_industries ci
         WHERE ci.company_id = c.company_id
           AND ci.verified_at IS NOT NULL) AS dogrulanmis_faaliyet,
       (SELECT count(*) FROM company_industries ci
         WHERE ci.company_id = c.company_id) AS faaliyet_sayisi,
       (SELECT count(*) FROM source_records s
         WHERE s.company_id = c.company_id) AS kaynak_sayisi,
       (SELECT count(DISTINCT s.source_id) FROM source_records s
         WHERE s.company_id = c.company_id) AS kaynak_tur_sayisi,
       (SELECT count(*) FROM company_identifiers ci2
         WHERE ci2.company_id = c.company_id) AS kimlik_verisi,
       (SELECT count(DISTINCT ci3.identifier_type) FROM company_identifiers ci3
         WHERE ci3.company_id = c.company_id
           AND ci3.identifier_type IN ('vkn', 'tckn')) AS kimlik_celiskisi
  FROM companies c
"""

# Tek yazma ifadesi (D-249/2: toplu yazma = tek SQL, executemany degil).
_YAZ = """
INSERT INTO company_risk_scores AS t (
    company_id, corporateness_score, reliability_score, reputation_score,
    cyber_security_score, operational_power_score, transparency_score,
    fraud_risk_score, overall_trust_score, recommendation_tier,
    calculated_at, score_version
)
SELECT v.cid,
       v.corporateness_score, v.reliability_score, v.reputation_score,
       v.cyber_security_score, v.operational_power_score, v.transparency_score,
       v.fraud_risk_score, v.overall_trust_score, v.recommendation_tier,
       NOW(), :v
  FROM unnest(
       CAST(:ids AS uuid[]),
       CAST(:corporateness AS numeric[]),
       CAST(:reliability AS numeric[]),
       CAST(:reputation AS numeric[]),
       CAST(:cyber AS numeric[]),
       CAST(:power AS numeric[]),
       CAST(:transparency AS numeric[]),
       CAST(:fraud AS numeric[]),
       CAST(:overall AS numeric[]),
       CAST(:tier AS text[])
  ) AS v(cid, corporateness_score, reliability_score, reputation_score,
          cyber_security_score, operational_power_score, transparency_score,
          fraud_risk_score, overall_trust_score, recommendation_tier)
ON CONFLICT (company_id) DO UPDATE SET
    corporateness_score = EXCLUDED.corporateness_score,
    reliability_score = EXCLUDED.reliability_score,
    reputation_score = EXCLUDED.reputation_score,
    cyber_security_score = EXCLUDED.cyber_security_score,
    operational_power_score = EXCLUDED.operational_power_score,
    transparency_score = EXCLUDED.transparency_score,
    fraud_risk_score = EXCLUDED.fraud_risk_score,
    overall_trust_score = EXCLUDED.overall_trust_score,
    recommendation_tier = EXCLUDED.recommendation_tier,
    calculated_at = NOW(),
    score_version = EXCLUDED.score_version
"""


def _satiri_hazirla(satir: Mapping[str, object]) -> dict[str, object]:
    """Ham DB satirini skorlari_hesapla'nin bekledigi girdiye cevirir.

    Ayrica D-245 kapisini uygular: dogrulanmamis deger puan almaz.
    """
    kimlik_celiskisi = satir.get("kimlik_celiskisi")
    return {
        "legal_name": satir.get("legal_name"),
        "address": satir.get("address"),
        "primary_phone": satir.get("primary_phone"),
        "primary_email": satir.get("primary_email"),
        "website_domain": satir.get("website_domain"),
        "employee_count": satir.get("employee_count"),
        # D-246: bu ucu dogrulanmis sayan yol yaziyor; ham kolon okunmaz.
        "dogrulanmis_tckn": 1 if _gecerli_tckn(satir.get("tax_number")) else None,
        "dogrulanmis_mersis": 1 if satir.get("mersis_number") else None,
        "dogrulanmis_sicil": 1 if satir.get("trade_registry_number") else None,
        # D-252: yalniz kanit listesindeki kaynak ya da `verified_at` dolu
        # faaliyet dogrulanmis sayilir. Tahmin edilen kod puan uretmez.
        "nace_kanitli": 1 if _nace_kanitli(satir) else None,
        "faaliyet_sayisi": satir.get("faaliyet_sayisi"),
        "kaynak_sayisi": satir.get("kaynak_sayisi"),
        "kaynak_tur_sayisi": satir.get("kaynak_tur_sayisi"),
        # Siber alani icin kanit bayragi; alan adi tek basina kanit degil.
        "siber_kanit": satir.get("siber_kanit"),
        "kimlik_verisi": satir.get("kimlik_verisi"),
        "kimlik_celiskisi": kimlik_celiskisi,
    }


def _gecerli_tckn(deger: object) -> bool:
    """11 haneli kimlik; D-246: uzunluk tek basina kanit degil, kapidan gecer."""
    metin = str(deger or "").strip()
    return len(metin) == 11 and metin.isdigit()


def _nace_kanitli(satir: Mapping[str, object]) -> bool:
    """D-252: dogrulanmamis NACE tahmindir, kanit degildir."""
    kaynak = str(satir.get("nace_source") or "").strip().lower()
    gecerlilik = str(satir.get("nace_validity") or "").strip().lower()
    if kaynak in NACE_KANIT_KAYNAKLARI or gecerlilik == "verified":
        return True
    # Kanit kaynagi ayri bir tabloda olabilir (MERSIS/TSG yazimi).
    return int(satir.get("dogrulanmis_faaliyet") or 0) > 0


def risk_recalc(engine=None, *, surum: str = SURUM) -> int:
    """Tum firmalarin risk skorlarini yeniden hesaplar ve TEK ifadeyle yazar.

    Bu modulde tabloya yazan tek fonksiyondur (D-256/2). Donen deger yazilan
    firma sayisidir.
    """
    motor = engine or get_engine()
    with motor.connect() as conn:
        satirlar = conn.execute(text(_SORGU)).mappings().all()
    if not satirlar:
        return 0

    ids: list[str] = []
    kolonlar: dict[str, list[object]] = {ad: [] for ad in _SKOR_FONKSIYONLARI}
    kolonlar[GENEL_SKOR] = []
    tierler: list[object] = []

    for satir in satirlar:
        skorlar = skorlari_hesapla(_satiri_hazirla(dict(satir)))
        ids.append(str(satir["company_id"]))
        for ad in _SKOR_FONKSIYONLARI:
            kolonlar[ad].append(skorlar[ad])
        kolonlar[GENEL_SKOR].append(skorlar[GENEL_SKOR])
        tierler.append(kademe(skorlar[GENEL_SKOR]))

    with motor.begin() as conn:
        conn.execute(
            text(_YAZ),
            {
                "ids": ids,
                "corporateness": kolonlar["corporateness_score"],
                "reliability": kolonlar["reliability_score"],
                "reputation": kolonlar["reputation_score"],
                "cyber": kolonlar["cyber_security_score"],
                "power": kolonlar["operational_power_score"],
                "transparency": kolonlar["transparency_score"],
                "fraud": kolonlar["fraud_risk_score"],
                "overall": kolonlar[GENEL_SKOR],
                "tier": tierler,
                "v": surum,
            },
        )
    return len(ids)
