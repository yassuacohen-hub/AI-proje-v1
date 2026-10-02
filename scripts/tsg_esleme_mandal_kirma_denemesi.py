"""VERI-TSG-ESLEME-CASE-01 mandalının KIRILDIĞINI kanıtlar (D-256/4).

`_TR_ASCII` tablosundaki `ı -> I` ve `ş -> S` karşılıklarını geçici olarak
kaldırır (eski hatalı katlamaya döndürür), mandalın kırmızıya döndüğünü
ölçer ve dosyayı bit düzeyinde geri yükler.

Kullanım: python scripts/tsg_esleme_mandal_kirma_denemesi.py
"""

import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEDEF = os.path.join(KOK, "skills", "services", "ticaret_sicili_kanit.py")
TEST = os.path.join("tests", "test_tsg_zincir.py")

#: Eski (hatalı) katlamanın ikisini geri getiren satırlar.
KALDIRILACAK = ('        "ı": "I",\n', '        "ş": "S",\n')


def pytest_kos() -> int:
    return subprocess.call(
        [sys.executable, "-X", "utf8", "-m", "pytest", TEST, "-q", "-p", "no:randomly"],
        cwd=KOK,
    )


def main() -> int:
    yedek = os.path.join(tempfile.gettempdir(), "kanit_d317.yedek")
    shutil.copy2(HEDEF, yedek)
    try:
        metin = open(HEDEF, encoding="utf-8").read()
        yeni = metin
        for satir in KALDIRILACAK:
            if satir not in yeni:
                print(f"[UYARI] satir bulunamadi: {satir!r} — kirilma denemesi gecersiz")
                return 1
            yeni = yeni.replace(satir, "", 1)
        with open(HEDEF, "w", encoding="utf-8", newline="") as f:
            f.write(yeni)

        kod = pytest_kos()
        if kod == 0:
            print("[KIRILMA YOK] mandal eski hatayi YAKALAMADI - mandal ise yaramaz")
            return 1
        print("[DOGRULANDI] mandal eski ASCII katlamasini yakaladi (kirmizi)")
        return 0
    finally:
        shutil.copy2(yedek, HEDEF)
        kod2 = pytest_kos()
        print(f"[GERI ALINDI] kanit dosyasi eski haline dondu; mandal kodu={kod2}")
        if kod2 != 0:
            print("[UYARI] geri alma sonrasi mandal yine kirmizi - dosya bozuldu")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
