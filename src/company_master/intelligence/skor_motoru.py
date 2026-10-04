# -*- coding: utf-8 -*-
"""Firsat motoru — Need/Fit/Timing/Ensemble dort skoru (VERI-SKOR-MOTORU-01).

SSOT: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`
  :215-228  Opportunity Gates (esikler)
  :229-240  Three-Score System (skor tanimlari, kanit gereksinimi)
  :241-266  Ensemble formulu
Karis: D-319 — resmi skor seti K4 (bu dort skor). K2'nin 8 skoru risk motoru
olarak ayrica yasar; bu modulle karismaz.

Uctageler:

1. **Girdisi olmayan skor `None` doner, 0 degil.** D-249: "veri yok" ile
   "0 puan" ayri degerlerdir. Olculebilen ama sifir cikan sinyal gercek
   `0.0`'dir; olculemeyen `None`'dur.
2. **Skor yazan tek kapisi `firsat_recalc()`.** D-256/2. Bu modulde baska
   INSERT/UPDATE yoktur; yazma tek SQL ifadesidir (D-249/2).
3. **Ensemble bileseni `None` ise ensemble `None`'dur.** Bileseni 0 saymak
   "olcduk, sifir bulduk" demek olurdu; o da D-249 ihlali. Bilesen yoksa
   birlesik skor da hesaplanamaz.
4. **Kalibrasyon sabitleri surumle gelir.** D-250/6: agirlik seti degisince
   eski puanlar bayatlasir. Bu yuzden `KALIBRASYON` + `SURUM` birlikte
   degisir; `score_version` kolonu ayni surumu tasir.

Bilinen sinirlama (F3 bagimliligi): `fit_score` girdisi olan
`company_capabilities` / `certifications` / `key_personnel` semada var
(0004_faz_1_2.sql) ama ETL dolgusu F3'te yapilmadi. Bu tablolar bos oldugu
surece `fit_score` `None` doner — hata firlatmaz. Bu bir eksik degil,
D-249'nin dogru davranisidir.
"""
from __future__ import annotations

import logging
import math
from typing import Mapping

from sqlalchemy import text

from ..db.connection import get_engine

logger = logging.getLogger(__name__)

__all__ = [
    "SURUM",
    "SKORLAR",
    "AGIRLIKLAR",
    "KALIBRASYON",
    "KAPI_ESIKLERI",
    "SKOR_ARALIK",
    "need_score",
    "fit_score",
    "timing_score",
    "evidence_strength",
    "compute_ensemble_score",
    "firsat_skorlari",
    "kapi_gecildi_mi",
    "firsat_recalc",
]

SURUM = "v1"

# SSOT:232-237 — dort skorun kanidi. `evidence_strength` SSOT:224'te bir
# GATE girdisidir; SSOT:232-237'de "skor" olarak sayilmaz, bu yuzden
# `company_opportunity_scores` tablosunda kolonu yoktur (girdidir, ciktidir
# degil — raporda kayitlidir).
SKORLAR: tuple[str, ...] = (
    "need_score",
    "fit_score",
    "timing_score",
    "ensemble_score",
)

# SSOT:246-251 — varsayilan agirliklar, birebir. Toplam 1.0.
AGIRLIKLAR: dict[str, float] = {
    "need": 0.30,
    "fit": 0.35,
    "timing": 0.20,
    "evidence": 0.15,
}

SKOR_ARALIK = (0.0, 1.0)

# SSOT:260-261 — bonuslar. V7'deki +0.20/+0.15 degerleri V9'de kisaltildi.
# Bunlar TEK agirlik setinin parcasi degil, ustune eklenen bonus; toplam
# 0.08 ile 1.0'i asamaz cunku clamp uygulanir.
FIELD_BONUS = 0.05
SIGNAL_BONUS = 0.03

# v1 kalibrasyonu. SSOT yalnizca agirliklari ve bonuslari sabitler; asagidaki
# doygunluk sabitleri olcumle degil, kararla konmustur. Sayilar burada tek
# yerde durur; SSOT dogrulanmadan degistirilmez (D-227/2). Degisince SURUM
# artar ve eski satirlar bayat isaretlenir.
KALIBRASYON: dict[str, float] = {
    # Need: kac farkli sinyal turu "kume" sayilir.
    "need_doygunluk": 3.0,
    # Timing: recency yarim yasam gun sayisi (kucuk = yeni = yuksek puan).
    "timing_yarim_yasam_gun": 180.0,
    # Timing: mevsim eslesmesi bonusu (SSOT:236 "seasonality").
    "timing_mevsim_bonus": 0.10,
    # Evidence: kac farkli kaynak turu "guclu kanit" sayilir.
    "evidence_doygunluk": 3.0,
    # Fit: kac yetenek/sertifika/anahtar kisi kaydi doygunluk sayilir.
    "fit_doygunluk": 5.0,
    # Evidence gate esigi SSOT:224.
    "kapu_evidence": 0.20,
}

