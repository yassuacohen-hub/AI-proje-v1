# -*- coding: utf-8 -*-
import ast
import sys
import pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")
DOSYA = BASE / "src/company_master/api/routers/v1/v1_network.py"
src = DOSYA.read_text(encoding="utf-8")
L = src.splitlines(keepends=True)
agac = ast.parse(src)

funcs = [n for n in agac.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

# get_full_report'un ust-duzey return'unu (ilk return) bul; o return'dan SONRAKI
# tum ust-duzey statementlari olule -> sil.
gfr = next(f for f in funcs if f.name == "get_full_report")
ilk_return_idx = None
for i, s in enumerate(gfr.body):
    if isinstance(s, ast.Return):
        ilk_return_idx = i
        break

olu_baslangic = gfr.body[ilk_return_idx + 1].lineno  # return'dan sonraki ilk stmt
olu_bitis = gfr.end_lineno  # fonksiyonun bittigi satir

# Cift tanimlar: _fetch_company_by_vkn ve _get_company_vkn'in 2. tanimlari
by_name = {}
for f in funcs:
    by_name.setdefault(f.name, []).append(f)
cift_silinecek = []
for ad in ("_fetch_company_by_vkn", "_get_company_vkn"):
    if len(by_name.get(ad, [])) == 2:
        cift_silinecek.append((by_name[ad][1].lineno, by_name[ad][1].end_lineno))

# Silinecek satir araliklarini birlestir (1-based, dahil)
silinecek = []
silinecek.append((olu_baslangic, olu_bitis))
for lb, eb in cift_silinecek:
    silinecek.append((lb, eb))
silinecek.sort()

print(f"Olu kod (get_full_report return sonrasi): {olu_baslangic}-{olu_bitis}")
for lb, eb in cift_silinecek:
    print(f"Cift tanim: {lb}-{eb}")

# Satirlari filtrele: silinecek araliklardaki 1-based satirlari at
sil = set()
for lb, eb in silinecek:
    sil.update(range(lb, eb + 1))

# Birlestirilmis aralik sonrasi kalan bosluklari da temizleme: once sadece
# belirlenen satirlari at, sonra sondaki fazla bosluklari normallestir.
yeni = [satir for idx, satir in enumerate(L, 1) if idx not in sil]
yeni_src = "".join(yeni)

# Sondaki 3+ bos satiri 1'e indir (dosya sonu)
yeni_src = yeni_src.rstrip("\n") + "\n"

# Dogrula: tekrar parse edilebiliyor mu + fonksiyon sayisi
yeni_agac = ast.parse(yeni_src)
yeni_funcs = [n for n in yeni_agac.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
adlar = {}
for f in yeni_funcs:
    adlar[f.name] = adlar.get(f.name, 0) + 1
print("\n=== YENI DURUM ===")
print(f"Satir sayisi: {len(L)} -> {len(yeni_src.splitlines())}")
print(f"Fonksiyon sayisi: {len(funcs)} -> {len(yeni_funcs)}")
cift = {k: v for k, v in adlar.items() if v > 1}
print(f"Kalan cift tanim: {cift if cift else 'YOK'}")
# get_full_report artik tek return'li mi
gfr2 = next(f for f in yeni_funcs if f.name == "get_full_report")
ret = [s for s in gfr2.body if isinstance(s, ast.Return)]
print(f"get_full_report ust-duzey return sayisi: {len(ret)}")

DOSYA.write_text(yeni_src, encoding="utf-8")
print("\nYAZILDI.")
