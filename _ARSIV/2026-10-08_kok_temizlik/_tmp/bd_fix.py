# -*- coding: utf-8 -*-
"""Tek kullanimlik: bulgu_defteri.md bozuk satirlari 6 alana cek (TEST-BACKLOG-CI-01-a)."""
import io, re, sys
P = r"c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\bulgu_defteri.md"
with io.open(P, encoding="utf-8", newline="") as f:
    raw = f.read()
nl = "\r\n" if "\r\n" in raw else "\n"
L = raw.split(nl)
EMO = {"COZULDU": "🟢", "yari": "🟡", "mavi": "🔵", "yesil": "🟢"}

def fix(s):
    a = s.split(" | ")
    if len(a) >= 4 and a[3] in EMO:
        a[3] = EMO[a[3]]
    s = " | ".join(a)
    if s.endswith(" |"):
        s = s[:-2].rstrip()
    if s.endswith(" | "):
        s = s[:-3].rstrip()
    if s.count(" | ") == 4 and " Cozum: " in s:
        k = s.rfind(" Cozum: ")
        s = s[:k] + " | Cozum: " + s[k + 8:]
    return s

# 116: COZULDU + 7. alan 'bkz. rapor'
i = 115
assert L[i].startswith("2026-10-03 | SCRAPE-005-KAZIMA-DOCKER-INTEGRATION"), L[i][:60]
L[i] = fix(L[i].replace(". | bkz. rapor:", "; bkz. rapor:"))
# 154+155 birlestir
assert L[153].startswith("2026-10-04 | UI-ADMIN-ACIKLAMA-METIN-37 | utku | yesil"), L[153][:60]
assert L[154].startswith("ender_topbar"), L[154][:30]
L[153] = L[153].rstrip() + " " + L[154].strip()
L[153] = L[153].replace(" degisti. Test :207", " degisti. | Test :207")
del L[154]
for i in (145, 146, 147, 148, 150, 152, 153):
    L[i] = fix(L[i])
for i in (115, 145, 146, 147, 148, 150, 152, 153):
    n = L[i].count(" | ")
    print(i + 1, n, L[i][:70])
    assert n == 5, (i + 1, n)
with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(nl.join(L))
print("OK")