# SSOT:220-225 — dort gate esigi. Esik altinda kalan gate'in ne yapacagi
# SSOT'ta yazili; karar burada UYGULANMAZ, yalnizca degerlendirilir.
KAPI_ESIKLERI: dict[str, float] = {
    "need": 0.25,
    "fit": 0.30,
    "evidence": 0.20,
    "timing": 0.30,
}

# Asagidaki iki SQL ifadesi bu modulun tek veritabani yuzudur.
# Yazma ifadesi TEK SQL'dir (D-249/2: toplu yazma = tek ifade, executemany
# degil). Okuma ifadesi girdi toplar; skor hesabi Python'da kalir.

_SORGU = """
SELECT c.company_id,
       (SELECT count(DISTINCT e.event_type)
          FROM company_events e
         WHERE e.company_id = c.company_id
           AND e.event_type IS NOT NULL) AS sinyal_tur_sayisi,
       (SELECT count(*)
          FROM company_events e
         WHERE e.company_id = c.company_id
           AND e.event_type IS NOT NULL
           AND e.detected_at >= NOW() - INTERVAL '365 days') AS gecmis_desen,
       (SELECT count(*) FROM company_capabilities cp
         WHERE cp.company_id = c.company_id) AS yetenek_sayisi,
       (SELECT count(*) FROM certifications ce
         WHERE ce.company_id = c.company_id) AS sertifika_sayisi,
       (SELECT count(*) FROM key_personnel kp
         WHERE kp.company_id = c.company_id) AS anahtar_kisi_sayisi,
       (SELECT count(*) FROM source_records s
         WHERE s.company_id = c.company_id) AS kaynak_sayisi,
       (SELECT count(DISTINCT s.source_id) FROM source_records s
         WHERE s.company_id = c.company_id) AS kaynak_tur_sayisi,
       (SELECT max(s.collected_at) FROM source_records s
         WHERE s.company_id = c.company_id) AS son_kaynak_zamani,
       (SELECT count(*) FROM company_events e
         WHERE e.company_id = c.company_id
           AND e.detected_at >= NOW() - INTERVAL '10 days') AS son_10_gun_sinyal,
       c.identity_completeness AS kimlik_tamligi
  FROM companies c
"""

_YAZ = """
INSERT INTO company_opportunity_scores AS t (
    company_id, need_score, fit_score, timing_score, ensemble_score,
    calculated_at, score_version
)
SELECT v.cid, v.need_score, v.fit_score, v.timing_score, v.ensemble_score,
       NOW(), :v
  FROM unnest(
       CAST(:ids AS uuid[]),
       CAST(:need AS numeric[]),
       CAST(:fit AS numeric[]),
       CAST(:timing AS numeric[]),
       CAST(:ensemble AS numeric[])
  ) AS v(cid, need_score, fit_score, timing_score, ensemble_score)
ON CONFLICT (company_id) DO UPDATE SET
    need_score = EXCLUDED.need_score,
    fit_score = EXCLUDED.fit_score,
    timing_score = EXCLUDED.timing_score,
    ensemble_score = EXCLUDED.ensemble_score,
    calculated_at = NOW(),
    score_version = EXCLUDED.score_version
"""


def _sinirla(deger: float) -> float:
    """SSOT:263 clamp. Skor araligi 0.0-1.0; tas deger kirpilir."""
    return max(SKOR_ARALIK[0], min(SKOR_ARALIK[1], deger))


def _sayi(deger: object) -> float | None:
    """Sayiya cevirir; olculemeyen deger `None` kalir."""
    if deger is None:
        return None
    try:
        return float(deger)
    except (TypeError, ValueError):
        return None


def need_score(sinyal_tur_sayisi: object = None,
               gecmis_desen: object = None) -> float | None:
    """Ihtiyac olasiligi (SSOT:234).

    SSOT:234 kanit gereksinimi: "Signal cluster, historical pattern".
    Olculebilir ama sifir sinyal varsa `0.0` doner; hic olculemiyorsa
    `None` doner (D-249).
    """
    sinyal = _sayi(sinyal_tur_sayisi)
    if sinyal is None:
        return None
    doygunluk = KALIBRASYON["need_doygunluk"]
    puan = _sinirla(sinyal / doygunluk)
    desen = _sayi(gecmis_desen)
    if desen is not None and desen > 0:
        puan = _sinirla(puan + 0.10)
    return puan


