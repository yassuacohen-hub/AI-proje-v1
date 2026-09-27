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
#: 'worktree klasoru' D-223 (2026-09-27) ile arsive tasindi; geri dogarsa ihlal.
YASAK_GOVDELER = {"AI proje v1", "data_worktree", "worktree klasoru"}

#: D-223: yedekte kalip canli agacta kaybolan urun sahibi dokumanlari.
#: Olcum (2026-09-27): OPERASYON_KILAVUZU.md 668 satir SADECE backups/ altindaydi.
#: Bir dokuman yalnizca yedekte kalirsa pratikte yok demektir.
CANLI_KALMASI_GEREKEN_DOKUMANLAR = (
    "docs/OPERASYON_KILAVUZU.md",
    "docs/GOREV_PANOSU_KULLANIM_KILAVUZU.md",
)


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
        if ad not in IZINLI_DIZINLER and not ad.startswith(("_", "."))
    }
    assert not izinsiz, (
        f"D-221 Kural 2 ihlali: kokte izinsiz dizin -> {sorted(izinsiz)}. "
        "Yeni kok girdisi KAHIN karari ister."
    )


@pytest.mark.parametrize("yol", CANLI_KALMASI_GEREKEN_DOKUMANLAR)
def test_kilavuz_canli_agacta(yol: str) -> None:
    """D-223: urun sahibi dokumani yedege kacmaz.

    OPERASYON_KILAVUZU.md bir kez bunu yasadi: D-187 yedege aldi, canli
    nusha geri konmadi, 5 gun kimse fark etmedi. Bu test o sessiz kaybi
    sesli hale getirir.
    """
    dosya = VAULT / yol
    assert dosya.is_file(), (
        f"D-223 ihlali: '{yol}' canli agacta yok. "
        "Yedekte durmasi yeterli degil — urun sahibi yedege bakmaz."
    )


#: D-228 — vault ICINDE paralel veri govdesi yasagi.
#: Bosluk olcumu (2026-09-27): YASAK_GOVDELER yalniz KOK'e bakiyordu; bu yuzden
#: 'Huginn Data Insights/data_worktree/' (504 izlenen dosya, 50.3 MB) 6 gun
#: yasadi ve ucuncu bir gorev panosu izi tasidi (orchestrator/gorev_panosu.md).
VAULT_ICI_YASAK_DIZINLER = {"data_worktree", "data_eski", "data_backup"}


def test_vault_icinde_paralel_veri_govdesi_yok() -> None:
    """D-228: 'data' yaninda ikinci veri govdesi = ikinci SSOT = yanan zaman.

    Kokteki mandal (test_ikiz_govde_yeniden_dogmadi) vault ICINI gormuyordu.
    Bu test o bosluğu kapatir: ikiz veri dizini geri dogarsa kirmizi yanar.
    """
    dogan = {p.name for p in VAULT.iterdir() if p.is_dir()} & VAULT_ICI_YASAK_DIZINLER
    assert not dogan, (
        f"D-228 ihlali: vault icinde paralel veri govdesi -> {sorted(dogan)}. "
        "Essiz icerik data/ veya arsive tasinir; ikiz dizin durmaz."
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


def test_d223_agents_mde_kayitli_ve_d172_emekli() -> None:
    """D-223 yazildi ve D-172 emekli isaretlendi mi.

    D-187 dersi: tasima yapilip karar yazilmazsa eski kural 'yururlukte'
    gorunur. Bu test o bosluğu kapatir.
    """
    metin = (VAULT / "AGENTS.md").read_text(encoding="utf-8")
    assert "Tek Otorite: Vault (D-223" in metin, "D-223 karari AGENTS.md'de yok."
    assert "EMEKLİ — D-223" in metin, (
        "D-172 emekli isareti yok: eski kural hala yururlukte gorunuyor."
    )


def test_d228_agents_mde_kayitli() -> None:
    """D-228 metni SSOT'ta duruyor mu — test ile karar birbirini tutmali."""
    metin = (VAULT / "AGENTS.md").read_text(encoding="utf-8")
    assert "(D-228 " in metin, "D-228 karari AGENTS.md'de yok."


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
