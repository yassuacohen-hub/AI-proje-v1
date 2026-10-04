"""'Hiç yazılmadı' iddiasını test eder.

İddia: ILAN_TURU_ESLEME / olay_esle hiç yazılmadı, dosya 29 Eylül'den beri
aynı.

Test edilecek 3 bağımsız olgu:
  A) Dosya calisma agacinda HEAD ile ayni mi? (git status)
  B) Git'teki hicbir commit/stash icinde "def olay_esle" var mi?
  C) Canli DB'deki event_type degerleri, olay_esle'in uretecegi degerler mi?
     (Bunu koda BAKMADAN dogrular: DB dolu satirlar kanit dosyalariyla
      il_turu uzerinden eslestirilir ve slug kurali denetlenir.)
"""

import json
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
DOSYA = "skills/services/ticaret_sicili_kanit.py"


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


print("=== A) dosya calisma agacinda mi degisti ===")
st = git("status", "--porcelain", "--", DOSYA).strip()
print(f"   git status: {st or '(bos = dosya HEAD ile BIREBIR ayni)'}")
print(f"   son commit: {git('log', '-1', '--format=%h %ad %s', '--date=short', '--', DOSYA).strip()}")

print("\n=== B) 'def olay_esle' git'in herhangi bir yerinde mi ===")
n = git("log", "--all", "--oneline", "-S", "def olay_esle", "--", DOSYA).strip()
print(f"   commitlerde: {n or 'YOK'}")
for i in range(8):
    p = git("stash", "show", "-p", f"stash@{{{i}}}")
    if "def olay_esle" in p:
        print(f"   stash@{{{i}}}: *** 'def olay_esle' ICERIYOR ***")
p = git("fsck", "--no-reflogs", "--lost-found")
dangling = [l for l in p.splitlines() if "dangling blob" in l]
print(f"   askida blob: {len(dangling)}")

print("\n=== C) canli DB: event_type degerleri olay_esle'in ciktilari mi ===")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from sqlalchemy import create_engine, text  # noqa: E402

url = next(
    (l.split("=", 1)[1].strip() for l in (ROOT / ".env").read_text(
        encoding="utf-8").splitlines() if l.strip().startswith("DATABASE_URL=")),
    None,
)
eng = create_engine(url, pool_pre_ping=True)
with eng.connect() as c:
    dolu = c.execute(text(
        "select event_type, direction, count(*) from company_events "
        "where event_type is not null and event_type<>'' group by 1,2"
    )).fetchall()

print(f"   event_type dolu grup: {len(dolu)}")
for et, dr, adet in dolu:
    print(f"     {et:26} / {dr:10} -> {adet} satir")

# slug kurali: ASCII'ye indir, buyut, bosluk -> _
def slug(m):
    s = unicodedata.normalize("NFKD", m).encode("ascii", "ignore").decode()
    return "_".join(s.upper().replace("-", " ").split()).lower()

# kanittaki il_turu'lari oku
kanit_tur = Counter()
for p in sorted((ROOT / "data" / "kanit").rglob("*.json")):
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        continue
    t = (d.get("il_turu") or "").strip()
    if t:
        kanit_tur[t] += 1

print(f"\n   kanittaki benzersiz il_turu: {len(kanit_tur)}")
db_slugleri = {et for et, _, _ in dolu}
kanit_slugleri = {slug(t) for t in kanit_tur}
ortus = db_slugleri & kanit_slugleri
print(f"   DB event_type ∩ kanit slug = {len(ortus)}/{len(db_slugleri)}")
print(f"   kesisenler: {sorted(ortus)}")
only_db = sorted(db_slugleri - kanit_slugleri)
print(f"   sadece DB'de (kanitta yok): {only_db}")

print("\n=== SONUC ===")
if len(ortus) == len(db_slugleri):
    print("   DB'deki her event_type, kanittaki bir il_turu'nun slug'i.")
    print("   Bu degerleri SADECE olay_esle uretebilir -> kod calisti.")
else:
    print("   Kismi eslesme; daha inceleme gerekir.")
