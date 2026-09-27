"""D-241: dis kok (git deposu koku) temiz kalir — mandal.

D-221 kok politikasini yaziyordu ama mandali yoktu; .gitignore deseni de
dosyalar zaten takipli oldugu icin islemiyordu. Sonuc: kokte 131 dosya birikti.
Bu test kapiyi kurar: kokte izin listesi disinda dosya olusursa kirmizi yanar.
"""

from __future__ import annotations

import pathlib

import pytest

# tests/ -> vault koku -> dis kok (git deposu koku)
DIS_KOK = pathlib.Path(__file__).resolve().parents[2]

# Kokte kalmasina izin verilen dosyalar. Buyumez — yeni ad eklemek
# D-241 ihlalidir, dosya alt klasore ait.
IZINLI_DOSYA = frozenset(
    {
        ".gitignore",
        "AGENTS.md",
        "tsconfig.json",
        "n8nac-config.json",
    }
)

# Platform zorunlulugu olan nokta klasorleri + mesru ust klasorler.
IZINLI_KLASOR_ONEK = ("_ARSIV_", ".")
IZINLI_KLASOR = frozenset({"Huginn Data Insights", "yedekler", "src", "workflows"})


def _kok_dosyalari() -> list[str]:
    return sorted(p.name for p in DIS_KOK.iterdir() if p.is_file())


@pytest.mark.skipif(
    not (DIS_KOK / ".gitignore").exists(),
    reason="dis kok bulunamadi (farkli klasor yapisi)",
)
def test_kokte_izinsiz_dosya_yok() -> None:
    """Kokte izin listesi disinda dosya birikmez (D-241)."""
    fazla = sorted(set(_kok_dosyalari()) - IZINLI_DOSYA)
    assert not fazla, (
        f"Dis kokte {len(fazla)} izinsiz dosya: {fazla[:10]}\n"
        "Cozum: tek kullanimlik betik/cikti alt klasore tasinir "
        "(_ARSIV_* veya ilgili repo). Izin listesi buyutulmez (D-241)."
    )


@pytest.mark.skipif(
    not (DIS_KOK / ".gitignore").exists(),
    reason="dis kok bulunamadi (farkli klasor yapisi)",
)
def test_kokte_izinsiz_klasor_yok() -> None:
    """Kokte tanimsiz ust klasor olusmaz (D-241)."""
    fazla = sorted(
        p.name
        for p in DIS_KOK.iterdir()
        if p.is_dir()
        and p.name not in IZINLI_KLASOR
        and not p.name.startswith(IZINLI_KLASOR_ONEK)
    )
    assert not fazla, f"Dis kokte tanimsiz klasor: {fazla}"


def test_izin_listesi_kucuk_kalir() -> None:
    """Tavan: izin listesi 4 adi asmaz, yalniz kuculur (D-220 deseni)."""
    assert len(IZINLI_DOSYA) <= 4, (
        f"Izin listesi {len(IZINLI_DOSYA)} ada cikmis. Tavan 4 ve yalniz kuculur; "
        "yeni dosyaya yer acmak icin buyutmek D-241 ihlalidir."
    )
