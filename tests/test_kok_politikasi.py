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


# ---------------------------------------------------------------------------
# Vault kokunde tek kullanimlik betik birikmesi (D-221)
# ---------------------------------------------------------------------------

# tests/ -> vault koku
VAULT_KOK = pathlib.Path(__file__).resolve().parents[1]

#: Koke dusecek tek kullanimlik desenler (D-221). Ayni desenler vault
#: .gitignore'inda da yasakli; burada mandal onlari diske dusuruyor.
TEK_KULLANIMLIK_ONEK = (
    "check_", "fix_", "run_", "verify_", "add_", "clean_", "debug_", "count_",
)

#: Koke kalan _onekli dosyalar bunlar disinda (D-219 canli sablon).
IZINLI_ONEKLI = frozenset({"_ajan_context_sablon.md"})


def _vault_kok_tek_kullanimlik() -> list[str]:
    """Vault kokunde D-221'e aykiri tek kullanimlik dosyalar."""
    supheli = {
        p.name
        for p in VAULT_KOK.iterdir()
        if p.is_file()
        and p.name not in IZINLI_ONEKLI
        and (p.name.startswith("_") or p.name.startswith(TEK_KULLANIMLIK_ONEK))
    }
    return sorted(supheli)


def test_vault_kokte_tek_kullanimlik_yok() -> None:
    """Vault kokunde tek kullanimlik betik/cikti birikmez (D-221).

    Ajanlar `check_*.py` / `run_*.py` gorup YANLIS betigi calistirir:
    ayni isin 5-7 kopyasi koke birikmisti. Cozum: `_ARSIV_tek_kullanimlik/`
    altina tasinir; izin listesi BUYUTULMEZ.
    """
    fazla = _vault_kok_tek_kullanimlik()
    assert not fazla, (
        f"Vault kokte {len(fazla)} tek kullanimlik dosya: {fazla[:10]}\n"
        "Cozum: `_ARSIV_tek_kullanimlik/` altina tasinir. D-221 bu olcumun "
        "gereklidir: kokte biriken betik ajanin yanlis calistirmasina yol acar."
    )


def test_ajan_sablonu_kokte_kalir() -> None:
    """D-219 sablonu arsive kacar; 3 referans onu okuyor."""
    assert (VAULT_KOK / "_ajan_context_sablon.md").is_file(), (
        "D-219 ajan context sablonu kokten tasinmis/tasinmamaya calisiliyor. "
        "Bu dosya olmadan ajanlar kalici hafiza uretemiyor."
    )

