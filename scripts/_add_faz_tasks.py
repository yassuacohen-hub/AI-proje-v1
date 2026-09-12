#!/usr/bin/env python3
"""Dashboard Faz gorevlerini task board'a ekle."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from company_master.orchestrator.task_board import gorev_ekle, gorev_guncelle

# Faz 1: Roo Code — Mimari altyapı
gorev_ekle(
    task_id="FAZ-01",
    baslik="Dashboard Temel AltyapI: API Envanteri + Auth/RBAC + Pagination + P7-16 Detay",
    sahip="roo_code",
    oncelik="P0",
    dosyalar=["app.py", "web_dashboard/index.html", "web_dashboard/js/app.js"],
    kaynak="harici",
)
gorev_guncelle("FAZ-01", **{"not": "Roo Code: Mimari altyapI, gUvenlik, performans temeli. API envanteri, Auth/RBAC, Pagination, Firma Detay modalI."})

# Faz 2: Cline — Entegrasyon
gorev_ekle(
    task_id="FAZ-02",
    baslik="Dashboard Entegrasyon: P7-18 Filtre + P7-17 Trend + Snapshot Tablosu",
    sahip="cline",
    oncelik="P1",
    dosyars=["app.py", "web_dashboard/js/app.js"],
    kaynak="harici",
)
gorev_guncelle("FAZ-02", **{"not": "Cline: Mevcut API entegrasyonu, veri akIsI. Filtre, Kalite trendi grafIgi, snapshot tablosu."})

# Faz 3: Kilo Code — UX/Tema
gorev_ekle(
    task_id="FAZ-03",
    baslik="Dashboard UX/Tema: P7-21 Performans + Tema + Responsive",
    sahip="kilo_code",
    oncelik="P1",
    dosyalar=["web_dashboard/css/style.css", "web_dashboard/index.html", "web_dashboard/js/app.js"],
    kaynak="harici",
)
gorev_guncelle("FAZ-03", **{"not": "Kilo Code: UI/UX, tema, modal yapI. Performans metrikleri, Dark/Light tema, Responsive."})

print("3 Faz gorevi task board'a eklendi.")
