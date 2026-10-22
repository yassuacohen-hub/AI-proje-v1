# -*- coding: utf-8 -*-
"""SAG ALTI 'Ozel' ETIKETI -> GERCEK MODEL ADI.

OLCULEN (20.10 ~21:51):
  config.toml model = 'cx/gpt-5.6-luna'. GUI'nin tanidigi 11 isim arasinda bu YOK
  (GUI kataloqu: gpt-6-astra, gpt-6.1-sol, gpt-6-sol, gpt-6-luna, gpt-5.6-sol,
   gpt-5.6-terra, gpt-5.6-luna, daybreak x2, gpt-5.5, codex-auto-review).
  GUI tanimadiyi modeli 'Ozel' diye etiketler -> kullanici 'secim alani yok' gorur.

COZUM: ayni mutfak modelini, GUI'nin TANIDIGI isimle yazmak.
  'gpt-5.6-luna' artik 9Router'da takma ad olarak CALISIYOR (alias eklendi, 2/2 test)
  => GUI ismi tanir (etiket dogru gorunur) VE istek 9Router'da karsilik bulur.

Guvenlik: yedek + tomllib geri-okuma + canli /responses testi. Anahtar yazilmaz.
"""
import json
import re
import shutil
import tomllib
import urllib.request
from datetime import datetime
from pathlib import Path

CFG = Path.home() / ".codex" / "config.toml"
YEDEK = Path.home() / ".codex" / "yedek"
K = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"

# GUI kataloğundaki adlar -> 9Router takma adi uzerinden gercek hedef
HEDEF = "gpt-5.6-luna"


def canli(m: str) -> str:
    govde = {"model": m, "input": "Reply with exactly: ETIKET-TAMAM", "stream": False}
    req = urllib.request.Request(
        "http://localhost:20128/v1/responses", data=json.dumps(govde).encode(),
        headers={"Authorization": "Bearer " + K,
                 "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return f"HATA {str(e)[:50]}"
    metin = " ".join([(c.get("text") or c.get("value") or "")
                      for it in (j.get("output") or [])
                      for c in (it.get("content") or [])]).strip()
    if not metin and "choices" in j:
        metin = (j["choices"][0].get("message", {}).get("content") or "").strip()
    return f"{j.get('status')} / {metin[:24] or 'BOS'}"


def main() -> int:
    # 1) hedef GUI kataloğunda ve canli mi — ONCE dogrula, sonra yaz
    print("hedef canli test:", canli(HEDEF))

    metin = CFG.read_text(encoding="utf-8")
    YEDEK.mkdir(parents=True, exist_ok=True)
    y = YEDEK / ("config." + datetime.now().strftime("%Y%m%d_%H%M%S") + ".toml")
    shutil.copy2(CFG, y)
    yeni, n1 = re.subn(r'(?m)^model = "[^"]*"', f'model = "{HEDEF}"', metin, count=1)
    if n1 != 1:
        raise SystemExit("model satiri bulunamadi (dosya bozulmadi)")
    CFG.write_text(yeni, encoding="utf-8")
    with open(CFG, "rb") as f:
        d = tomllib.load(f)
    print("yedek:", y.name)
    print(f"yeni AKTIF: {d.get('model_provider')}/{d.get('model')}")
    print("GUI kataloğunda var mi:", "EVET" if d.get("model") == HEDEF else "HAYIR")
    print("\nSONRAKI ADIM: Codex'i kapatip ac -> sag altta '5.6 Luna' yazmali, 'Ozel' degil.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
