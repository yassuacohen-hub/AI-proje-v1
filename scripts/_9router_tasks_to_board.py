#!/usr/bin/env python3
"""9R-02/9R-03/9R-04 gorevlerini panoya ekler (9R-02 aktif, digerleri plan).

ORCH-01/ORCH-02 devami: atomik yazma kullanilir; dosyalar -> file-lock
sahipligi alir. Kilit cakismasi olursa PermissionError rapordanlanir ve
gorev eklenmez (pano kirlenmez).
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.company_master.orchestrator.task_board import (
    gorev_ekle,
    gorev_guncelle,
    agent_sync_yaz,
    gorev_listesi,
)

GOREVLER = [
    {
        "task_id": "9R-02",
        "baslik": "Vektor Katmani + Dublikasyon Pilotu - ChromaDB, vector/ paketi, index_companies.py, matcher doldurma (VKN+fuzzy+vektor)",
        "sahip": "roo_code",
        "oncelik": "P1",
        "aktif": True,
        "dosyalar": [
            "src/company_master/vector/",
            "src/company_master/entity_resolution/matcher.py",
            "scripts/index_companies.py",
            "requirements-app.txt",
            "tests/vector/",
        ],
        "source": "ic",
        "from_agent": "roo_code",
    },
    {
        "task_id": "9R-03",
        "baslik": "Chat Tabanli Ilan Zenginlestirme - analyzer.py'ye 9Router chat ile sektor/pozisyon/skill cikarimi (fallback: regex)",
        "sahip": "roo_code",
        "oncelik": "P2",
        "aktif": False,
        "dosyalar": [
            "src/company_master/intelligence/job_intelligence/pipeline/analyzer.py",
        ],
        "source": "ic",
        "from_agent": "roo_code",
    },
    {
        "task_id": "9R-04",
        "baslik": "Web Fetch/Search Aktivasyonu - Firecrawl+Tavily provider eklendikten sonra web_fetch/web_search canli test + kariyer sayfasi analiz akisi",
        "sahip": "roo_code",
        "oncelik": "P3",
        "aktif": False,
        "dosyalar": [
            "src/company_master/gateway/ninerouter_client.py",
        ],
        "source": "ic",
        "from_agent": "roo_code",
    },
]


def main() -> int:
    mevcut = {t["task_id"] for t in gorev_listesi()}
    eklendi, hata = [], []
    for g in GOREVLER:
        tid = g["task_id"]
        if tid in mevcut:
            print(f"ATLANDI (var): {tid}")
            continue
        aktif = g.pop("aktif", False)
        try:
            task = gorev_ekle(**g)
            if aktif:
                gorev_guncelle(tid, durum="aktif")
            eklendi.append(tid)
            print(f"EKLENDI: {tid} -> {task['durum']}{' (aktif)' if aktif else ''}")
        except PermissionError as exc:
            hata.append(tid)
            print(f"LOCK ENGELI: {tid} -> {exc}")
        except Exception as exc:  # noqa: BLE001
            hata.append(tid)
            print(f"HATA: {tid} -> {exc!r}")

    if eklendi:
        agent_sync_yaz()
        print(f"agent_sync yenilendi ({len(eklendi)} gorev).")

    print(f"SONUC: eklenen={eklendi} hata={hata}")
    return 1 if hata else 0


if __name__ == "__main__":
    raise SystemExit(main())