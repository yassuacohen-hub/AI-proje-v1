# -*- coding: utf-8 -*-
"""bilo 4.8.C bolumundeki kalan yenisatir/kontrol-karakteri yutmalarini ve yarim mojibake'yi duzeltir.
Kullanim: python -X utf8 ..\\_tmp\\ortak_son_duzelt.py DOSYA [--yaz]"""
import re
import sys

yol = sys.argv[1]
yaz = "--yaz" in sys.argv
CTL = r"[\x00-\x08\x0b\x0c\x0e-\x1f]?"
metin = open(yol, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in metin else "\n"
satirlar = metin.split(nl)

# 1) "|" ile biten satir + "ode_modules" ile baslayan satir => 'n' yutulmus, birlestir
cikti, i = [], 0
while i < len(satirlar):
    s = satirlar[i]
    if i + 1 < len(satirlar) and s.rstrip().endswith("|") and satirlar[i + 1].startswith("ode_modules"):
        s = s.rstrip() + " n" + satirlar[i + 1]
        i += 1
    cikti.append(s)
    i += 1

SUB = [
    (r"(?<![A-Za-z])" + CTL + r"rontend", "frontend"),
    (r"(?<![A-Za-z])" + CTL + r"rowser-testing", "browser-testing"),
    (r"(?<![A-Za-z])" + CTL + r"onts\.googleapis", "fonts.googleapis"),
    (r"(?<![A-Za-z])" + CTL + r"rand\.md", "brand.md"),
    (r"(?<![A-Za-z])" + CTL + r"pp/", "app/"),
    (r"(- )\t?sc --noEmit", r"\1tsc --noEmit"),
    (r"Kurulu ✅ ✅ .*? \|", "Kurulu ✅ |"),
    (r"Ä±", "ı"),
    (r"Å\x9f|Å(?=[a-z])", "ş"),
]
degisen = 0
for k, s in enumerate(cikti):
    y = s
    for kalip, yeni in SUB:
        y = re.sub(kalip, yeni, y)
    if y != s:
        degisen += 1
        cikti[k] = y
sonuc = nl.join(cikti)
kalan = [(n + 1, l[:90]) for n, l in enumerate(cikti) if re.search(r"[ÃÂÄÅâ]|[\x00-\x08\x0b\x0c\x0e-\x1f]", l)]
print("degisen satir", degisen, "kalan supheli", len(kalan))
for n, l in kalan:
    print(n, repr(l))
if yaz:
    open(yol, "w", encoding="utf-8", newline="").write(sonuc)
    print("yazildi", yol)
