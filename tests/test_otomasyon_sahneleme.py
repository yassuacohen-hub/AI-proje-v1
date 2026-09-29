"""D-288: hicbir betik toptan sahneleme (`git add -A` / `git add .`) yapmaz.

NEDEN: `scripts/git_auto_push.bat` gunde iki kez `git add -A` ile tum agaci
sahneliyordu. Olculdu: 64 otomatik commit, 2150 benzersiz dosya (src/ 217,
tests/ 143, scripts/ 233). `dfc5f0a` tek basina 352 dosya / 41619 satir aldi;
ucustaki kodu ve D-241 geregi SILINMIS bir araci tarihe soktu. "Tek tek sahnele"
kurali uc ajan icin vardi ama zorlayani yoktu (D-261 deseni).

Mandal `git ls-files` uzerinden calisir: diske degil, IZLENEN betige bakar.
Belge/rapor taranmaz -- oradaki `git add -A` metni bir komut degil, bir kayittir
(D-270: metin taramasi tek basina kanit degil, bu yuzden kapsam yurutulebilir
dosya uzantilariyla sinirlandi).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1]

#: Yalnizca yurutulebilir betikler. `.md`/`.json`/`.jsonl` kayit tutar, komut calistirmaz.
BETIK_UZANTILARI = {".bat", ".cmd", ".ps1", ".sh", ".py"}

#: git cagrisi: duz `git`, .bat degiskeni `%GIT%`, kabuk degiskeni `$GIT`/`${GIT}`.
#: ILK SURUM SADECE `git` ARIYORDU ve `"%GIT%" add -A` satirini KACIRIYORDU; mandal
#: yalanci yesildi. Kirarak dogrulama yakaladi (bkz. D-288 kaydi).
CAGRI = r"""(?:git|%[A-Za-z_]*GIT[A-Za-z_]*%|\$\{?[A-Za-z_]*GIT[A-Za-z_]*\}?)"""

#: `git add -A`, `git add --all`, `git add .` -- tirnakli/listeli bicimleri de yakalar.
TOPTAN = re.compile(
    CAGRI + r"""["']?\s*,?\s*["']?add["']?\s*,?\s*["']?(?:-A|--all|\.)(?=["'\s]|$)""",
    re.IGNORECASE,
)

#: Mandalin kendisi deseni metin olarak tasir; kendini sayamaz.
MUAF = {"tests/test_otomasyon_sahneleme.py"}

#: Yorum baslangiclari. Kurali ANLATAN metin ile kurali CAGIRAN satir ayni sey degil;
#: gerekce yazmak (D-267) ihlal sayilmamali.
YORUM = re.compile(r"""^\s*(#|REM\b|::|//)""", re.IGNORECASE)
UCLU = re.compile(r'"""|\'\'\'')


def _kod(metin: str) -> str:
    """Yorum satirlarini ve uclu tirnakli bloklari atar, geriye calisan kod kalir."""
    satirlar: list[str] = []
    blokta = False
    for satir in metin.splitlines():
        tek = len(UCLU.findall(satir)) % 2 == 1
        if blokta:
            blokta = not tek
            continue
        if tek:
            blokta = True
            continue
        if not YORUM.match(satir):
            satirlar.append(satir)
    return "\n".join(satirlar)


def _izlenen_betikler() -> list[str]:
    ciktilar = subprocess.run(
        ["git", "ls-files"],
        cwd=VAULT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    return [
        y
        for y in ciktilar
        if Path(y).suffix.lower() in BETIK_UZANTILARI and y not in MUAF
    ]


def test_d288_hicbir_betik_toptan_sahnelemez() -> None:
    """Yurutulebilir hicbir izlenen dosya `git add -A|--all|.` cagirmaz."""
    suclular: list[str] = []
    for yol in _izlenen_betikler():
        tam = VAULT / yol
        if not tam.is_file():
            continue  # index hayaleti (D-281): diskte yok, taranamaz
        metin = _kod(tam.read_text(encoding="utf-8", errors="replace"))
        if TOPTAN.search(metin):
            suclular.append(yol)
    assert not suclular, (
        f"D-288 ihlali: {len(suclular)} betik toptan sahneleme yapiyor -> {suclular}. "
        "Beyaz liste kullan: `git add -- <yol> [<yol>...]`. "
        "Toptan sahneleme ucustaki kodu ve silinmis araclari tarihe sokar; "
        "kapsam disi kalan tek bir kimlik dosyasi geri alinamaz bicimde sizar."
    )


def test_d288_otomasyon_betigi_beyaz_liste_kullaniyor() -> None:
    """Gunluk otomasyon hala `git add` yapiyor ama YOL vererek yapiyor.

    Yalniz `-A`'nin yoklugunu olcmek yetmez: birisi `add` satirini tumden silse
    yedek sessizce bosalir ve ustteki mandal yine yesil kalirdi.
    """
    betik = VAULT / "scripts" / "git_auto_push.bat"
    assert betik.is_file(), "scripts/git_auto_push.bat diskte yok."
    metin = betik.read_text(encoding="utf-8", errors="replace")
    assert 'add -- "%%P"' in metin, (
        "git_auto_push.bat beyaz liste ile sahnelemiyor; "
        "`git add -- <yol>` bicimi bekleniyor."
    )


if __name__ == "__main__":  # ponytail: cerceve yok, tek kosulur dogrulama
    test_d288_hicbir_betik_toptan_sahnelemez()
    test_d288_otomasyon_betigi_beyaz_liste_kullaniyor()
    print("OK")
