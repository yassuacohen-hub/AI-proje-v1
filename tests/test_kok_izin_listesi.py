# -*- coding: utf-8 -*-
"""D-221 mandali: kok dizin izin listesi + ikiz govde yasagi.

D-221 yazili bir kuraldi ama mandali yoktu; kural test edilmezse erir.
Olcum (2026-09-27): kokte 143 dosya = 9 ikiz + 108 cop + 26 essiz.

Bu test kokun ICERIGINI temizlemez (o ayri ve geri alinabilir bir is);
kokun TANIMINI dondurur: yeni bir govde/pano dogarsa kirmizi yanar.
"""
from __future__ import annotations

import subprocess
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


#: D-230 — GOMULU govde kopyasi yasagi.
#: Bosluk olcumu (2026-09-27): D-228 mandali `VAULT.iterdir()` kullaniyordu,
#: yani YALNIZ ust seviyeye bakiyordu. Bu yuzden
#: `data/orchestrator/backups/D-187_faz2_2026-09-22/worktree_klasoru_kopya/`
#: (vault'un TAM kopyasi; toplam 2904 dosya / 147.7 MB) 5 gun gorulmedi.
#: Ayni klasor ucuncu bir pano izi de tasiyordu (task_board.json.tmp, .bak).
#: Derinlige bakmayan bir mandal, derinde saklanani hic yakalamaz.
GOMULU_KOPYA_IMZALARI = ("worktree_klasoru_kopya", "vault_kopya", "_kopya_govde")

#: D-220 tavani: temizlik sonrasi 0. Bu sayi yalniz KUCULEBILIR.
GOMULU_KOPYA_TAVANI = 0


def test_gomulu_govde_kopyasi_yok() -> None:
    """D-230: govde kopyasi derinde de durmaz — yer degistirmek yok saymaz.

    `git ls-files` degil DISK taranir: bu kopya hic izlenmemisti (git'te 0),
    sorun versiyonlama degil govdenin kendisiydi. Yani mandal diske bakmali.
    """
    bulunan = sorted(
        p.relative_to(VAULT).as_posix()
        for p in VAULT.rglob("*")
        if p.is_dir() and any(imza in p.name for imza in GOMULU_KOPYA_IMZALARI)
    )
    assert len(bulunan) <= GOMULU_KOPYA_TAVANI, (
        f"D-230 ihlali: gomulu govde kopyasi -> {bulunan} "
        f"(tavan {GOMULU_KOPYA_TAVANI}). Essiz icerik arsive tasinir, kopya silinir."
    )


def test_d230_agents_mde_kayitli() -> None:
    """D-230 metni SSOT'ta duruyor mu."""
    metin = (VAULT / "AGENTS.md").read_text(encoding="utf-8")
    assert "(D-230 " in metin, "D-230 karari AGENTS.md'de yok."


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


#: D-229 — zaman damgali yedek/gecici dosya git'te IZLENMEZ.
#: Bosluk olcumu (2026-09-27): .gitignore'da `*.backup_*` ve `_tmp_*` desenleri
#: VARDI, ama bu 65 dosya desenler yazilmadan ONCE eklenmisti; git izlenen
#: dosyada .gitignore'a bakmaz. Yani kural yaziliydi, mandali yoktu.
#: Silmek veri kaybi degil: hepsi git gecmisinde duruyor (ilk giris ec770e4).
YEDEK_DESENLERI = (".backup_", ".yedek_", "_pytest_rerun", "_tmp_onem_test")

#: D-220 tavani: temizlik sonrasi 0. Bu sayi yalniz KUCULEBILIR.
IZLENEN_YEDEK_TAVANI = 0


def test_zaman_damgali_yedek_git_te_izlenmiyor() -> None:
    """D-229: yedegin yedegi git'te durmaz — gecmis zaten yedektir.

    `git ls-files` kullanir (diskteki dosyaya degil, IZLENEN dosyaya bakar);
    cunku sorun dosyanin varligi degil, versiyonlanmasiydi.
    """
    izlenen = subprocess.run(
        ["git", "ls-files"],
        cwd=VAULT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    artik = sorted(y for y in izlenen if any(d in y for d in YEDEK_DESENLERI))
    assert len(artik) <= IZLENEN_YEDEK_TAVANI, (
        f"D-229 ihlali: git'te {len(artik)} zaman damgali yedek izleniyor "
        f"(tavan {IZLENEN_YEDEK_TAVANI}) -> {artik[:5]}... "
        "`git rm --cached` ile cikar; icerik gecmiste duruyor."
    )


def test_d229_agents_mde_kayitli() -> None:
    """D-229 metni SSOT'ta duruyor mu."""
    metin = (VAULT / "AGENTS.md").read_text(encoding="utf-8")
    assert "(D-229 " in metin, "D-229 karari AGENTS.md'de yok."


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
