#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Intelligence modulu kullanim ornekleri."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from company_master.intelligence.market_brain import MarketBrain
from company_master.intelligence.customer_brain import CustomerBrain


def main():
    print("=" * 60)
    print("MARKET BRAIN - Pazar Analizi")
    print("=" * 60)
    mb = MarketBrain()

    print("\n[1] Sektor dagilimi (ilk 5):")
    sectors = mb.sector_count()
    for s in sectors[:5]:
        print(f"  - {s['sektor']}: {s['company_count']} ({s['share_pct']}%)")

    print("\n[2] Pazar buyuklugu tahmini (genel):")
    size = mb.market_size_estimate()
    print(f"  Firma sayisi: {size['company_count']}")
    print(f"  Tahmini calisan: {size['total_employee_estimate']}")
    print(f"  Tahmini ciro: {size['estimated_revenue_tl']:,.0f} TL")
    print(f"  Guven: {size['confidence']}")

    print("\n[3] Rekabet analizi - ilk sektor:")
    if sectors and sectors[0]["sektor"] != "Bilinmiyor":
        sec = sectors[0]["sektor"]
    else:
        sec = sectors[1]["sektor"] if len(sectors) > 1 else sectors[0]["sektor"]
    comp = mb.competitive_analysis(sec)
    print(f"  Sektor: {comp['sektor']}")
    print(f"  Firma sayisi: {comp['company_count']}")
    print(f"  Yogunluk: {comp['competition_density']}")
    print(f"  OSB uye orani: {comp['osb_member_ratio']}%")

    print("\n[4] Trend sektorler (ilk 5):")
    for t in mb.trending_sectors(limit=5)[:5]:
        print(f"  - {t['sektor']}: skor={t['trend_score']}, n={t['company_count']}")

    print()
    print("=" * 60)
    print("CUSTOMER BRAIN - Musteri Analizi")
    print("=" * 60)
    cb = CustomerBrain()

    print("\n[1] Musteri segmentasyonu:")
    segs = cb.segment_companies()
    print(f"  Toplam: {segs['total_companies']}")
    for s in segs["segments"]:
        print(f"  - {s['segment']}: {s['count']} ({s['share_pct']}%)")

    print("\n[2] Oncelikli lead'ler (ilk 5):")
    leads = cb.priority_leads(top_n=5)
    for lead in leads:
        print(f"  - {lead['legal_name']}: skor={lead['priority_score']}, "
              f"calisan={lead['employee_count']}, dq={lead['data_quality_score']}")

    if leads:
        sample_id = leads[0]["company_id"]
        print(f"\n[3] Kalite skoru (ornek firma: {leads[0]['legal_name'][:40]}):")
        q = cb.quality_score(sample_id)
        print(f"  Skor: {q['score']}/100")
        print(f"  Bilesenler: {q['components']}")

        print(f"\n[4] LTV tahmini:")
        ltv = cb.lifetime_value_estimate(sample_id)
        print(f"  LTV: {ltv.get('ltv_tl', 0):,.0f} TL")

        print(f"\n[5] Churn riski:")
        ch = cb.churn_risk(sample_id)
        print(f"  Risk: {ch['risk']} - Sebepler: {ch['reasons']}")

    print("\n=== Tum testler basariyla tamamlandi ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"HATA: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)