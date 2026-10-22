# -*- coding: utf-8 -*-
"""codex_model_sec.py PORTFOY'unu GUI-UYUMLU isimlere cevirir.

OLCULEN (20.10 ~21:57):
  GUI sag alttaki model kutusu OpenAI HESAP planindan geliyork
  (auth kartinda chatgpt_plan_type = 'free') -> listede TEK satir gorunur,
  secim yapilamiyor. Biz bunu degistiremeyiz (hesap/plani OpenAI'nin kontrolunde).
  AMA config.toml'daki isim GUI kataloğunda varsa ETIKET DOGRU gorunur
  ('Ozel' yerine '5.6 Luna'). cx/on eki GUI'de 'Ozel' yazdiriyork.

YAPILACAK: portfoydeki modelleri, GUI'nin tanidigi ve 9Router'da TAKMA ADI
olan isimlere bagla. Takma adlar canli test edildi (14/14, 2/2 deneme).
  gpt-5.6-luna  -> cx/gpt-5.6-luna  (guclu)
  gpt-5.6-terra -> cx/gpt-5.6-terra (kod)
  gpt-5.5       -> nemotron-3.5-lightning:free (bedava)
  glm-5.3       -> nemotron-3-nano-omni reasoning (derin)
  qwen3.8-flash-next -> bzl/auto:free (oto)
  claude -> 'fullclaude' GUI kataloğunda YOK, etiket 'Ozel' kalir ama CALISIR.
Idempotent + yedek + canli dogrulama.
"""
import re
import shutil
import subprocess
import sys
import tomllib
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ARAC = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\scripts\codex_model_sec.py")
MASAUSTU = Path(r"C:\Users\yasin\OneDrive\Desktop\gereksiz")
K9 = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"

YENI = {
    "guclu": '"9router", "gpt-5.6-luna"',
    "kod": '"9router", "gpt-5.6-terra"',
    "bedava": '"9router",\n                "gpt-5.5"',
    "derin": '"9router",\n                "glm-5.3"',
    "oto": '"9router", "qwen3.8-flash-next"',
}


def canli(m: str) -> str:
    b = ("{" + '"model": "%s", "input": "Reply with exactly: OK", "stream": false}' % m).encode()
    r = urllib.request.Request("http://localhost:20128/v1/responses", data=b,
                               headers={"Authorization": "Bearer " + K9,
                                        "Content-Type": "application/json"},
                               method="POST")
    try:
        with urllib.request.urlopen(r, timeout=90) as x:
            import json
            j = json.loads(x.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return "HATA " + str(e)[:34]
    import json
    metin = " ".join([(c.get("text") or c.get("value") or "")
                      for it in (j.get("output") or [])
                      for c in (it.get("content") or [])]).strip()
    if not metin and "choices" in j:
        metin = (j["choices"][0].get("message", {}).get("content") or "").strip()
    return f"{j.get('status')}/{metin[:12] or 'BOS'}"


metin = ARAC.read_text(encoding="utf-8")
shutil.copy2(ARAC, ARAC.with_name("codex_model_sec.py.yedek-20261020b"))
sayac = 0
for profil, deger in YENI.items():
    # portfoy satiri:  "ad":   ("GUC", "9router", "<model>"),  (çok satirli olabilir)
    desen = re.compile(r'("%s":\s+\("[^"]*",\s*)"[^"]*"(?:,\s*\n\s*)?"[^"]*"(,)'
                       % re.escape(profil))
    yeni, n = desen.subn(lambda m: m.group(1) + deger + m.group(2), metin, count=1)
    if n == 1:
        metin = yeni
        sayac += 1
        print(f"PORTFOY guncellendi: {profil}")
    else:
        print(f"SARIMAT Desen tutmadi: {profil} (elle kontrol gerekir)")
ARAC.write_text(metin, encoding="utf-8")

import ast
ast.parse(ARAC.read_text(encoding="utf-8"))
print(f"\ntoplam {sayac}/5 guncellendi · sozdizimi gecerli")

# aktif modeli GUI-uyumlu isme al (su an cx/ ekiyle yazilmis, etiket 'Ozel')
subprocess.run([sys.executable, str(ARAC), "guclu"], check=True, timeout=120)
with open(Path.home() / ".codex" / "config.toml", "rb") as f:
    d = tomllib.load(f)
aktif = d.get("model")
print("AKTIF model:", aktif, "· GUI kataloğunda var mi:",
      "EVET" if aktif in {"gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.5", "glm-5.3",
                          "qwen3.8-flash-next", "gpt-6-luna", "gpt-6-sol",
                          "gpt-6-astra", "gpt-6.1-sol", "gpt-5.6-sol"} else "HAYIR")
print("canli test:", canli(aktif))

# tek-tik dosyasini masaustune koy
MASAUSTU.mkdir(parents=True, exist_ok=True)
for ad in ("codex_degistir.bat", "codex_model_menu.bat", "codex_model_sec.py"):
    src = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\scripts") / ad
    if src.exists():
        shutil.copy2(src, MASAUSTU / ad)
        print("MASAUSTU:", ad)
print("masaüstü içeriği:", sorted(p.name for p in MASAUSTU.iterdir()))
