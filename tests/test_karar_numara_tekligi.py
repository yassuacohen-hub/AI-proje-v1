# -*- coding: utf-8 -*-
"""D-227 mandalı: karar numarası (D-NNN) yalnız AGENTS.md'den verilir.

İki katman:
  1. TEKLİK — AGENTS.md içindeki kanonik karar başlıkları benzersiz numara taşır.
  2. SAHİPLENME — AGENTS.md dışındaki hiçbir belge karar numarasını
     dosya adında veya H1 başlığında *sahiplenmez*; yalnız gövdede referans verir.

Geriye dönük düzeltme değer üretmez (bkz. D-220). Mevcut ihlal sayısı tavan
olarak sabitlenir; test yalnız **artışı** yakalar. Tavan düşürülebilir, asla
yükseltilemez.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
AGENTS = KOK / "AGENTS.md"

# Kanonik karar başlığı: "## Başlık (D-NNN — KAHİN kararı TARİH)"
# "D-NNN Ek — ..." biçimi bilerek DIŞARIDA: uzantı başlığı numarayı sahiplenmez.
KANONIK = re.compile(r"^##+ .*?\(D-(\d{1,3}) [\u2014-] KAH", re.M)

# Dosya adında karar numarası sahiplenmesi: D-216_..., ..._D223.md
AD_SAHIPLENME = re.compile(r"D-?\d{2,3}")

# H1'de sahiplenme: "# D-223: ..." / "# D-185 — ..."
H1_SAHIPLENME = re.compile(r"^# D-?\d{2,3}\b")

# Taranan alanlar. backups/ tarihsel yedektir, kapsam dışı.
TARANAN = ("plans/*.md", "docs/*.md", "data/orchestrator/*.md", "hubs/*.md", "*.md")

# D-227 anındaki ÖLÇÜLMÜŞ ihlal tavanı (tahmin değil). YALNIZ KÜÇÜLÜR.
TAVAN_AD = 35
TAVAN_H1 = 24


def _belgeler() -> list[Path]:
    out: list[Path] = []
    for kalip in TARANAN:
        out += [p for p in KOK.glob(kalip) if p.name != "AGENTS.md"]
    return sorted(set(out))


def test_agents_md_var() -> None:
    assert AGENTS.is_file(), f"AGENTS.md bulunamadi: {AGENTS}"


def test_kanonik_karar_numaralari_tekil() -> None:
    """AGENTS.md içinde aynı D-NNN iki kez kanonik başlık olamaz."""
    numaralar = KANONIK.findall(AGENTS.read_text(encoding="utf-8"))
    assert numaralar, "AGENTS.md'de kanonik karar basligi bulunamadi - regex bozulmus olabilir"
    tekrar = sorted({n for n in numaralar if numaralar.count(n) > 1})
    assert not tekrar, (
        f"AYNI KARAR NUMARASI BIRDEN COK KANONIK BASLIKTA: {tekrar}. "
        "Karar numarasi tekildir; birini yeniden numaralandir veya alt baslik yap."
    )


def test_karar_numarasi_dosya_adinda_sahiplenilmez() -> None:
    """AGENTS.md dışı belge adları karar numarası taşımamalı (tavan sabit)."""
    ihlal = [p.relative_to(KOK).as_posix() for p in _belgeler() if AD_SAHIPLENME.search(p.name)]
    assert len(ihlal) <= TAVAN_AD, (
        f"DOSYA ADINDA KARAR NUMARASI ARTTI: {len(ihlal)} > tavan {TAVAN_AD}.\n"
        f"Yeni ihlaller icin listeye bak: {ihlal}"
    )


def test_karar_numarasi_h1_basliginda_sahiplenilmez() -> None:
    """AGENTS.md dışı belgeler H1'de karar numarası sahiplenmemeli (tavan sabit)."""
    ihlal = []
    for p in _belgeler():
        ilk = p.read_text(encoding="utf-8", errors="replace").lstrip().split("\n", 1)[0]
        if H1_SAHIPLENME.match(ilk):
            ihlal.append(p.relative_to(KOK).as_posix())
    assert len(ihlal) <= TAVAN_H1, (
        f"H1'DE KARAR NUMARASI ARTTI: {len(ihlal)} > tavan {TAVAN_H1}.\n"
        f"Rapor karar numarasi sahiplenmez, govdede referans verir. Liste: {ihlal}"
    )


@pytest.mark.parametrize(
    "ad",
    ["BOT_HANDLER_DATA_FIX.md", "BOT_HANDLER_DATA_FIX_KAPANIS.md"],
)
def test_cakisan_raporlar_referansa_cevrildi(ad: str) -> None:
    """D-227 tetikleyicisi olan iki rapor geri dönmemeli."""
    p = KOK / "data" / "orchestrator" / ad
    assert p.is_file(), f"{ad} bulunamadi - yeniden adlandirma geri alinmis olabilir"
    metin = p.read_text(encoding="utf-8", errors="replace")
    assert "Karar referansı: D-" in metin, f"{ad} icinde karar referans notu yok"
    assert not H1_SAHIPLENME.match(metin.lstrip().split("\n", 1)[0]), (
        f"{ad} yine H1'de karar numarasi sahipleniyor"
    )
