# Intelligence Modulu

Bu modul Ankara B2B Company Master icin pazar ve musteri analizleri saglar.

## Market Brain

Pazar buyukluk tahmini, rekabet analizi, sektor trendleri ve firsalacak sektorelerin tespiti.

### Kullanim
    from company_master.intelligence.market_brain import MarketBrain, run_analysis
    brain = MarketBrain()
    print(brain.market_size_estimate())
    print(brain.competitive_analysis('Teknoloji ve Bilişim'))
    print(brain.trending_sectors())

### Methods
- sector_count() — Sektor dagilimi
- market_size_estimate() — Pazar buyukluk tahmini
- competitive_analysis(sektor) — Rekabet analizi
- trending_sectors() — Trend sektorler

## Customer Brain

Musteri segmentasyonu, LTV tahmini, churn riski ve priority lead scoring.

### Kullanim
    from company_master.intelligence.customer_brain import CustomerBrain, run_analysis
    brain = CustomerBrain()
    print(brain.segment_companies())
    print(brain.priority_leads(top_n=50))

### Methods
- quality_score(comp) — Veri kalitesi skorlamasi (0-100)
- segment_companies() — Musteri segmentasyonu
- lifetime_value_estimate(comp) — LTV tahmini
- churn_risk(comp) — Churn riski (HIGH/MEDIUM/LOW)
- priority_leads(top_n) — Oncelikli lead listesi

## Gereksinimler
- Python 3.11+
- json (stdlib)
- collections (stdlib)

## Notlar
- Veri kaynagi: data/ostim/firmalar_full.jsonl
- MVP kalip: Veri tabani dogrulaması yapıldıktan sonra kullanılabilir.
- Yontem: Basit skorlama algoritmalari; gerekirse ML modelleriyle geliştirilebilir.
