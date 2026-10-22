# -*- coding: utf-8 -*-
"""(1) codex_gui_takma_ad.py ESLEME tablosunu OLCULEN canli hedeflerle esitle
   (2) ~/.codex/MODELLER.md 'GUI'den secme' yasaagini kaldir (artik guvenli)
Her iki dosya icin once yedek; regex ile hedefli degisiklik; geri okuma dogrulamasi."""
import re
import shutil
from pathlib import Path

BETIK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\scripts\codex_gui_takma_ad.py")
MD = Path.home() / ".codex" / "MODELLER.md"

# 20.10 ~21:28 canli /responses olcumu ile dogrulanmis hedefler
YENI = {
    "gpt-5.6-sol": "cx/gpt-5.6-luna",
    "deepseek-v4.1-flash": "openrouter/nvidia/nemotron-3.5-lightning:free",
    "glm-5.3": "openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
}


def betik_esitle() -> None:
    metin = BETIK.read_text(encoding="utf-8")
    shutil.copy2(BETIK, BETIK.with_name(BETIK.name + ".yedek"))
    oncesi = metin
    for ad, hedef in YENI.items():
        metin = re.sub(r'("%s": )"[^"]*"' % re.escape(ad),
                       r'\g<1>"%s"' % hedef, metin, count=1)
    if metin == oncesi:
        print("BETIK: degisiklik gerekmedi/eslesmedi")
    BETIK.write_text(metin, encoding="utf-8")
    geri = BETIK.read_text(encoding="utf-8")
    for ad, hedef in YENI.items():
        satir = '"%s": "%s"' % (ad, hedef)
        print(("OK  " if satir in geri else "KONTROL ET ") + satir)
    # sozdizimi kontrolu
    import ast
    ast.parse(geri)
    print("BETIK: sozdizimi gecerli")


def md_guncelle() -> None:
    metin = MD.read_text(encoding="utf-8")
    shutil.copy2(MD, MD.with_name("MODELLER.md.yedek-20261020"))
    yeni_baslik = """## DURUM (2026-10-20 ~21:28): GUI'den seçim ARTIK GÜVENLİ ✅

Sorun neydi (ölçüldü): Codex masaüstü, listeden her seçimde ayar dosyasına
KENDİ katalog adını yazıyor (`gpt-5.6-sol`, `deepseek-v4.1-flash`...). Aktif
sağlayıcı 9Router olduğu için o isimlerin karşılığı yoktu → 503 → sohbet
"Düşünüyor" ekranında takılıyordu.

Çözüm (kuruldu): 9Router'da o 14 isme **takma ad** açıldı; her biri CANLI bir
modele bağlandı. Kanıt: `scripts/codex_gui_takma_ad.py --test` → 14/14 cevap verdi.
Yani masaüstü listesinden istediğini seçebilirsin.

En hızlı yol yine komutla seçimdir (Codex'i kapat-aç gerektirmez):
"""
    # Eski 'ONEMLI' blogunu (SONUC satirina kadar) degistir
    desen = re.compile(r"## ÖNEMLİ .*?\*\*SONUÇ: GUI listesinden seçim yapma\. Modeli tek komutla değiştir:\*\*",
                       re.S)
    yeni, n = desen.subn(yeni_baslik, metin, count=1)
    if n == 0:
        print("MD: desen bulunamadi — dosya degistirilmedi")
        return
    MD.write_text(yeni, encoding="utf-8")
    geri = MD.read_text(encoding="utf-8")
    print("MD: guncellendi · 'ARTIK GÜVENLİ' var mi:", "ARTIK GÜVENLİ" in geri)
    print("MD: eski yasak satiri kaldi mi:", "seçim yapma" in geri)


if __name__ == "__main__":
    betik_esitle()
    print()
    md_guncelle()
