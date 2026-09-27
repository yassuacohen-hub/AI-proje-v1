# -*- coding: utf-8 -*-
"""D-235 mandali: kaziyicilar kendi sayfalama dongusunu YAZAMAZ.

Kural dokumani tek basina uyulmaz — kanit: ucu de ayni `while True` hatasini
bagimsizca yapti (Ivedik 3375 satir / 14 tekil firma). Bu test kurali makineye
baglar: yeni kaziyici elle dongu yazarsa test kirmizi olur.

Eski borc IZIN_LISTESI ile taninir; gorev kapaninca satir buradan SILINIR.
Liste buyumez — yalniz kuculur.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

KAZIYICI_DIZINI = Path(__file__).resolve().parents[1] / "src/company_master/etl/scrapers"

# Bilinen borc: sablona tasinacak dosyalar (VERI-KAZIYICI-DONGU-01).
# Gorev kapaninca ilgili satir SILINIR, yenisi EKLENMEZ.
IZIN_LISTESI = {
    "ostim_scraper.py": "VERI-KAZIYICI-DONGU-01 — sektor bazli dongu, sablona tasinacak",
    "ostim_scraper_full.py": "VERI-KAZIYICI-DONGU-01 — sablona tasinacak",
}

ELLE_DONGU = re.compile(r"^\s*while\s+True\s*:", re.MULTILINE)


def _kaziyici_dosyalari() -> list[Path]:
    return sorted(
        p for p in KAZIYICI_DIZINI.glob("*_scraper*.py") if not p.name.startswith("base_")
    )


def test_kaziyici_dizini_bulundu():
    dosyalar = _kaziyici_dosyalari()
    assert dosyalar, f"kaziyici bulunamadi: {KAZIYICI_DIZINI}"


@pytest.mark.parametrize("yol", _kaziyici_dosyalari(), ids=lambda p: p.name)
def test_elle_sayfalama_dongusu_yok(yol: Path):
    """`while True:` yalniz izin listesindeki eski dosyalarda olabilir."""
    metin = yol.read_text(encoding="utf-8")
    if not ELLE_DONGU.search(metin):
        return
    assert yol.name in IZIN_LISTESI, (
        f"{yol.name} elle `while True` sayfalama dongusu iceriyor. "
        "D-235: BaseOsfbScraper.sayfa_dongusu() kullanilmali "
        "(docs/VERI_KAYNAK_KURALLARI.md K-1)."
    )


def test_izin_listesi_gecerli():
    """Izin listesindeki dosya hala varsa ve borcu bittiyse liste guncellenmeli."""
    adlar = {p.name for p in _kaziyici_dosyalari()}
    for ad in IZIN_LISTESI:
        assert ad in adlar, f"izin listesinde olmayan dosya: {ad} — satir silinmeli"
        metin = (KAZIYICI_DIZINI / ad).read_text(encoding="utf-8")
        assert ELLE_DONGU.search(metin), (
            f"{ad} artik elle dongu icermiyor — IZIN_LISTESI'nden SILINMELI"
        )


def test_cikti_ekleme_kipinde_acilmiyor():
    """K-3: jsonl 'a' kipiyle acilirsa kopyalar ust uste yigilir."""
    suclu = []
    for yol in _kaziyici_dosyalari():
        metin = yol.read_text(encoding="utf-8")
        if re.search(r'"a"\s+if\s+.*OUTPUT_PATH', metin):
            suclu.append(yol.name)
    assert not suclu, (
        f"ekleme kipi (a) kullanan kaziyici: {suclu} — "
        "D-235 / K-3: tam turda cikti bastan yazilir"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
