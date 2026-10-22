"""ORTAK_TASARIM onarim: stash(temiz, yerel ekler) taban + bilo'nun duzeltilmis 4.8.C bolumu (tek kopya).
Kullanim: ortak_onar.py [--yaz]   (varsayilan: yalniz olc, _tmp/ortak_onarilmis.md'ye yazar)
Ayrica messages.jsonl tekrar olcumu (yazmaz).
"""
import subprocess as s, re, sys, json

F = "docs/MUSTERI_PANEL_ORTAK_TASARIM.md"


def blob(rev):
    r = s.run(["git", "show", f"{rev}:{F}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace")


def ters(t):
    out = []
    for ln in t.split("\n"):
        k = ln
        for _ in range(3):
            if not any(c in k for c in "\u00c2\u00c3\u00e2"):
                break
            try:
                k = k.encode("cp1252").decode("utf-8")
            except Exception:
                try:
                    k = k.encode("latin-1").decode("utf-8")
                except Exception:
                    break
        out.append(k)
    return "\n".join(out)


def bolum(t, bas_re, son_re):
    """ilk bas_re eslesmesinden, sonraki son_re eslesmesine kadar (son haric)."""
    m = re.search(bas_re, t, re.M)
    if not m:
        return None
    n = re.search(son_re, t[m.end():], re.M)
    bit = m.end() + n.start() if n else len(t)
    return m.start(), bit


taban = blob("stash@{0}")
bilo = ters(blob("HEAD"))
BAS = r"^#### 4\.8\.C"
SON = r"^### 4\.8b"
yb = bolum(bilo, BAS, SON)
yt = bolum(taban, BAS, SON)
print("bilo(HEAD ters, ilk kopya) 4.8.C satir araligi:", bilo[:yb[0]].count("\n") + 1, "-", bilo[:yb[1]].count("\n"))
print("taban(stash) 4.8.C satir araligi:", taban[:yt[0]].count("\n") + 1, "-", taban[:yt[1]].count("\n"))
yeni_bolum = bilo[yb[0]:yb[1]]
sonuc = taban[:yt[0]] + yeni_bolum + taban[yt[1]:]
print("sonuc satir", sonuc.count("\n"),
      "moji", sum(1 for l in sonuc.split("\n") if "\u00c3" in l or "\u00c2" in l),
      "4.8b", len(re.findall(r"^### 4\.8b", sonuc, re.M)),
      "4.8.C", len(re.findall(r"^#### 4\.8\.C", sonuc, re.M)),
      "marker", len(re.findall(r"^(<<<<<<<|>>>>>>>)", sonuc, re.M)),
      "rontend/ode_modules bozuk", len(re.findall(r"(?<![a-z/])(rontend-ui|rowser-testing|ode_modules/recharts)", sonuc)))
# bilo'nun HEAD'de baska yerde de degisiklik var mi? ters-HEAD ilk kopya disinda kalan fark
import difflib
eski = blob("d5299819")
d = [x for x in difflib.unified_diff(eski.split("\n"), sonuc.split("\n"), lineterm="", n=0)
     if x[:1] in "+-" and x[:3] not in ("+++", "---")]
print("d5299819 -> sonuc: degisen satir", len(d))
out = "_tmp/ortak_onarilmis.md"
open(out if "--yaz" not in sys.argv else F, "w", encoding="utf-8", newline="\n").write(sonuc)
print("yazildi:", out if "--yaz" not in sys.argv else F)

# messages.jsonl tekrar
seen, tot, uniq = set(), 0, []
with open("data/orchestrator/chat/messages.jsonl", encoding="utf-8-sig") as f:
    for l in f:
        if not l.strip():
            continue
        tot += 1
        try:
            o = json.loads(l)
        except Exception:
            uniq.append(l); continue
        k = (o.get("tarih"), o.get("kimden"), o.get("kime"), o.get("type"), o.get("task_id"), o.get("mesaj"))
        if k in seen:
            continue
        seen.add(k); uniq.append(l)
print("messages.jsonl toplam", tot, "benzersiz", len(uniq))