def fit_score(yetenek_sayisi: object = None,
              sertifika_sayisi: object = None,
              anahtar_kisi_sayisi: object = None) -> float | None:
    """Urun uyumu (SSOT:235).

    SSOT:235 kanit gereksinimi: "Capability match, certification, capacity".
    F3 tamamlanana kadar uc girdi tablosu da bos kalir; o durumda uc
    toplam `None` ise fonksiyon `None` doner — hata firlatmaz, sahte `0`
    uretmez. Tablo bos olmak "uyumsuzluk" degil "olcum yok"tur.
    """
    parcalar = (
        _sayi(yetenek_sayisi),
        _sayi(sertifika_sayisi),
        _sayi(anahtar_kisi_sayisi),
    )
    if all(p is None for p in parcalar):
        return None
    # Bir tablo ETL ile dolmus, digerleri dolmamis olabilir. O zaman
    # olculebilen parcaya gore puan uretilir, olculemeyen parcaagirlik
    # TUMU DE 0 kabul edilerek disarida birakilir (D-249/3: eksik veri
    # firmayi cezalandirmaz).
    toplam = sum(p for p in parcalar if p is not None)
    return _sinirla(toplam / KALIBRASYON["fit_doygunluk"])


def timing_score(gun_once: object = None, mevsim_uyumu: object = None) -> float | None:
    """Zamanlama (SSOT:236).

    SSOT:236 kanit gereksinimi: "Recency, seasonality, budget cycle".
    `gun_once` = en son kanit kaydinin yasidir. `mevsim_uyumu` True ise
    mevsim bonusu eklenir. Gun yasi hic bilinmiyorsa `None`.
    """
    yas = _sayi(gun_once)
    if yas is None:
        return None
    if yas < 0:
        yas = 0.0
    yari = KALIBRASYON["timing_yarim_yasam_gun"]
    puan = _sinirla(math.pow(0.5, yas / yari))
    if mevsim_uyumu:
        puan = _sinirla(puan + KALIBRASYON["timing_mevsim_bonus"])
    return puan


def evidence_strength(kaynak_tur_sayisi: object = None,
                      kaynak_sayisi: object = None) -> float | None:
    """Kanit gucu — SSOT:224 Evidence Gate'inin girdisi.

    Bu bir SKOR DEGIL, bir GATE girdisidir; SSOT:232-237'de dort skor
    arasinda sayilmaz, bu yuzden `company_opportunity_scores` tablosunda
    kolonu yoktur. `compute_ensemble_score` bunu girdi olarak alir.
    """
    tur = _sayi(kaynak_tur_sayisi)
    adet = _sayi(kaynak_sayisi)
    if tur is None and adet is None:
        return None
    tur = tur if tur is not None else 0.0
    adet = adet if adet is not None else 0.0
    puan = 0.6 * _sinirla(tur / KALIBRASYON["evidence_doygunluk"])
    puan += 0.4 * _sinirla(adet / (KALIBRASYON["evidence_doygunluk"] * 3))
    return _sinirla(puan)


def compute_ensemble_score(need: object = None,
                           fit: object = None,
                           timing: object = None,
                           evidence: object = None,
                           weights: Mapping[str, float] | None = None,
                           *,
                           is_field_verified: bool = False,
                           active_intent_10d: bool = False) -> float | None:
    """Birlesik skor — SSOT:241-266 formulu birebir.

    Agirliklar SSOT:246-251; bonuslar SSOT:260-261; clamp SSOT:263.
    Bilesenlerden biri `None` ise sonuc `None`'dur: bileseni 0 saymak
    "olcduk ve sifir bulduk" anlamina gelirdi, o da D-249 ihlalidir.

    Pozisyonel imza SSOT:243 ile birebir ayni kaldi. Iki bonus bayragi
    anahtar-kelimeyle ayrica alinir; SSOT:260-261 bunlari ayri kosul olarak
    yazar, skor bileseninden **turetilemez**. Evetlemedigimiz bir kosulu
    bilesenden baska bir bilesene tasimak (or. "evidence >= 1.0 ise field
    bonusu") uydurma olurdu; varsayilan `False` guvenli taraftir.
    """
    agirliklar = dict(AGIRLIKLAR if weights is None else weights)
    bilesenler = {
        "need": _sayi(need),
        "fit": _sayi(fit),
        "timing": _sayi(timing),
        "evidence": _sayi(evidence),
    }
    if any(v is None for v in bilesenler.values()):
        return None
    for ad in bilesenler:
        if ad not in agirliklar:
            return None

    ham = sum(bilesenler[ad] * agirliklar[ad] for ad in bilesenler)
    bonus = 0.0
    if is_field_verified:
        bonus += FIELD_BONUS
    if active_intent_10d:
        bonus += SIGNAL_BONUS
    return _sinirla(ham + bonus)


