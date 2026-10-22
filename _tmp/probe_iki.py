# -*- coding: utf-8 -*-
"""IKI PROBE (tek turda, bagimsiz):
 A) Claude Code 'hangi modeli kullandigini' soyleyebiliyor mu?
    -> claude -p --output-format json  icinde model alani var mi?
       Varsa secici arac 'secim gercekten uygulandi' kanitini KULLANICIGA gosterir.
 B) Codex sol alt rozeti model adini gosterir mi?
    -> rozet = [model_providers.X] name alanini basiyor (olculen).
       name gecici olarak model+ozellik yazip degismiyor mu, CLI ile test edilir,
       sonra ESKI DEGERE geri alinir (patch-apply-revert).
Degerler yazilmaz (D-380)."""
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
CFG = Path.home() / ".codex" / "config.toml"
S = json.loads((Path.home() / ".claude" / "settings.json").read_text(encoding="utf-8"))
for k, v in (S.get("env") or {}).items():
    os.environ[k] = str(v)

print("=== A) Claude Code JSON cikisinda model bilgisi ===")
for ek in (["--output-format", "json"], ["--output-format", "json", "--model",
                                          "claude-claudecombo"]):
    t = time.time()
    try:
        o = subprocess.run(["claude", "-p", "Say OK"] + ek, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=200)
        cikti = (o.stdout or "").strip()
        print(f"\n{' '.join(ek)}  ({time.time()-t:.1f}s)")
        try:
            j = json.loads(cikti)
            print("  ALANLAR:", sorted(j.keys()))
            for a in ("model", "modelUsage", "durationMs", "totalCostUsd", "numTurns"):
                if a in j:
                    print(f"  {a} = {json.dumps(j[a])[:120]}")
        except Exception:
            print("  JSON degil:", cikti[:120])
    except Exception as e:  # noqa: BLE001
        print("  hata:", str(e)[:80])

print("\n=== B) Codex rozeti = provider 'name' alani (gecmik dene + geri al) ===")
metin = CFG.read_text(encoding="utf-8")
eski_ad = re.search(r'\[model_providers\.evren\]\s*\nname = "([^"]*)"', metin)
print("  mevcut rozet yazisi:", eski_ad.group(1) if eski_ad else "?")
yedek = CFG.with_name("config.probe_yedek.toml")
shutil.copy2(CFG, yedek)

# aktif provider'i evren yapip name'i model bilgisiyle degistir
m = re.search(r'(?m)^model_provider = "([^"]*)"', metin)
aktif = m.group(1) if m else "?"
print("  aktif provider:", aktif)
# AKTIF saglayicinin BLOUGUNA hedef al (ilk name = 9router'a aitti -> yanlisti)
blok = r'(\[model_providers\.' + re.escape(aktif) + r'\][^\[]*)'
pencere = re.search(blok, metin, re.S)
if not pencere:
    print("  BLOK BULUNAMADI, probe atlandi")
    raise SystemExit(0)
eski_blok = pencere.group(1)
yeni_blok, n = re.subn(r'(?m)^(name = )"[^"]*"',
                       r'\g<1>"EVREN-GPT / hizli-2sn"', eski_blok, count=1)
yeni = metin.replace(eski_blok, yeni_blok, 1)
CFG.write_text(yeni, encoding="utf-8")
print("  %s blogu name guncellendi (n=%d):" % (aktif, n),
      "EVREN-GPT" in CFG.read_text(encoding="utf-8"))

cx = Path.home() / "AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe"
o = subprocess.run([str(cx), "--strict-config", "exec",
                    "Reply with exactly: ROZET-TEST", "-s", "read-only"],
                   input="", capture_output=True, text=True,
                   encoding="utf-8", errors="replace", timeout=400)
bulunan = "ROZET-TEST" in (o.stdout or "")
print("  Codex name degisikliginden SONRA calisiyor mu:", "EVET" if bulunan else "HAYIR")
print("  stdout kuyrugu:", (o.stdout or "").strip()[-90:].replace("\n", " | "))

# GERI AL
shutil.copy2(yedek, CFG)
print("  geri alindi:", eski_ad.group(1) if eski_ad else "?",
      "→", "OK" if (eski_ad and eski_ad.group(1) in CFG.read_text(encoding="utf-8")) else "KONTROL ET")
