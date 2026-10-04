# -*- coding: utf-8 -*-
"""ALTYAPI-MIMIR-HABER-KUSU-01 — F2 haber kuşu kaynak haritası denetimi.

Üç kural, ağ yok:
  1. Haritadaki her URL `getir_izinli_mi` → None (izinsiz kalırsa GETIR çalışmaz).
  2. Her URL `https://` (GETIR http(s) kabul eder ama kanıt https).
  3. Harita anahtarları paket kaynak kodlarıyla eşleşir (`KAYNAK_PAKET_ADI`).

Kanıt: `docs/HABER_KUSU_KAYNAK_OLCUMU.md` — her adresin HTTP/süre/karakter satırı.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.odin_ai.arac_dongusu import (  # noqa: E402
    KAYNAK_HARITASI,
    KAYNAK_PAKET_ADI,
    getir_izinli_mi,
)
from company_master.paketler import PAKET_KAYNAKLARI  # noqa: E402

OLCUM_DOK = ROOT / "docs" / "HABER_KUSU_KAYNAK_OLCUMU.md"

PAKET_KODLARI: set[str] = set()
for _kodlar in PAKET_KAYNAKLARI.values():
    PAKET_KODLARI.update(_kodlar)


def test_harita_en_alti_adres_ve_her_adres_iznli():
    assert len(KAYNAK_HARITASI) >= 6, f"harita cok kucuk: {len(KAYNAK_HARITASI)}"
    reddedilen = {etiket: getir_izinli_mi(url, None)
                  for etiket, url in KAYNAK_HARITASI.items()
                  if getir_izinli_mi(url, None) is not None}
    assert not reddedilen, f"GETIR reddi -> harita islevsiz: {reddedilen}"


def test_her_adres_https():
    http_olan = {e: u for e, u in KAYNAK_HARITASI.items() if not u.startswith("https://")}
    assert not http_olan, f"https olmayan adres: {http_olan}"


def test_harita_anahtarlari_paket_kodlariyla_kesisiyor():
    assert set(KAYNAK_HARITASI) == set(KAYNAK_PAKET_ADI), \
        "kopru anahtarlari harita ile ayni degil (D-211 ikiz riski)"
    bilinmeyen = {e: k for e, k in KAYNAK_PAKET_ADI.items() if k not in PAKET_KODLARI}
    assert not bilinmeyen, f"PAKET_KAYNAKLARI'nda olmayan kod uydurulmus: {bilinmeyen}"
    kesisan = set(KAYNAK_PAKET_ADI.values()) & PAKET_KODLARI
    assert kesisan, "harita ile paket kodlari kesismiyor"


def test_olcum_dokumani_her_adresi_kanitliyor():
    metin = OLCUM_DOK.read_text(encoding="utf-8")
    eksik = [url for url in KAYNAK_HARITASI.values() if url not in metin]
    assert not eksik, f"olcum dokumaninda 200 kaniti yok: {eksik}"
    # her adresin yaninda HTTP 200 satiri olmali
    for url in KAYNAK_HARITASI.values():
        satir = next((s for s in metin.splitlines() if url in s), "")
        assert "| 200 |" in satir, f"200 kaniti yok: {url}"
