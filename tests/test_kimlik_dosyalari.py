"""D-293: ozel anahtar / sertifika dosyalari depoya girmez.

NEDEN: `config/certs/selfsigned.key` (gercek RSA ozel anahtar) 2026-09-20'de
`90c4702` ile elle commit edildi. Dosya bugun ne HEAD agacinda ne index'te;
`.gitignore:155-156` (`*.key`, `*.pem`) 2026-09-24'te `7a9ff2c` ile eklendi.
Ama kurali ZORLAYAN hicbir sey yoktu -- desenler tek bir elle duzenlemeyle
kaybolsa kimse fark etmezdi (D-261 deseni: zorlayicisi olmayan kural, kural degil).

IKI AYRI SEY olculur:
1. `git ls-files` -- IZLENEN dosyada kimlik uzantisi var mi (gercek durum).
2. `git check-ignore` -- desen GERCEKTEN eslesiyor mu (D-270: `.gitignore`
   metnini okumak yetmez; `/_*.txt` ornegi D-288'de tam da boyle yaniltti,
   desen dosyada YAZIYORDU ama alt dizine inmiyordu).

`.crt`/`.cer` KAPSAM DISI: sertifika acik anahtardir, sizmasi zarar vermez ve
test fikstürü olarak mesru sekilde izlenebilir. Yasak yalniz SIR tasiyanlara.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1]

#: Sir tasiyan kimlik uzantilari. `.crt`/`.cer`/`.pub` bilerek disarida (acik anahtar).
SIR_UZANTILARI = (".key", ".pem", ".p12", ".pfx", ".jks", ".keystore")

#: Desen kapsamini olcmek icin kullanilan ornek yollar: kok, alt dizin, derin alt dizin.
#: Uclu ornek, D-288'de yakalanan "yalniz koke bagli desen" hatasini yakalar.
ORNEK_YOLLAR = ("gizli.key", "config/certs/selfsigned.key", "a/b/c/sunucu.pem")


def _izlenen() -> list[str]:
    return subprocess.run(
        ["git", "ls-files"],
        cwd=VAULT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()


def test_d293_izlenen_ozel_anahtar_yok() -> None:
    """Hicbir izlenen dosya sir tasiyan kimlik uzantisi taşimaz."""
    suclular = [y for y in _izlenen() if y.lower().endswith(SIR_UZANTILARI)]
    assert not suclular, f"izlenen kimlik dosyasi: {suclular}"


def test_d293_gitignore_kimlik_desenleri_gercekten_esliyor() -> None:
    """`git check-ignore` ile olculur: desen var demek, desen calisiyor demek degil."""
    tutulmayan: list[str] = []
    for yol in ORNEK_YOLLAR:
        sonuc = subprocess.run(
            ["git", "check-ignore", "-q", "--no-index", yol],
            cwd=VAULT,
            capture_output=True,
            text=True,
        )
        if sonuc.returncode != 0:
            tutulmayan.append(yol)
    assert not tutulmayan, f".gitignore bu kimlik yollarini tutmuyor: {tutulmayan}"
