# ETL Mimarisi

Bağlantılar: [[00-Home]] · [[01_sirket_master_ana_belgesi]] · [[01_mvp_gereksinimleri]] · [[01_veri_toplama_modeli]]

Bu belge, [[01_sirket_master_ana_belgesi]] (Company Master V1.0) §8 ve §17'den türetilmiş sistem mimarisi özetidir.

## Veri akışı

```text
SOURCE
  ↓
RAW INGESTION
  ↓
NORMALIZATION
  ↓
VALIDATION
  ↓
ENTITY RESOLUTION
  ↓
COMPANY MASTER
  ↓
ENRICHMENT
  ↓
DATA QUALITY
  ↓
SEARCH INDEX
  ↓
INTELLIGENCE LAYER
```

Ham veri ile temizlenmiş veri ayrıdır.

## Ana kimlik kararı

```text
company_id = UUID (Primary Key)
VKN = benzersiz kimlik/doğrulama alanı
MERSİS = yardımcı kimlik alanı
```

## Entity Resolution eşikleri (başlangıç)

```text
95–100 → otomatik eşleştir
85–94  → güçlü aday
70–84  → ikinci kontrol
<70    → eşleştirme yapma
```

Eşikler gerçek veri benchmark'ı ile yeniden ayarlanır.

## Arama

İlk MVP için **PostgreSQL + Full Text Search** yeterlidir. Meilisearch / Elasticsearch ilk günden zorunlu değildir.

## Mimari sınır

Company Master tek başına tahmin ve skorlama yapmaz (satın alma, bütçe, fırsat skoru vb.). Bunlar ileride Intelligence Engine katmanlarının sorumluluğudur. Tam tablo tanımları için master belge §3'e bakınız.
