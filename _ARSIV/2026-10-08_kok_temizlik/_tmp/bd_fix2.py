# -*- coding: utf-8 -*-
"""Tek kullanimlik: bulgu_defteri.md kalan bozuk satirlari 6 alana cek (TEST-BACKLOG-CI-01-a).
Kural: ilk 4 alan sabit; son parca = karar; aradaki fazla '|' -> ' / ' (metin korunur, ayirici degil).
"""
import io
P = r"data/orchestrator/bulgu_defteri.md"
raw = io.open(P, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in raw else "\n"
L = raw.split(nl)
ETIKET = {  # renk alanina yazilmis etiketler -> (emoji, ozet oneki)
    "YENI-BULGU (commit-msg mandali)": "🟡",
    "CANLI-DOGRULAMA": "🔵",
    "PANO-BULGU": "🟡",
    "KAPI-OLCUM-KIRMIZI": "🔴",
    "DUZELTILDI (ARCHITECTURE cikis kapisi)": "🟢",
}
EMOJI = set("🔴🟡🟢🔵")
BILGI_KARAR = "bilgi kaydi, karar gerekmedi (6 alan TEST-BACKLOG-CI-01-a ile tamamlandi)"
n = 0
for i, s in enumerate(L):
    if not s[:4].isdigit():
        continue
    a = [x.strip() for x in s.split("|")]
    if len(a) == 6 and a[3] in EMOJI:
        continue
    if a[3] in ETIKET:
        a[4] = f"{a[3]}: {a[4]}"
        a[3] = ETIKET[a[3]]
    if len(a) == 5:
        if " ORKESTRATOR KARARI: " in a[4]:
            oz, kr = a[4].split(" ORKESTRATOR KARARI: ", 1)
            a = a[:4] + [oz.strip(), "ORKESTRATOR KARARI: " + kr]
        else:
            a.append(BILGI_KARAR)
    elif len(a) > 6:
        a = a[:4] + [" / ".join(a[4:-1]), a[-1]]
    assert len(a) == 6 and a[3] in EMOJI and a[5], (i + 1, a[:4])
    L[i] = " | ".join(a)
    n += 1
    print(i + 1, L[i][:80])
io.open(P, "w", encoding="utf-8", newline="").write(nl.join(L))
print("duzeltilen:", n)
