# -*- coding: utf-8 -*-
"""Claude Desktop'in `inferenceModels` KAYIT SEMASINI uygulama kodundan bulur.
Neden: yanlis alan adi yazarsam uygulama ayari gecersiz sayabilir -> PO hic model
goremez. Elindeki tek kanitli sekil: {name, anthropicFamilyTier, maxEffort}.
Yontem: app.asar icinde 'anthropicFamilyTier' gecen yerleri + cephelerini bas.
Anahtar degeri YOK (kod dosyasi), yine de desen maskesi uygulanir (D-380)."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path.home() / "AppData/Local"
DESEN = re.compile(r"(sk-[A-Za-z0-9\-]{10,}|nvapi-[A-Za-z0-9\-]{10,})")

adaylar = []
for ad in ("claude-desktop", "Claude", "Claude-3p", "Programs"):
    d = KOK / ad
    if d.exists():
        adaylar += list(d.rglob("app.asar"))
if not adaylar:
    print("app.asar bulunamadi; aday dizinler:", [str(a) for a in adaylar])
    for d in (KOK / "Programs", KOK):
        if d.exists():
            print("  icerik:", [p.name for p in d.iterdir()][:15])
    raise SystemExit(0)

for asar in adaylar[:3]:
    print(f"\n########## {asar} ({asar.stat().st_size/1e6:.1f} MB) ##########")
    ham = asar.read_bytes().decode("latin-1", "replace")
    for anahtar in ("anthropicFamilyTier", "inferenceModels"):
        yerler = [m.start() for m in re.finditer(anahtar, ham)]
        print(f"  '{anahtar}': {len(yerler)} gecis")
        for y in yerler[:4]:
            parca = DESEN.sub("…MASKELI", ham[max(0, y - 260):y + 320])
            parca = " ".join(parca.split())
            print(f"    …{parca}…\n")
