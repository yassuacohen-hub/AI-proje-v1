"""Bulgu defteri kararı için ölçüm: teslimlerde bulgu kapsamı nedir?

D-224: "her teslim bulgu yazıyor" iddiası tahmindir; sayılır.
"""

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = Path(__file__).resolve().parent.parent
ORCH = KOK / "data" / "orchestrator"

# --- 1) Teslim kayıtları ---
kuyruk = json.loads((ORCH / "onay_kuyrugu.json").read_text(encoding="utf-8"))
kayitlar = kuyruk if isinstance(kuyruk, list) else kuyruk.get("kuyruk", [])
print(f"onay_kuyrugu kaydi: {len(kayitlar)}")
ciktili = [k for k in kayitlar if k.get("ciktilar")]
print(f"  --cikti dolu olan: {len(ciktili)}  ({100*len(ciktili)/len(kayitlar):.0f}%)")

# --- 2) Teslim raporlarında ## Bulgular bölümü ---
def raporlar(tur: str) -> list[Path]:
    return sorted((ORCH).glob(f"*{tur}*.md"))


def bolum_var(p: Path, ad: str) -> bool:
    try:
        t = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return re.search(rf"^##\s+{re.escape(ad)}", t, re.M | re.I) is not None


for tur, etiket in (("rapor", "rapor"), ("bulgular", "bulgular")):
    dosyalar = raporlar(tur)
    if not dosyalar:
        print(f"{tur}: 0 dosya")
        continue
    bulgulu = [d for d in dosyalar if bolum_var(d, "Bulgular")]
    bos = [
        d.name for d in bulgulu
        if re.search(r"Bulgu yok", d.read_text(encoding="utf-8"), re.I)
    ]
    print(
        f"{tur} dosyasi: {len(dosyalar)} | '## Bulgular' bolumu olan: "
        f"{len(bulgulu)} | icinde 'Bulgu yok' yazan: {len(bos)}"
    )

# --- 3) Bulgu defteri şu an ---
defter = ORCH / "bulgu_defteri.md"
if defter.exists():
    satirlar = [l for l in defter.read_text(encoding="utf-8").splitlines() if l.strip().startswith("|") is False and "|" in l]
    print(f"\nbulgu_defteri.md: VAR, {len(satirlar)} kayit satiri")
    for s in satirlar:
        parca = [p.strip() for p in s.split("|")]
        print(f"  {parca[0]} {parca[1]} {parca[3] if len(parca)>3 else ''} -> {parca[-1][:50]}")
else:
    print("\nbulgu_defteri.md: YOK")

# --- 4) Ajana özel bulgu defteri var mı? ---
defterler = sorted(p for p in KOK.rglob("bulgu*defter*") if p.is_file())
print(f"\nproje genelinde bulgu defteri dosyasi: {len(defterler)}")
for p in defterler[:10]:
    print(f"  {p.relative_to(KOK)}")

# --- 5) D-67 kuralı gerçekten zorlanıyor mu? ---
kural = (KOK / "AGENTS.md").read_text(encoding="utf-8")
i = kural.find("Bulgu İşleme Zorunluluğu")
print(f"\nAGENTS.md 'Bulgu Isleme Zorunluluğu' bolumu: {'VAR' if i>0 else 'YOK'}")
for satir in kural[i : i + 700].splitlines():
    if "görev" in satir.lower() or "karar" in satir.lower() or "Reddet" in satir:
        print("   ", satir.strip()[:120])

# --- 6) teslim komutu bulgu defterini kontrol ediyor mu? ---
kutu = (KOK / "scripts" / "gorev_kutusu.py").read_text(encoding="utf-8")
i = kutu.find("def cmd_teslim")
govde = kutu[i : i + 2000]
print(f"\ncmd_teslim icinde 'bulgu_defteri' geciyor mu: {'bulgu_defteri' in govde}")
print(f"cmd_teslim icinde zorunlu argümanlar: ozet={('--ozet' in govde)} cikti={('--cikti' in govde)}")
