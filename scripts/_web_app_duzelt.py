# -*- coding: utf-8 -*-
"""web_app.py kurallari duzelt (Turkce duyarsiz kisaltma + stop words)."""
from pathlib import Path

p = Path(r"C:\Projeler\Huginn Data Insights\web_app.py")
src = p.read_text(encoding="utf-8")

# 1) Oluk pre-compiled tanimlari kaldir (52-59 civari)
old_block = "_RE_MULTI_SPACE = _re.compile"
idx = src.find(old_block)
assert idx != -1, "eski blok bulunamadi"
# blok baslangici: '# Pre-compiled' yorum satirina kadar git
comment_idx = src.rfind("# Pre-compiled", 0, idx)
end_marker = "_COMPANY_TYPE_ABBR = {"
end_idx = src.find(end_marker)
assert end_idx != -1, "bitis bulunamadi"
# tanimdan onceki yorum satirini da atla: iki satir yukaridaki satir basina git
end_idx = src.rfind("\n", 0, src.rfind("\n", 0, end_idx)) + 1
new_block = """# Turkce duyarsiz eslesme: kural 2 kisaltmalari ASCII tanimli; girdideki
# Turkce harfler (I noktali/ciftesleri) de eslesmeli.
_TR_INSENSITIVE_CLS = {'I': '[İI]', 'C': '[ÇC]', 'G': '[ĞG]', 'O': '[ÖO]', 'U': '[ÜU]', 'S': '[ŞS]'}


def _tr_insensitive(escaped: str) -> str:
    \"\"\"_re.escape() sonrasi pattern'i Turkce harf duyarsiz yapar.\"\"\"
    out = []
    i = 0
    while i < len(escaped):
        ch = escaped[i]
        if ch == '\\\\' and i + 1 < len(escaped):
            out.append(escaped[i:i + 2])
            i += 2
            continue
        out.append(_TR_INSENSITIVE_CLS.get(ch, ch))
        i += 1
    return ''.join(out)


def _tr_rx(phrase: str) -> str:
    \"\"\"Kelime sinirlu + Turkce duyarsiz regex uretir.\"\"\"
    return r'(?<!\\w)' + _tr_insensitive(_re.escape(phrase)) + r'(?![\\w.])'


"""
src = src[:comment_idx] + new_block + src[end_idx:]

# 2) Combo replace -> duyarsiz regex
old = """    for long_phrase, short_form in sorted(_COMBO_ABBR.items(), key=lambda x: -len(x[0])):
        name = name.replace(long_phrase, short_form)"""
new = """    for long_phrase, short_form in sorted(_COMBO_ABBR.items(), key=lambda x: -len(x[0])):
        name = _re.sub(_tr_rx(long_phrase), short_form, name)"""
assert old in src, "combo blok yok"
src = src.replace(old, new)

# 3) Activity + company_type sub -> _tr_rx
old = """    for long_phrase, short_form in sorted(_ACTIVITY_ABBR.items(), key=lambda x: -len(x[0])):
        name = _re.sub(r'(?<!\\w)' + _re.escape(long_phrase) + r'(?![\\w.])', short_form, name)
    
    for long_phrase, short_form in sorted(_COMPANY_TYPE_ABBR.items(), key=lambda x: -len(x[0])):
        name = _re.sub(r'(?<!\\w)' + _re.escape(long_phrase) + r'(?![\\w.])', short_form, name)"""
new = """    for long_phrase, short_form in sorted(_ACTIVITY_ABBR.items(), key=lambda x: -len(x[0])):
        name = _re.sub(_tr_rx(long_phrase), short_form, name)

    for long_phrase, short_form in sorted(_COMPANY_TYPE_ABBR.items(), key=lambda x: -len(x[0])):
        name = _re.sub(_tr_rx(long_phrase), short_form, name)"""
assert old in src, "activity/company blok yok"
src = src.replace(old, new)

# 4) Stop words: GIDA cikar + noktasiz varyantlar ekle
old = """_TRADE_NAME_STOP_WORDS = frozenset({
    'VE', 'ILE', 'BI', 'AMMA', 'LAKIK',
    'SAN.', 'SANAYI', 'SANAYII', 'TIC.', 'TICARET', 'TICARETI',
    'LTD. ŞTI.', 'LTD. STI.', 'LTD.', 'LTD', 'A.S.', 'A.S', 'A.Ş.', 'A.Ş',
    'STI.', 'STI', 'ŞTI.', 'ŞTI', 'ORT.', 'ORT', 'KOL. ŞTI.', 'KOM. ŞTI.', 'KOOP.',
    'PAZ.', 'ITH.', 'IHR.', 'MUH.', 'MIM.', 'İNŞ.', 'INS.', 'NAK.', 'OTO.',
    'TUR.', 'TEK.', 'GIDA', 'HIZM.', 'TAR.', 'MAD.', 'IMAL.',
    'BIL.', 'YAZ.', 'MAK.', 'MOB.', 'ELEK.', 'KIM.',
    'KOOP', 'TAS', 'TAO', 'DTM', 'KOBI',
})"""
new = """_TRADE_NAME_STOP_WORDS = frozenset({
    'VE', 'ILE', 'BI', 'AMMA', 'LAKIK',
    'SAN.', 'SAN', 'SANAYI', 'SANAYII', 'TIC.', 'TIC', 'TICARET', 'TICARETI',
    'LTD. ŞTI.', 'LTD. STI.', 'LTD.', 'LTD', 'A.S.', 'A.S', 'A.Ş.', 'A.Ş',
    'STI.', 'STI', 'ŞTI.', 'ŞTI', 'ORT.', 'ORT', 'KOL. ŞTI.', 'KOM. ŞTI.', 'KOOP.',
    'PAZ.', 'PAZ', 'ITH.', 'ITH', 'IHR.', 'IHR', 'MUH.', 'MUH', 'MIM.', 'MIM',
    'İNŞ.', 'INS.', 'INS', 'INŞ', 'NAK.', 'NAK', 'OTO.', 'OTO',
    'TUR.', 'TUR', 'TEK.', 'TEK', 'HIZM.', 'HIZM', 'TAR.', 'TAR', 'MAD.', 'MAD',
    'IMAL.', 'IMAL', 'BIL.', 'BIL', 'YAZ.', 'YAZ', 'MAK.', 'MAK', 'MOB.', 'MOB',
    'ELEK.', 'ELEK', 'KIM.', 'KIM', 'GIDA', 'GID', 'GIDA.',
    'KOOP', 'TAS', 'TAO', 'DTM', 'KOBI',
})"""
assert old in src, "stop words blok yok"
src = src.replace(old, new)

p.write_text(src, encoding="utf-8", newline="")
print("web_app.py guncellendi")
