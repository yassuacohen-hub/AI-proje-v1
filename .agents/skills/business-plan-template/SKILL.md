---
name: business-plan-template
description: >-
  Huginn Data Insights için iş planı + pazarlama kanavunu tanımlayan
  şablon. OSINT kazıma pipeline → lead generation → B2B satış kanalları
  üç aşamada modellenir. Obsidian `V10/06-Kurulum/03_business_plan.md`
  ile sinonk.
author:
  - Cline
version: 1.0.0
license: Apache-2.0
tags:
  - business
  - pazarlama
  - iş-planı
  - lead-generation
  - osint
---

# İş Planı Şablonu — Huginn OSINT Pazarlama Pipeline

Bu beceri, **veri kazıma → lead skor → pazarlama kampanyası** üç aşamalı
iş modelini tanımlar. OSINT motoru (`osint-web-scraping-toolkit` skill)
ile birlikte çalışır.

## 1. İş Modeli Canvas (özet)

| Anahtar İş Parçacığı | Kanallar | Değer Teklifleri |
|----------------------|----------|------------------|
| OSINT kazıma (Apify) + hukuki tavsiye | Web scraping, webhook | Veri zenginleştirme, pazarlama listeleri, risk skoru |
| Lead skorlama (quality_engine) | Admin panel (web_dashboard) | GDPR/KVKK uyumlu lead listesi |
| Satış otomasyonu (CRM entegrasyonu) | CSV / API dışa aktarım | Segment bazlı kampanya |

## 2. Pazarlama Stratejileri

### A. Lead Generation
- `quick_scrape` → işletmeleri topla (`sector="İnşaat/B2B"`)
- webhook → `apify_webhook_events.jsonl` → quality score > 70 → lead

### B. Etkileşim
- web_dashboard `/companies/match` → alıcı sektör eşleştir
- CSV export → sales team (GDPR onaylı)

### C. Satış
- CRM entegrasyonu (`hubspot`, `pipedrive`) — future task

## 3. Maliyet / ROI Tahmini

| Gider | Aylık (₺) | Not |
|-------|-----------|-----|
| Apify kredisi | 15.000 | premium plan |
| OSINT ajan saat | 20.000 | 40 saat @ 500₺ |
| Hosting (Supabase) | 2.000 | DB + auth |
| **Toplam** | **37.000** | |

| Gelir | Tahmin | Not |
|-------|--------|-----|
| Lead satışı (500 lead @ 100₺) | 50.000 | B2B segment |
| **Net** | **13.000** | 35% marj |

## 4. Riskler
- **GDPR/KVKK**: işletme telefon numarası gibi PII toplama — `enterprise-data-classification` skill zorunlu
- **Rate-limit**: aynı domain > 1 dk → ban. `osint-web-scraping-toolkit` retry politikasını uygula
- **Kaynak**: Apify kredisi tükenirse `9router` fallback LLM'ye geçer

## 5. Obsidian / Karar Defteri Entegrasyonu
Her iş planı güncellemesi →
`data/orchestrator/decision_log.jsonl`:

```python
log_decision(
    action="is_plan_guncelle",
    category="pazarlama",
    note="Q4 lead hedefi: 500 → 750; Apify budget +50%"
)
```

---
*Şablon `AI proje v1/V10/06-Kurulum/03_business_plan.md` şablonuna göre
hazırlanmıştır; kopya çatışması yoktur.*
