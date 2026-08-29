---
name: data-designer-synthetic
description: >-
  NVIDIA NeMo Data Designer, Gretel ve Misata standartlarında bildirimsel (declarative)
  şema tanımlama, KVKK/GDPR uyumlu sentetik test verisi üretimi ve iş senaryoları simülasyonu becerisi.
---

# Sentetik Veri Tasarımı & Üretimi Becerisi (Data Designer & Synthetic Engine)

Bu beceri, işletmelerin gerçek müşteri verilerini riske atmadan güvenli, istatistiksel olarak tutarlı ve iş kurallarına uygun sentetik test verileri üretmesini sağlar.

---

## 1. Sentetik Veri Tasarım Döngüsü

### Adım 1: Bildirimsel Şema Tasarımı (Schema Declaration)
Her veri alanı için tip, format ve kısıtları (constraints) belirle:
* Sayısal alanlar için: Dağılım (Normal, Uniform), min, max, ortalama, standart sapma.
* Kategorik alanlar için: Olasılık ağırlıkları (Örn: `['İstanbul': 0.45, 'Ankara': 0.25, 'İzmir': 0.30]`).
* Tarih alanları için: Başlangıç-bitiş tarih aralıkları ve artış trendleri.

### Adım 2: İş Senaryoları ve Anomali Enjeksiyonu (Outcome & Scenario Modeling)
* Hedef senaryoları tanımla:
  - *Normal Akış:* %95 standart işlem.
  - *Fraud / Sahtekarlık Simülasyonu:* %5 yüksek tutarlı, şüpheli lokasyonlu işlem.
  - *Uç Durumlar (Edge Cases):* Aşırı uzun isimler, sınır limitinde bakiyeler.

### Adım 3: Gizlilik ve KVKK/GDPR Uyumu (Privacy-Preservation)
* Gerçek isimler, TCKN'ler veya telefon numaraları yerine tamamen matematiksel olarak üretilmiş taklit (mock) veriler kullan.
