# -*- coding: utf-8 -*-
import sys, importlib.util
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pathlib
BASE = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")
L = (BASE / "tests/test_sayfa_iskeleti.py").read_text(encoding="utf-8").splitlines()
# MUAF blogu (satir 41-60) + EKRANLAR turetim mekanizmasi
print("=== MUAF SOZLUGU (41-70) ===")
for i in range(40, 70):
    if i < len(L):
        print(f"{i+1}| {L[i]}")

# EKRANLAR'i gercekten hesapla
import ast
TABS = BASE / "web_dashboard" / "tabs"
kaynak = (BASE / "tests/test_sayfa_iskeleti.py").read_text(encoding="utf-8")
mod = ast.parse(kaynak)
# MUAF anahtarlarini cek
muaf_keys = set()
for node in ast.walk(mod):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "MUAF":
                for k in node.value.keys:
                    if isinstance(k, ast.Constant):
                        muaf_keys.add(k.value)
mevcut = {p.stem for p in TABS.glob("*.py") if not p.stem.startswith("_")}
ekranlar = sorted(mevcut - muaf_keys)
print("\n=== EKRANLAR (test edilecek) ===")
print(ekranlar)
print("\nmusteri_odeme kapsamda mi?:", "musteri_odeme" in ekranlar)
print("musteri_kredi kapsamda mi?:", "musteri_kredi" in ekranlar)
print("admin_denetim kapsamda mi?:", "admin_denetim" in ekranlar)