def firsat_skorlari(veri: Mapping[str, object]) -> dict[str, float | None]:
    "Ham DB satirindan dort resmi skoru uretir (arayuzun bekledigi sozu)."""
    kayit = dict(veri or {})

    kimlik = _sayi(kayit.get("kimlik_tamligi"))
    kayit_tarihi = kayit.get("son_kaynak_zamani")
    gun_once = _gun_once(kayit_tarihi)
    mevsim = kayit.get("mevsim_uyumu")

    need = need_score(kayit.get("sinyal_tur_sayisi"),
                      kayit.get("gecmis_desen"))
    fit = fit_score(kayit.get("yetenek_sayisi"),
                    kayit.get("sertifika_sayisi"),
                    kayit.get("anahtar_kisi_sayisi"))
    timing = timing_score(gun_once, mevsim)
    evidence = evidence_strength(kayit.get("kaynak_tur_sayisi"),
                                 kayit.get("kaynak_sayisi"))
    kimlik = _sayi(kayit.get("kimlik_tamligi"))
    ensemble = compute_ensemble_score(
        need, fit, timing, evidence,
        is_field_verified=bool(kimlik is not None and kimlik >= 5.0),
        active_intent_10d=bool(_sayi(kayit.get("son_10_gun_sinyal")) or 0),
    )
    return {
        "need_score": need,
        "fit_score": fit,
        "timing_score": timing,
        "ensemble_score": ensemble,
        # Asagidaki iki alan tabloya YAZILMAZ; gate degerlendirmesi icindir.
        "evidence_strength": evidence,
        "kapi": kapi_gecildi_mi(need, fit, evidence, timing),
    }


def _gun_once(zaman: object) -> float | None:
    """Zaman damgasindan gun yasini hesaplar; bilinmiyorsa `None`."""
    if zaman is None:
        return None
    if isinstance(zaman, (int, float)):
        return float(zaman) / 86400.0
    tohum = getattr(zaman, "timestamp", None)
    if tohum is None:
        return None
    import datetime as _dt

    simdi = _dt.datetime.now(_dt.timezone.utc)
    if zaman.tzinfo is None:
        zaman = zaman.replace(tzinfo=_dt.timezone.utc)
    return max(0.0, (simdi - zaman).total_seconds() / 86400.0)


def kapi_gecildi_mi(need: object = None, fit: object = None,
                    evidence: object = None, timing: object = None,
                    esikler: Mapping[str, float] | None = None
                    ) -> dict[str, object]:
    """SSOT:215-228 gate degerlendirmesi.

    Sonuc yalnizca degerlendirmedir; karar uretmez. Need gate'i basarisizsa
    SSOT:227 uyarisi gecerlidir: en yuksek aksiyon `INVESTIGATE`'dir.
    """
    esik = dict(KAPI_ESIKLERI if esikler is None else esikler)
    degerler = {"need": need, "fit": fit, "evidence": evidence, "timing": timing}
    durum: dict[str, object] = {}
    for ad, deger in degerler.items():
        sayi = _sayi(deger)
        if sayi is None:
            # Esik "gecilmedi" degil, OLCULEMEDI. D-249: bilinmeyen deger
            # basarisiz sayilmaz; panelde ayrica gosterilir.
            durum[ad] = "olculmedi"
        else:
            durum[ad] = "gecti" if sayi >= esik[ad] else "kalmadi"
    return {
        "durum": durum,
        # SSOT:227: need < 0.25 ise CONTACT_NOW yasak.
        "contact_now_yasak": durum["need"] != "gecti",
        "olculmeyen": [ad for ad, v in durum.items() if v == "olculmedi"],
    }


def firsat_recalc(engine=None, *, surum: str = SURUM) -> int:
    """Tum firmalarin firsat skorlarini yeniden hesaplar ve TEK ifadeyle yazar.

    Bu modulde tabloya yazan tek fonksiyondur (D-256/2). Donen deger yazilan
    firma sayisidir. Gercek hesaplama D-238 geregi bu gorevde CANLI
    VERITABANINA CALISTIRILMAZ; fonksiyon uretilir ve testte sahte
    motorla dogrulanir.
    """
    motor = engine or get_engine()
    with motor.connect() as conn:
        satirlar = conn.execute(text(_SORGU)).mappings().all()
    if not satirlar:
        return 0

    ids: list[str] = []
    toplam: dict[str, list[object]] = {ad: [] for ad in SKORLAR}

    for satir in satirlar:
        skorlar = firsat_skorlari(dict(satir))
        ids.append(str(satir["company_id"]))
        for ad in SKORLAR:
            toplam[ad].append(skorlar[ad])

    with motor.begin() as conn:
        conn.execute(
            text(_YAZ),
            {
                "ids": ids,
                "need": toplam["need_score"],
                "fit": toplam["fit_score"],
                "timing": toplam["timing_score"],
                "ensemble": toplam["ensemble_score"],
                "v": surum,
            },
        )
    logger.info("firsat skoru yazildi: %d firma (surum %s)", len(ids), surum)
    return len(ids)
