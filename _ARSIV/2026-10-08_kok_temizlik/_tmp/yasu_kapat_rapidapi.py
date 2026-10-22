# -*- coding: utf-8 -*-
"""VERI-RAPIDAPI-OSINT-ISTEMCI-01: 2 acik chat kaydini gerekceli kararla kapat."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master import chat

tid = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"

# index=5: kademe-1 yasağı kaydi — bu tur kademe-2 (uygulama) yetkisi verildi, PO dogrudan
# "yapip teslim et" emri verdi; kod fiilen yazildi (rapidapi_osint.py) ve 9/9 test geciyor.
karar5 = (
    "KADEME KONULU COZULDU: Bu tur PO dogrudan 'yapip teslim et' emri verdi ve fiilen kademe-2 "
    "(uygulama) yetkisi kullanildi — kod yazildi (src/company_master/engine/rapidapi_osint.py), "
    "9/9 test gecti (tests/test_rapidapi_osint.py). Kayit 2026-10-06 nobet turuna ait; nobet_modu.json "
    "kurulumundan (D-65, ihsan 2026-10-10) bu yana kademe kurali ayrik. Eski kademe-1 itirazi artik "
    "uygulanamaz durumda -> stale, gerekceli kapatildi."
)

# index=6: GUNLUK_TAVAN=50 varsayimi — kaydin kendi onerdigi cozum uygulandi: kodda
# 'varsayim, dogrulanmadi' yorumu. Abonelik plani teyidi PO'ya dusuyor, kod tarafi kapandi.
karar6 = (
    "GUNLUK_TAVAN=50 COZULDU: Kaydin kendi onerdigi cozum uygulandi — rapidapi_osint.py'de GUNLUK_TAVAN=50 "
    "'varsayim, dogrulanmadi; PO/RapidAPI abonelik plani teyidi bekliyor' yorumuyla isaretlendi. "
    "Istemci env ile override edilebilir (HUGINN_RAPIDAPI_GUNLUK_TAVAN), yani abonelik plani nettilesince "
    "kod degisikligi gerekmez. Kod/istemci tarafi kapandi; abonelik rakaminin teyidi ayri bir PO karari, "
    "bu gorevin kod kapsamini bloklamaz."
)

r5 = chat.kapat(tid, 5, karar5)
r6 = chat.kapat(tid, 6, karar6)
print("index=5 kapat:", "OK" if r5 and r5.get("durum") == "cozuldu" else "HATA", "->", (r5 or {}).get("durum"))
print("index=6 kapat:", "OK" if r6 and r6.get("durum") == "cozuldu" else "HATA", "->", (r6 or {}).get("durum"))

# dogrula: artik acik kayit kalmasin
kalan = [i for i, k in enumerate(chat.oku(tid)) if k.get("durum") == "acik"]
print("kalan acik indexler:", kalan)
