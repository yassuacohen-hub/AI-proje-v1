"""or_* betiklerine standart baslik ekler (olcum, kalici degil).

Ekler:
  1) `# -*- coding: utf-8 -*-` + bos satir
  2) Modul docstring'i (dosya adindan turetilir) + bos satir
  3) utf-8 stdout sarmali (Windows kod sayfasi Turkce karakterleri
    EncodeError verir; bu olcumdu: or_seckin.py PowerShell'de patladi)
Zaten varsa dokunmaz (idempotent).
"""
import pathlib
import re

KOK = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights\scripts")

ACIKLAMA = {
    "or_kod_liste.py": ("OpenRouter kod modelleri: fiyat + indirim + deger analizi.",
                        "python -X utf8 scripts/or_kod_liste.py"),
    "or_seckin.py": ("Seckin'in kullandigi kod modelleri + :batch indirim kazanci.",
                     "python -X utf8 scripts/or_seckin.py"),
    "or_fiyat_ara.py": ("OpenRouter modelinde fiyat arama.",
                        "python -X utf8 scripts/or_fiyat_ara.py <model>"),
    "or_sablon_ekle.py": ("Continue yapilandirmasina model sablonu ekler.",
                          "python -X utf8 scripts/or_sablon_ekle.py"),
    "or_batch_cikar.py": (":batch modellerini listeden cikarir (ayri API ister).",
                          "python -X utf8 scripts/or_batch_cikar.py"),
}

SARMAL = (
    "import sys\n"
    "\n"
    "if hasattr(sys.stdout, \"reconfigure\"):\n"
    "    sys.stdout.reconfigure(encoding=\"utf-8\", errors=\"replace\")\n"
)

for ad, (aciklama, kullanim) in ACIKLAMA.items():
    yol = KOK / ad
    if not yol.is_file():
        print("YOK:", ad)
        continue
    metin = yol.read_text(encoding="utf-8", errors="replace")
    degisti = []
    if not metin.startswith("# -*- coding: utf-8 -*-"):
        metin = "# -*- coding: utf-8 -*-\n" + metin
        degisti.append("coding")
    # docstring: ilk cift tirnakli blok
    if not re.match(r'^#.*?\n\s*"""', metin, re.S):
        govde = ("---\n\n"
                 f"{aciklama}\n\n"
                 f"Kullanim:\n    {kullanim}\n\n"
                 "Anahtar degerleri HICBIR cikti/loga yazilmaz (D-288).\n")
        metin = metin.replace('"""', '"""\n' + govde, 1)
        degisti.append("docstring")
    if "reconfigure" not in metin:
        # import sys sonrasi ya da basta ekle
        satir = metin.splitlines(True)
        konum = 0
        for i, ln in enumerate(satir):
            if ln.startswith("import ") or ln.startswith("from "):
                konum = i + 1
        satir.insert(konum, "\n" + SARMAL)
        metin = "".join(satir)
        degisti.append("sarmal")
    yol.write_text(metin, encoding="utf-8")
    print(f"{ad:22} -> {','.join(degisti) or 'zaten hazir'}")