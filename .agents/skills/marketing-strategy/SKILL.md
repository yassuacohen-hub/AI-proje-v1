---
name: marketing-strategy
description: >-
  OSINT to lead — pazarlama otomasyon workflow'ı. quality_engine skoru,
  web_dashboard match, CSV/CRM dışa aktarım. `business-plan-template`
  skill'ine bağlıdır.
author:
  - Kilo Code
  - Roo Code
version: 1.0.0
license: Apache-2.0
tags:
  - pazarlama
  - lead-scoring
  - osint
  - crm
---

# Pazarlama Stratejisi — OSINT Lead Pipeline

Bu skill, **9router/osint-web-scraping-toolkit** ile toplanan veriyi
**web_dashboard** → **CRM/csv** yoluna taşır.

## Workflow

```
quick_scrape (osint)  →  events.jsonl  →  quality_engine (score > 70)
        ↓                         ↓              ↓
   webhook dlq                  DLQ retry      lead_table
        ↓                         ↓              ↓
retry_dlq_events.py ←→  /api/companies/export (CSV)  →  CRM
```

## A. Lead Skor Kuralı (quality_engine)
```yaml
score_min: 70
rules:
  - sector_match: buyer_sector   # 30 puan
  - calisan: ">50"               # 20 puan
  - web_var: true                # 20 puan
  - email_format: valid          # 15 puan
  - phone_format: valid          # 15 puan
```

## B. web_dashboard entegrasyonu
- `/companies/match` → buyer sector'e en uygun firmalar
- `/companies/export?format=csv` → GDPR onaylı lead listesi
- `/admin/pending` → lead onayı / ban

## C. Kampanya Sekansları
1. **Sıcak lead** (score 85+): email + telefon aynı anda
2. **Ilık lead** (score 70–84): email → 2 gün sonra follow-up
3. **Soğuk lead** (score < 70): nurture drip campaign (9router LLM ile özelleştir)

## D. Ölçüm (Metrik)
| KPI | Hedef | Dashboard |
|-----|-------|-----------|
| Kazıma → lead dönüşüm | 12% | Streamlit P7-19 |
| Lead → CRM entegrasyon | 90% | DLQ error rate |
| Kampanya ROI | 300% | business-plan ROI |

## E. Sınırlamalar / Yasak
- **GDPR**: email/telefon toplama — mutlaka `enterprise-data-classification` sonrası
- **API limit**: 9router web search max 50 sorgu/dk → `respect_rate_limit`
- `.env` anahtarları asla skill içinde hardcode yapılmaz

---
*İlili: `AGENTS.md` → "MVP kuralı: veri tabanı, temel temizlik ve iş
akışı kanıtlanmadan web arayüzüne geçilmez." Bu skill, DLQ retry +
quality score kanıtları doğrultusunda çalışır.*
