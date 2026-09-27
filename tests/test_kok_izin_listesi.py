# -*- coding: utf-8 -*-
"""D-221 mandali: kok dizin izin listesi + ikiz govde yasagi.

D-221 yazili bir kuraldi ama mandali yoktu; kural test edilmezse erir.
Olcum (2026-09-27): kokte 143 dosya = 9 ikiz + 108 cop + 26 essiz.

Bu test kokun ICERIGINI temizlemez (o ayri ve geri alinabilir bir is);
kokun TANIMINI dondurur: yeni bir govde/pano dogarsa kirmizi yanar.
"""
from __future__ import annotations

from pathlib import Path

import pytest

VAULT = Path(__file__).resolve().parents[1]
KOK = VAULT.parent

#: D-221 Kural 2 — kokte durabilecek dizinler.
IZINLI_DIZINLER = {
    "Huginn Data Insights",  # vault: asil govde
    "yedekler",  # D-221: .bundle yedekleri
    "src",
    "workflows",
    ".git",
    ".agents",
    ".github",
    ".vscode",
    ".obsidian",
    ".roo",
    ".kilo",
    ".continue",
    ".storybook",
    ".kombai",
    ".n8nac",
}

#: D-221 Kural 3 — yeniden dogmasi yasak paralel govdeler.
YASAK_GOVDELER = {"AI proje v1", "data_worktree"}

#: D-172/D-177 CELISKISI (2026-09-27 olcumu):
#:   D-172 "worktree klasoru/ = yazma otorite, SSOT" der.
#:   D-177 "Huginn Data Insights/ = graph canonical" der.
#: Klasorun GERCEK icerigi: 5 dosya -> 3 bos JSON (2 B) + 2 tek seferlik
#: dump betigi. Yani SSOT degil, kalinti.
#: Silmek D-172'yi iptal etmek olur (KAHIN karari bekliyor). O karara kadar
#: mandal yalnizca BUYUMEYI engeller: kalinti kalinti kalir, govde olamaz.
KALINTI_UST_SINIR = 5


def _kok_dizinleri() -> set[str]:
    return {p.name for p in KOK.iterdir() if p.is_dir()}


def test_ikiz_govde_yeniden_dogmadi() -> None:
    """Kural 3: paralel govde = 'hangi nusha dogru?' sorusu = yanan zaman."""
    dogan = YASAK_GOVDELER & _kok_dizinleri()
    assert not dogan, (
        f"D-221 Kural 3 ihlali: ikiz govde yeniden dogdu -> {sorted(dogan)}. "
        "Paralel govde yasak; icerik vault'a tasinir."
    )


def test_kokte_izinsiz_dizin_yok() -> None:
    """Kural 2: listede olmayan dizin koke ait degil.

    Arsiv/gecici klasorler (_ARSIV_*, _trash) bilinmeyen degil, bilinen
    gecici alandir: sayilir ama ihlal saymaz.
    """
    izinsiz = {
        ad
        for ad in _kok_dizinleri()
        if ad not in IZINLI_DIZINLER
        and ad not in {"worktree klasoru"}  # D-172 celiskisi: asagida ayri mandal
        and not ad.startswith(("_", "."))
    }
    assert not izinsiz, (
        f"D-221 Kural 2 ihlali: kokte izinsiz dizin -> {sorted(izinsiz)}. "
        "Yeni kok girdisi KAHIN karari ister."
    )


def test_worktree_kalintisi_buyumedi() -> None:
    """D-172 celiskisi cozulene kadar: kalinti buyuyemez.

    Bu test klasoru MESRULASTIRMAZ; dondurur. 5 dosyayi gecerse biri
    orayi yeniden govde gibi kullaniyor demektir.
    """
    kalinti = KOK / "worktree klasoru"
    if not kalinti.is_dir():
        return  # D-172 cozuldu ve klasor kaldirildi: sorun yok
    sayi = len([p for p in kalinti.rglob("*") if p.is_file()])
    assert sayi <= KALINTI_UST_SINIR, (
        f"'worktree klasoru' buyudu: {sayi} dosya (ust sinir {KALINTI_UST_SINIR}). "
        "Kalinti govde olamaz — D-221 Kural 3."
    )


def test_kok_sabit() -> None:
    """Kural 1: kok tasinmaz — 10.368 sabit yol buna bagli."""
    assert (KOK / "Huginn Data Insights").is_dir(), (
        "Vault kokun altinda bulunamadi: kok tasinmis olabilir (D-221 Kural 1)."
    )


def test_d221_agents_mde_kayitli() -> None:
    """Kural metni SSOT'ta duruyor mu — test ile metin birbirini tutmali."""
    metin = (VAULT / "AGENTS.md").read_text(encoding="utf-8")
    assert "## D-221" in metin, "D-221 karari AGENTS.md'de yok."


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
