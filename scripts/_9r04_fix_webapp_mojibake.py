# -*- coding: utf-8 -*-
"""web_app.py'deki UTF-8 mojibake (double-encoding) onarimi.

Sorun: Turkce karakterler once UTF-8'e encode edilip sonra cp1252 ile yanlis
decode edilip tekrar UTF-8 olarak kaydedilmis. Ornek:
  "O" -> C3 96 -> cp1252'de "Ã–" -> tekrar UTF-8 -> C3 83 E2 80 93
Bu betik ham baytlari esleserek dogru UTF-8 baytlarina cevirir.
"""
from pathlib import Path

YOL = Path(__file__).resolve().parents[1] / "web_app.py"

# (bozuk bayt kaliplari, dogru UTF-8 baytlari)
DEGISIMLER: list[tuple[bytes, bytes]] = [
    # Buyuk harfler
    (b"\xc3\x84\xc2\xb0", "İ".encode("utf-8")),        # Ä°  -> İ
    (b"\xc3\x85\xc2\x9e", "Ş".encode("utf-8")),        # Å\u009e -> Ş
    (b"\xc3\x84\xc2\x9e", "Ğ".encode("utf-8")),        # Ä\u009e -> Ğ
    (b"\xc3\x83\xc5\x93", "Ü".encode("utf-8")),        # Ãœ  -> Ü
    (b"\xc3\x83\xe2\x80\x93", "Ö".encode("utf-8")),    # Ã–  -> Ö
    (b"\xc3\x83\xe2\x80\xa1", "Ç".encode("utf-8")),    # Ã‡  -> Ç
    (b"\xc3\x84\xc2\xb1", "ı".encode("utf-8")),        # Ä±  -> ı
    (b"\xc3\x86\xc2\xb0", "İ".encode("utf-8")),        # (alternatif İ kalıbı)
    # Kucuk harfler
    (b"\xc3\x85\xc5\xb8", "ş".encode("utf-8")),        # ÅŸ  -> ş
    (b"\xc3\x84\xc5\xb8", "ğ".encode("utf-8")),        # ÄŸ  -> ğ
    (b"\xc3\x83\xc2\xbc", "ü".encode("utf-8")),        # Ã¼  -> ü
    (b"\xc3\x83\xc2\xb6", "ö".encode("utf-8")),        # Ã¶  -> ö
    (b"\xc3\x83\xc2\xa7", "ç".encode("utf-8")),        # Ã§  -> ç
]

def main() -> int:
    raw = YOL.read_bytes()
    toplam = 0
    for bozuk, dogru in DEGISIMLER:
        sayi = raw.count(bozuk)
        if sayi:
            raw = raw.replace(bozuk, dogru)
            toplam += sayi
            print(f"  degisti {sayi}x  {bozuk!r} -> {dogru!r}")
    if toplam:
        YOL.write_bytes(raw)
        print(f"TOPLAM {toplam} mojibake onarildi: {YOL}")
    else:
        print("Hic mojibake bulunamadi (belki zaten duzgun veya kalip farkli).")
    # Dogrulama
    import py_compile
    try:
        py_compile.compile(str(YOL), doraise=True)
        print("py_compile: OK (sozdizimi gecerli)")
    except py_compile.PyCompileError as exc:
        print("py_compile HATASI:", exc)
        return 1
    # Kalan bozuk kalip var mi?
    kalan = sum(raw.count(b) for b, _ in DEGISIMLER)
    print(f"Kalan bozuk kalip: {kalan}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())