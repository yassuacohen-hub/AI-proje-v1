# -*- coding: utf-8 -*-
"""Claude Desktop 'Configure third-party inference' ayar DOSYASINI maskeli okur.
Bulunan yol: %LOCALAPPDATA%\\Claude-3p\\configLibrary\\<id>.json
D-380: anahtar/token/parola desenleri MASKELI basilir (gecen turda maskelemeyi
unuttum ve anahtarlar terminale duşti - tekrarlanmayacak)."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DIZIN = Path.home() / "AppData/Local/Claude-3p/configLibrary"

DESEN = re.compile(
    r"(sk-[A-Za-z0-9\-]{6,}|nvapi-[A-Za-z0-9\-]{6,}|eyJ[A-Za-z0-9_\-]{6,}|"
    r"ya29\.[A-Za-z0-9_\-]{6,}|ghu_[A-Za-z0-9]{6,}|castai_[A-Za-z0-9]{6,}|"
    r"workos:[A-Za-z0-9._\-]{6,}|aoaAAAA[A-Za-z0-9_\-]{6,}|cfut_[A-Za-z0-9]{6,}|"
    r"\$2b\$10\$[A-Za-z0-9./]{8,})")
HASSAS = ("key", "token", "secret", "password", "credential", "apikey")


def maske(anahtar: str, deger):
    s = deger if isinstance(deger, str) else json.dumps(deger, ensure_ascii=False)
    s = DESEN.sub(lambda m: m.group(1)[:7] + "…MASKELI", s)
    if any(x in anahtar.lower() for x in HASSAS) and isinstance(deger, str) and len(deger) > 10:
        s = f"***{deger[-4:]} ({len(deger)}b)"
    return s if len(s) <= 240 else s[:240] + f"…({len(s)}b)"


def yaz(o, derin=0):
    gir = "  " * derin
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, dict) and derin < 4:
                print(f"{gir}{k}:")
                yaz(v, derin + 1)
            elif isinstance(v, list) and derin < 4:
                print(f"{gir}{k}: (liste {len(v)})")
                for i, e in enumerate(v[:8]):
                    if isinstance(e, dict):
                        print(f"{gir}  [{i}] " + " · ".join(
                            f"{kk}={maske(kk, vv)}" for kk, vv in e.items()))
                    else:
                        print(f"{gir}  [{i}] {maske(k, e)}")
            else:
                print(f"{gir}{k} = {maske(k, v)}")


if not DIZIN.exists():
    raise SystemExit(f"DIZIN YOK: {DIZIN}")
for p in sorted(DIZIN.glob("*.json")):
    print(f"\n########## {p.name} ({p.stat().st_size}b) ##########")
    try:
        yaz(json.loads(p.read_text(encoding="utf-8")))
    except Exception as e:  # noqa: BLE001
        print("  okunamadi:", str(e)[:80])
