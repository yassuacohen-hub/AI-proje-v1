# -*- coding: utf-8 -*-
"""Pano guncelleme: P1-1/P1-2 scraper implementasyonu."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.orchestrator import task_board as tb  # noqa: E402

# P1-1 Ivedik scraper implemente edildi
tb.gorev_guncelle("P1-1", durum="aktif", **{
    "not": ("ivedik_scraper.py implemente edildi: fetch_firma_liste + fetch_firma_detay. "
            "Generic OSB yapisina uygun (card/table fallback). "
            "VPN ile test edilmesi gerekiyor. "
            "Calistirma: python -m company_master.etl.scrapers.ivedik_scraper --detayli")
})
tb.handoff_yaz("P1-1", "Ivedik scraper implementasyonu tamam (kod hazir)",
               "VPN ile ivedik.org.tr'ye erisip test et; selector'lari siteye gore ayarla")

# P1-2 Başkent scraper implemente edildi
tb.gorev_guncelle("P1-2", durum="aktif", **{
    "not": ("baskent_scraper.py implemente edildi: fetch_firma_liste + fetch_firma_detay. "
            "Generic OSB yapisina uygun (card/table fallback). "
            "VPN ile test edilmesi gerekiyor. "
            "Calistirma: python -m company_master.etl.scrapers.baskent_scraper --detayli")
})
tb.handoff_yaz("P1-2", "Başkent scraper implementasyonu tamam (kod hazir)",
               "VPN ile baskentosb.org.tr'ye erisip test et; selector'lari siteye gore ayarla")

tb.agent_sync_yaz()
print("Pano guncellendi")