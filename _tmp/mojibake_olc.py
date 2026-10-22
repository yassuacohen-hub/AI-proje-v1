"""ORTAK_TASARIM mojibake olcumu: HEAD blob tersine cevrilebilir mi? Diske yalniz _tmp'ye yazar."""
import subprocess as s, difflib, sys

F = "docs/MUSTERI_PANEL_ORTAK_TASARIM.md"
CWD = "."


def blob(rev):
    return s.run(["git", "show", f"{rev}:{F}"], capture_output=True, cwd=CWD).stdout.decode("utf-8", "replace")


def ters(t):
    """Satir satir: cp1252/latin-1 -> utf-8 geri cevir; olmayan satiri oldugu gibi birak."""
    out, n = [], 0
    for ln in t.split("\n"):
        k = ln
        for _ in range(3):
            if not any(c in k for c in "\u00c2\u00c3\u00e2"):
                break
            try:
                k2 = k.encode("cp1252", "strict").decode("utf-8", "strict")
            except Exception:
                try:
                    k2 = k.encode("latin-1", "strict").decode("utf-8", "strict")
                except Exception:
                    break
            k = k2
        if k != ln:
            n += 1
        out.append(k)
    return "\n".join(out), n


eski = blob("d5299819")
yeni = blob("HEAD")
duz, n = ters(yeni)
print("HEAD bozuk->duzeltilen satir:", n)
kalan = sum(1 for ln in duz.split("\n") if "\u00c3" in ln or "\u00c2" in ln)
print("duzeltme sonrasi hala Ã/Â iceren satir:", kalan)
d = list(difflib.unified_diff(eski.split("\n"), duz.split("\n"), lineterm="", n=0))
ek = sum(1 for x in d if x.startswith("+") and not x.startswith("+++"))
sil = sum(1 for x in d if x.startswith("-") and not x.startswith("---"))
print("d5299819 ile duzeltilmis HEAD farki: +%d -%d" % (ek, sil))
open("../_tmp/ortak_duz.md", "w", encoding="utf-8", newline="\n").write(duz)
print("yazildi: _tmp/ortak_duz.md")
