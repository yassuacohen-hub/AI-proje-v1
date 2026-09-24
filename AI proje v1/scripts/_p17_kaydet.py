# -*- coding: utf-8 -*-
"""P1-7 gorev kaydi + run3 ilerleme kontrolu (gecici orkestrasyon scripti)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.orchestrator import task_board as tb  # noqa: E402

mevcut = [t["task_id"] for t in tb.gorev_listesi()]
if "P1-7" not in mevcut:
    tb.gorev_ekle(
        "P1-7",
        "VKN web kazima (footer/hakkimizda/KVKK sayfalari)",
        "web_kazima",
        "P1",
        dosyalar=[
            "scripts/vkn_web_scraper.py",
            "AI proje v1/V10/07_referanslar/vkn_bulma_stratejisi.md",
        ],
    )

tb.gorev_guncelle("P1-7", durum="aktif", **{
    "not": ("vkn_web_scraper.py uretildi: robots.txt kontrolu, 2 sn rate limit, "
            "Turk VKN checksum dogrulamasi, VPN kurali notu. Strateji dokumani: "
            "07_referanslar/vkn_bulma_stratejisi.md. 30 sitelik pilot calisiyor.")
})
tb.handoff_yaz(
    "P1-7",
    "VKN web kazima araci hazir, pilot tarama suruyor",
    "Pilot verimi olculup yuksekse 500-er partiyle tam tarama",
)
tb.agent_sync_yaz()
print("P1-7 eklendi/guncellendi + AGENT_SYNC yenilendi")
