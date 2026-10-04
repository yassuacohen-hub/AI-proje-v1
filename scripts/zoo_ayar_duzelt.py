# -*- coding: utf-8 -*-
"""Zoo Code (VS Code) izin/yasak komut listesini sadelestir (KAHIN 2026-10-03).

Sorun: `zoo-code.allowedCommands` 193 adet tam-komut kaydi tasiyordu
(uzun python -c / powershell satirlari). Prefix eslesmesi tutmayinca her
yeni komut onay istiyordu. `deniedCommands` bostu.

Cozum: ~12 kisa prefix + 6 tehlikeli yasak. Dosya yedeklenir, sonra
json olarak yeniden yazilir (JSONC yorumlari yoksa). Yorum varsa yalniz
iki liste degistirilir (metin bazli).

Kullanim:  python scripts/zoo_ayar_duzelt.py [--kuru]

ponytail: VS Code settings.json tek kaynak; Zoo'nun kendi UI onay
anahtarlari (auto-approve toggles) buradan yazilmaz, kullanici tikler.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import shutil
import sys
from pathlib import Path

IZINLI: list[str] = [
    "python", "python -m pytest", "pytest", "git status", "git diff",
    "git log", "git show", "git add", "git commit", "dir", "findstr",
    "type", "powershell -NoProfile", "docker compose", "schtasks", "set",
]
YASAK: list[str] = [
    "--no-verify", "git reset --hard", "git push --force", "git push -f",
    "git clean", "rmdir /s", "del /s", "rd /s", "Remove-Item -Recurse",
    "format", "git checkout -- .",
]


def ayar_yolu() -> Path:
    return Path(os.environ["APPDATA"]) / "Code" / "User" / "settings.json"


def _yorum_var(metin: str) -> bool:
    return bool(re.search(r"^\s*//", metin, flags=re.M))


def duzelt(yol: Path, kuru: bool = False) -> dict:
    metin = yol.read_text(encoding="utf-8")
    temiz = re.sub(r"^\s*//.*$", "", metin, flags=re.M)
    d = json.loads(temiz)
    onceki = {
        "allowed": len(d.get("zoo-code.allowedCommands", [])),
        "denied": len(d.get("zoo-code.deniedCommands", [])),
    }
    if kuru:
        return onceki

    yedek = yol.with_name(
        "settings.json.yedek_" + _dt.datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(yol, yedek)

    if _yorum_var(metin):
        # Yorumlu dosya: yalniz iki listeyi metin icinde degistir.
        def _degistir(m: str, anahtar: str, deger: list[str]) -> str:
            yeni = f'"{anahtar}": ' + json.dumps(deger, ensure_ascii=False, indent=4)
            desen = rf'"{re.escape(anahtar)}"\s*:\s*\[.*?\]'
            if re.search(desen, m, flags=re.S):
                return re.sub(desen, lambda _: yeni, m, count=1, flags=re.S)
            return m.rstrip().rstrip("}") + f",\n    {yeni}\n}}\n"
        metin = _degistir(metin, "zoo-code.allowedCommands", IZINLI)
        metin = _degistir(metin, "zoo-code.deniedCommands", YASAK)
        yol.write_text(metin, encoding="utf-8")
    else:
        d["zoo-code.allowedCommands"] = IZINLI
        d["zoo-code.deniedCommands"] = YASAK
        yol.write_text(json.dumps(d, ensure_ascii=False, indent=4) + "\n",
                       encoding="utf-8")

    # Dogrulama: yeniden oku.
    son = json.loads(re.sub(r"^\s*//.*$", "", yol.read_text(encoding="utf-8"), flags=re.M))
    assert son["zoo-code.allowedCommands"] == IZINLI, "allowed yazilamadi"
    assert son["zoo-code.deniedCommands"] == YASAK, "denied yazilamadi"
    return {**onceki, "yedek": str(yedek), "allowed_yeni": len(IZINLI), "denied_yeni": len(YASAK)}


def main() -> int:
    kuru = "--kuru" in sys.argv
    sonuc = duzelt(ayar_yolu(), kuru=kuru)
    print(("KURU " if kuru else "") + json.dumps(sonuc, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
