# -*- coding: utf-8 -*-
"""BRIK-00 red duzeltmesi (kullanici karari 2026-09-22): kuyruk kaydi reddedildi'ye cekilir,
panodaki hatali done kaydi iptal'e donusturulur."""
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.company_master.orchestrator import task_board as tb  # noqa: E402

GEREKCE = (
    "Pano kaydi yok (task_board.json'da BRIK-00 yok), kanit/cikti dosyasi bildirilmemis. "
    "D-68 tutarlilik ihlali. Kullanici karari 2026-09-22: red. "
    "Onceki 'onaylandi' kaydi gecersiz kilindi."
)

# 1) Kuyruk: onaylandi -> reddedildi
kuyruk_yolu = tb.STATE_DIR / "onay_kuyrugu.json"
kuyruk = json.loads(kuyruk_yolu.read_text(encoding="utf-8-sig"))
n = 0
for x in kuyruk:
    if x.get("task_id") == "BRIK-00" and x.get("durum") == "onaylandi":
        x["durum"] = "reddedildi"
        x["onaylayan"] = "yasu (kontrolor)"
        x["gerekce"] = GEREKCE
        n += 1
tb.atomic_write_text(kuyruk_yolu, json.dumps(kuyruk, ensure_ascii=False, indent=2))
print("kuyruk guncellendi:", n)

# 2) Pano: done -> iptal (kayit varsa)
gorev = tb.gorev_getir("BRIK-00")
if gorev is not None:
    tb.gorev_guncelle(
        "BRIK-00",
        durum="archive",
        bitis=datetime.now().isoformat(timespec="seconds"),
        notu=f"IPTAL (kontrolor yasu, kullanici karari 2026-09-22): {GEREKCE}",
    )
    print("pano guncellendi: BRIK-00 -> iptal")
else:
    print("pano kaydi zaten yok")
