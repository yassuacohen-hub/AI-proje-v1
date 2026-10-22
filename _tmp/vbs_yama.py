# -*- coding: utf-8 -*-
"""EKREND hata penceresi tamiri: kombo_senkron_bekcisi.vbs 6. satirda
'C:\Program Files\Python312\python.exe' cagiriyor; bu yol YOK
=> WScript 80070002 'Sistem belirtilen dosyayi bulamiyor' => PO ekraninda pencere.

Onarim: bayat yolu GERCEK python yoluyla degistir (byte-duzeyi, kodlama bozulmaz),
once yedek, sonra wscript ile canli dogrulama (rc=0 ve pencere yok).
"""
import py_compile
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

VBS = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\scripts"
           r"\kombo_senkron_bekcisi.vbs")
HEDEF_PY = Path(r"c:\Huginn Data Projesi\Huginn Data Insights"
                r"\scripts\9router_ayar_senkron.py")

BAYAT = rb"C:\Program Files\Python312\python.exe"


def gercek_python() -> bytes:
    """Bu yorumlayicinin mutlak yolu = kanitli calisan python."""
    return str(Path(sys.executable)).encode("mbcs")


def main() -> int:
    ham = VBS.read_bytes()
    print("vbs boyut:", len(ham), "bayt")
    print("hedef script var mi:", HEDEF_PY.exists())
    print("bayat yol gecen yer sayisi:", ham.count(BAYAT))

    yeni_yol = gercek_python()
    print("gercek python:", yeni_yol.decode("mbcs"))
    if not Path(yeni_yol.decode("mbcs")).exists():
        raise SystemExit("python yolu dogrulanamadi — islem yok")

    if BAYAT not in ham:
        print("ZATEN DUZELMIS (bayat yol yok) — dokunulmadi")
        return 0

    yedek = VBS.with_name("kombo_senkron_bekcisi.vbs.yedek-20261020")
    shutil.copy2(VBS, yedek)
    print("yedek:", yedek.name)

    duz = ham.replace(BAYAT, yeni_yol)
    VBS.write_bytes(duz)
    print("YAMALANDI · yeni boyut:", VBS.read_bytes().__len__())
    print("kalan bayat yol:", VBS.read_bytes().count(BAYAT))

    print("\nCANLI DOGRULAMA: wscript ile calistir (gizli pencere, rc olmali)")
    r = subprocess.run(["wscript.exe", str(VBS)], capture_output=True,
                       text=True, timeout=60)
    print("wscript rc:", r.returncode, "| hata ciktisi:", (r.stderr or "YOK")[:120])
    print("=> rc=0 ve stderr bos ise artik hata penceresi CIKMAZ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
