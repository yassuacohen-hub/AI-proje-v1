# -*- coding: utf-8 -*-
"""nobet_modu.json yoktu -> herkes kademe 1 (PLAN). Dosyayi kur, chat kayitlarini D-286 ile kapat/guncelle."""
import sys as _s; _s.stdout.reconfigure(encoding="utf-8", errors="replace")
import json, os, subprocess, sys
from pathlib import Path

R = Path(r"c:\Huginn Data Projesi\Huginn Data Insights"); PY = sys.executable
ENV = dict(os.environ, HUGINN_AJAN="ihsan", PYTHONIOENCODING="utf-8")
MOD = R / "data/orchestrator/nobet_modu.json"
CHAT = R / "data/orchestrator/ajan-chat.jsonl"

def run(*args):
    r = subprocess.run([PY, *args], cwd=R, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    print(">>", " ".join(args[:5]), "| rc", r.returncode); print((r.stdout + r.stderr).strip()[-800:])

# 1) kademe dosyasi (ponytail: kademe 2 = P2- calisir; P0/P1 PO karari bekler, kademe 3 ihsan)
assert not MOD.exists(), "zaten var, dokunma"
MOD.write_text(json.dumps({
    "varsayilan_kademe": 2,
    "ajanlar": {
        "ihsan": {"kademe": 3, "rol": "orkestrator", "aktif": True},
        "utku":  {"kademe": 2, "rol": "uretim",      "aktif": True},
        "salih": {"kademe": 2, "rol": "test",        "aktif": True},
        "yasu":  {"kademe": 2, "rol": "denetim",     "aktif": True},
    },
    "not": "2026-10-10 ihsan: dosya yoktu, 2026-10-06'dan beri herkes kademe 1 (PLAN) kalmis. D-65.",
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("yazildi:", MOD)

# 2) sorun_index: task altindaki kayit sirasi (0-based)
def idx(task, ajan):
    kayitlar = [json.loads(l) for l in CHAT.read_text(encoding="utf-8").splitlines() if l.strip()]
    ayni = [k for k in kayitlar if k.get("task_id") == task]
    for i, k in enumerate(ayni):
        if k.get("ajan") == ajan:
            print(f"{task} {ajan} -> index {i} ({k.get('tarih') or k.get('zaman')})")
            return i
    raise SystemExit(f"bulunamadi {task} {ajan}")

T = "UI-ADMIN-PANEL-TEMEL-REFERANS-01"
KARAR = ("Kök neden: data/orchestrator/nobet_modu.json yoktu -> varsayilan_kademe=1, 2026-10-06'dan beri hicbir ajan "
         "gorev alamadi (ajan_nobet.log: son kademe>=2 turu 2026-10-05 23:45). Dosya kuruldu: utku/salih/yasu=2, ihsan=3. "
         "P0 is kademe 2'de 'al ETME' kuralina takilir; PO karari: (a) utku'yu kademe 3'e cikar ya da (b) ihsan devralir. "
         "Karar gelene kadar gorev blocked kalir, neden artik panoda yazili (D-65).")
run("scripts/ajan_chat.py", "kapat", T, str(idx(T, "utku")), "--karar", KARAR)
run("scripts/ajan_chat.py", "guncelle", T, str(idx(T, "ihsan")), "--durum", "cozuldu", "--cozum",
    "Düzeltme: blokaj nedeni chat'te 2026-10-06'dan beri vardı (utku kaydı), panoda değildi; benim 'kayıtlı değil' iddiam eksikti. " + KARAR)
run("scripts/ajan_nobet_kosucusu.py", "--durum")
