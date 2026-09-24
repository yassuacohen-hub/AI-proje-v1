# -*- coding: utf-8 -*-
"""web_app.py 3. duzeltme: SOFT setini kisaltilmis formlara daralt;
LIMITED gibi sirket turu kelimelerini HARD'a ekle."""
from pathlib import Path

p = Path(r"C:\Projeler\Huginn Data Insights\web_app.py")
src = p.read_text(encoding="utf-8")

old_hard = """    'STI.', 'STI', 'ŞTI.', 'ŞTI', 'SIRKETI', 'SIRKET', 'ANONIM', 'ANONIM ŞIRKETI',
    'ORT.', 'ORT', 'ORTAKLIK', 'KOL. ŞTI.', 'KOM. ŞTI.', 'KOOP.', 'KOOP',
    'KOLLEKTIF', 'KOMANDIT', 'TAS', 'TAO', 'DTM', 'KOBI',
})"""
new_hard = """    'STI.', 'STI', 'ŞTI.', 'ŞTI', 'SIRKETI', 'SIRKET', 'ANONIM', 'ANONIM ŞIRKETI',
    'LIMITED', 'LTD SIRKETI', 'LIMITED SIRKETI',
    'ORT.', 'ORT', 'ORTAKLIK', 'KOL. ŞTI.', 'KOM. ŞTI.', 'KOOP.', 'KOOP',
    'KOLLEKTIF', 'KOMANDIT', 'TAS', 'TAO', 'DTM', 'KOBI',
})"""
assert old_hard in src, "hard blok yok"
src = src.replace(old_hard, new_hard)

start = src.find("_TRADE_NAME_STOP_SOFT = frozenset({")
end = src.find("})\n", start) + 3
assert start != -1, "soft blok yok"

new_soft = """_TRADE_NAME_STOP_SOFT = frozenset({
    # Yalnizca KISALTILMIS faaliyet formlari (tabela adinda yer kaplamasin);
    # tam kelimeler (ELEKTRIK, INSAAT, MUHENDISLIK...) korunur (Kural 3 ornegi:
    # "DÜNDAR ELEKTRİK SANAYİ" -> "DÜNDAR ELEKTRİK").
    'PAZ.', 'PAZ', 'ITH.', 'ITH', 'IHR.', 'IHR', 'MUH.', 'MUH', 'MIM.', 'MIM',
    'İNŞ.', 'INS.', 'INS', 'INŞ', 'NAK.', 'NAK', 'OTO.', 'OTO',
    'TUR.', 'TUR', 'TEK.', 'TEK', 'HIZM.', 'HIZM', 'TAR.', 'TAR', 'MAD.', 'MAD',
    'IMAL.', 'IMAL', 'BIL.', 'BIL', 'YAZ.', 'YAZ', 'MAK.', 'MAK', 'MOB.', 'MOB',
    'ELEK.', 'ELEK', 'KIM.', 'KIM', 'GIDA',
})
"""
src = src[:start] + new_soft + src[end:]

p.write_text(src, encoding="utf-8", newline="")
print("web_app.py 3. duzeltme uygulandi")
