"""D-241: dis kok (git deposu koku) temiz kalir — mandal.

D-221 kok politikasini yaziyordu ama mandali yoktu; .gitignore deseni de
dosyalar zaten takipli oldugu icin islemiyordu. Sonuc: kokte 131 dosya birikti.
Bu test kapiyi kurar: kokte izin listesi disinda dosya olusursa kirmizi yanar.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
from typing import Iterable

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

#: Esszamanli ajan kilit kaydi (D-272/7).
KILIT_DOSYA = VAULT_KOK / "data" / "orchestrator" / "file_locks.json"

#: D-281 olcumu: kokte index'te duran ama diskte olmayan tek kullanimlik
#: dosya sayisi. BORC-SCRIPTS-01 kesilmesi urun sahibi kararina bagli
#: (kaynaksiz "borcumuz kalsin" iddiasi dogrulanamadi), bu yuzden borc
#: SIFIRLANMADI ama TAVANLANDI: artamaz, yalniz kuculur.
KOK_HAYALET_TAVANI = 76

#: D-281 olcumu: kilitli ama index hayaleti olan dosya sayisi. Ikisi de
#: yasu'nun acik isi (`ALTYAPI-SKILL-YAPISI-01`, D-269 skill havuzu);
#: baska ajanin silmesi bu turda commit EDILMEDI. Tavan yalniz kuculur.
KILIT_HAYALET_TAVANI = 2


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


# ---------------------------------------------------------------------------
# D-281: index hayaleti — diskte yok ama git index'te var
# ---------------------------------------------------------------------------


def _index_dosyalari() -> frozenset[str]:
    """Git index'teki yollar (vault koku gore). Git yoksa bos kume."""
    try:
        cp = subprocess.run(
            ["git", "ls-files"],
            cwd=VAULT_KOK,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):  # git yok / calismadi
        return frozenset()
    return frozenset(cp.stdout.splitlines()) if cp.returncode == 0 else frozenset()


def _index_hayaletleri(yollar: Iterable[str]) -> list[str]:
    """Index'te VAR ama diskte YOK olan yollar — commit edilmemis silme.

    Diskte de index'te de olmayan yol hayalet DEGILDIR: henuz yazilmamis
    dosyanin mesru rezervasyonudur (file_locks bunu destekler).
    """
    idx = _index_dosyalari()
    return sorted(y for y in yollar if y in idx and not (VAULT_KOK / y).exists())


def test_d281_kilitli_dosya_index_hayaleti_degil() -> None:
    """file_locks kaydi commit edilmemis silmeye isaret etmez (D-281).

    D-261 deseninin aynasi: kayit var, gerceklik yok. Ayrim onemli —
    rezervasyon (hic olmayan dosya) mesru, index hayaleti (silinmis ama
    commit edilmemis) calisma agacini yalanci yapar.
    """
    if not KILIT_DOSYA.is_file():
        pytest.skip("file_locks.json yok")
    kilitler = json.loads(KILIT_DOSYA.read_text(encoding="utf-8"))
    hayalet = _index_hayaletleri(kilitler)
    assert len(hayalet) <= KILIT_HAYALET_TAVANI, (
        f"{len(hayalet)} kilitli dosya index'te var ama diskte yok (tavan "
        f"{KILIT_HAYALET_TAVANI}): {hayalet}\n"
        "Cozum: silme commit edilir ve kilit birakilir. Kilidi olan ajan "
        "silmeyi commit etmeden isi bitmis saymaz. Tavan yalniz KUCULUR."
    )


def test_d281_kokte_index_hayaleti_tek_kullanimlik_yok() -> None:
    """D-221 mandalinin kor noktasi: diske bakiyordu, index'e bakmiyordu.

    Kokteki tek kullanimlik betikler diskten silinmis ama commit
    edilmemisti: `iterdir()` onlari gormedigi icin mandal yesil yaniyordu.
    D-270'in aynasi — yokluk disk taramasiyla kanitlanmaz.
    """
    kok_index = (y for y in _index_dosyalari() if "/" not in y)
    hayalet = [
        y
        for y in _index_hayaletleri(kok_index)
        if y not in IZINLI_ONEKLI
        and (y.startswith("_") or y.startswith(TEK_KULLANIMLIK_ONEK))
    ]
    assert len(hayalet) <= KOK_HAYALET_TAVANI, (
        f"Kokte {len(hayalet)} index hayaleti var, tavan {KOK_HAYALET_TAVANI} "
        f"(D-281 olcumu). Yeni ornekler: {hayalet[:5]}\n"
        "Cozum: silme commit edilir. Diskten silmek yetmez — index'te kalan "
        "kayit sonraki ajana 'bu betik var' der. Tavan yalniz KUCULUR."
    )

