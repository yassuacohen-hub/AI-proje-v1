# -*- coding: utf-8 -*-
import subprocess
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ozet = (
    "D-355 Faz A-B tamamlandi. Faz A: 0062_odeme_musteri_ayar.sql + down "
    "(odeme, musteri_ayar tablo, 6 RLS politikasi sahibi+admin, GRANT yok D-306/3 uyumlu). "
    "Faz B: musteri_odeme.py + musteri_kredi.py alt sekme govdeleri "
    "(3 render fn: odemeler/ayarlar/krediler), SECTIONS'a kayitli. "
    "Duzeltmeler: (1) test_sayfa_iskeleti MUAF'a musteri_odeme+musteri_kredi gerekceli eklendi "
    "(alt sekme govdesi, PageHeader yok - D-355 kurali); "
    "(2) 3 kilitli dosyada dosya_sonu (sonda newline) duzeltildi. "
    "Test: test_musteri_odeme 7/7 + musteri_odeme+dashboard_nav 127/127 yesil. "
    "KAPSAM DISI 2 hata admin_denetim (Section + 4 subheader): baska gorevin ekrani, yasuma ait degil, ilgili sahibe iletilecek."
)
karar = (
    "kapandi: 7/7 + 127/127 test yesil; 2 kapsam disi hata admin_denetim icin dikkat olarak ilgili sahibe iletilecek"
)

cmd = [
    sys.executable, "scripts/bulgu_defteri.py", "ekle",
    "--task-id", "VERI-MUSTERI-ODEME-AYAR-01",
    "--rol", "yasu",
    "--ozet", ozet,
    "--karar", karar,
    "--renk", "tamam",
]
r = subprocess.run(cmd, cwd=r"c:\HUGINN~1\HUGINN~1",
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print("STDOUT:\n" + (r.stdout or ""))
print("STDERR:\n" + (r.stderr or ""))
print("RC:", r.returncode)
sys.exit(r.returncode)
