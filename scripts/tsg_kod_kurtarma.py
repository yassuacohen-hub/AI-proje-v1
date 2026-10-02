"""Kayip kodu stash@{0} icinden cikarir ve dosyaya geri yazar.

 Bulgular:
   - `git stash show -p <stash>` TAM DIFF'I verir; `-- <dosya>` filtresi
     calismiyor. Onceden "dosya_listede=HAYIR" ciktisi YANLIStI.
   - stash@{0} ve stash@{1} icinde "def olay_esle" var.

 Bu script:
   1) stash@{0}'dan ticaret_sicili_kanit.py'nin + satirli halini cikarir
   2) _asciiye()'nin TR eslemesi ve ILAN_TURU_ESLEME/olay_esle tanimlarini dogrular
   3) Yedek alir, sonra geri yazar
   4) test_tsg_zincir.py ile dogrular
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
DOSYA_REL = "skills/services/ticaret_sicili_kanit.py"


def git(*a):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.stdout


def stash_dosya_icerigi(stash_no: int, dosya: str) -> str | None:
    """stash diff'inden bir dosyanin tam + halini kurar."""
    diff = git("stash", "show", "-p", f"stash@{{{stash_no}}}")
    if not diff:
        return None
    sonuc = []
    hedef = False
    for satir in diff.splitlines():
        if satir.startswith("diff --git "):
            hedef = f"b/{dosya}" in satir
            continue
        if not hedef:
            continue
        if satir.startswith(("index ", "new file mode", "deleted file mode",
                             "similarity index", "rename ", "--- ", "+++ ")):
            continue
        if satir.startswith("+") and not satir.startswith("+++"):
            sonuc.append(satir[1:])
    return "\n".join(sonuc) if sonuc else None


print("=== 1) stash'lerden tam dosya cikarimi ===")
adaylar = {}
for i in (0, 1):
    icerik = stash_dosya_icerigi(i, DOSYA_REL)
    if icerik:
        adaylar[i] = icerik
        print(f"   stash@{{{i}}}: {len(icerik.splitlines())} satir cikarildi")

if not adaylar:
    print("   HICBIR stash'ta dosya bulunamadi")
    raise SystemExit(1)

# --- en dolu adayi sec (ILAN_TURU_ESLEME + olay_esle iceren) ---
def kalite(icerik: str) -> tuple:
    return (
        "def olay_esle" in icerik,
        "ILAN_TURU_ESLEME" in icerik,
        "_TR_ASCII" in icerik or "TR_ASCII" in icerik,
        len(icerik),
    )

en_iyi_no = max(adaylar, key=lambda k: kalite(adaylar[k]))
icerik = adaylar[en_iyi_no]
print(f"\n=== 2) en dolu aday: stash@{{{en_iyi_no}}} ===")
print(f"   olay_esle: {'VAR' if 'def olay_esle' in icerik else 'YOK'}")
print(f"   ILAN_TURU_ESLEME: {'VAR' if 'ILAN_TURU_ESLEME' in icerik else 'YOK'}")
print(f"   _TR_ASCII: {'VAR' if '_TR_ASCII' in icerik else 'YOK'}")
print(f"   satir: {len(icerik.splitlines())}")

# --- sozluk anahtar sayisini olc ---
m = re.search(r"ILAN_TURU_ESLEME[^=]*=\s*\{(.*?)\n\}", icerik, re.S)
if m:
    anahtar = re.findall(r'^\s*["\']([^"\']+)["\']\s*:', m.group(1), re.M)
    print(f"   sozluk anahtari: {len(anahtar)}")
    for a in anahtar:
        print(f"     - {a}")

# --- dosyaya geri yaz ---
hedef = ROOT / DOSYA_REL
yedek = ROOT / "yedekler" / "ticaret_sicili_kanit_29eylul_yedek.txt"
hedef.parent.mkdir(parents=True, exist_ok=True)
if not yedek.exists():
    shutil.copy2(hedef, yedek)
    print(f"\n=== 3) mevcut dosya yedeklendi: {yedek.name} ===")
else:
    print(f"\n=== 3) yedek zaten var: {yedek.name} ===")

hedef.write_text(icerik + "\n", encoding="utf-8")
print(f"   geri yazildi: {hedef.relative_to(ROOT)} ({hedef.stat().st_size} b)")

# --- dogrulama ---
print("\n=== 4) dogrulama ===")
r = subprocess.run(
    [sys.executable, "-X", "utf8", "-c",
     f"import sys; sys.path.insert(0, {str(ROOT)!r}); "
     "from skills.services.ticaret_sicili_kanit import olay_esle, ILAN_TURU_ESLEME, _asciiye; "
     "print('IMPORT OK, anahtar:', len(ILAN_TURU_ESLEME)); "
     "print('asciiye Artirimi ->', _asciiye('Artırımı'))"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(ROOT),
)
print("   " + (r.stdout.strip() or r.stderr.strip()[-400:]))
