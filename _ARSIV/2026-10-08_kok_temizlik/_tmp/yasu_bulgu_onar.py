# -*- coding: utf-8 -*-
import sys, pathlib, re, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\bulgu_defteri.md")
ham = p.read_bytes()

# UTF-16LE parcasi: \x00 arali deseni (duzenli null byte yogunlugu)
# ilk bolgeyi bul: ardışik en az 6 (char, 0x00) çiftini yakala
m = None
for mm in re.finditer(rb"(?:[\x20-\x7e\xc0-\xff]\x00){6,}", ham):
    if m is None or mm.start() < m.start():
        m = mm
if m is None:
    print("UTF-16LE izi BULUNAMADI — dokunulmadi")
    sys.exit(1)

sinir = m.start()
print("UTF-16LE parcasinin baslangic konumu:", sinir, "| toplam:", len(ham))

utf8_kisim = ham[:sinir]
utf16_kisim = ham[sinir:]
# tek eksik byte olmasin diye tek byte dusse de decode dene
if len(utf16_kisim) % 2 == 1:
    utf16_kisim = utf16_kisim + b"\x00"
metin16 = utf16_kisim.decode("utf-16le", errors="replace")
print("UTF-16 parcasi ilk 200 karakter:", repr(metin16[:200]))

# gecerli kismi dogrula
utf8_kisim.decode("utf-8")  # hata verirse yontum kopup patlar
yeni = utf8_kisim + metin16.encode("utf-8")
# yedek al, sonra yaz
yedek = p.with_suffix(".md.yedek_enc")
shutil.copy2(p, yedek)
p.write_bytes(yeni)
print("ONARILDI. yedek:", yedek.name)
# dogrula
p.read_text(encoding="utf-8")
print("UTF-8 DOGRULAMA OK, yeni boyut:", p.stat().st_size)
