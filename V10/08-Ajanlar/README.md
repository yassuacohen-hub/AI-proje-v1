# Ajanlar ve Gelişime Açık Yapı

Bu bölüm, proje içindeki yapay zeka ajanlarının sorumluluk alanlarını, sınırlarını ve gelişime açık yapısını açıklar.

## Temel ilke

- Her ajan tek bir ana sorumluluğa sahip olmalıdır.
- Ajanlar birbirini ezmemeli, aynı anda aynı işi yapmamalıdır.
- Gelişim açık olmalı; ancak riskli operasyonlar kontrollü ve kısıtlı şekilde çalıştırılmalıdır.
- Web kazıma ve veri toplama, ayrı uzmanluk alanı olarak eklenebilir; ana karar ve doğrulama katmanı ayrı tutulmalıdır.

## Ajan seti

1. [[01_koordinator_ajan]]
2. [[02_mimar_ajan]]
3. [[03_arastirmaci_ajan]]
4. [[04_gelistirici_ajan]]
5. [[05_kalite_ajan]]
6. [[06_web_kazima_uzmani]]

## Ajanlar için standart

- Her ajan için temel alanlar şunlardır:
  - Amaç
  - Sorumluluk alanı
  - Kısıtlar
  - Çalıştığı dosyalar
  - Çıktı formatı
  - Gelişim ve genişletme alanları

## Önerilen operasyon modeli

- Koordinatör ajan yönlendirir.
- Mimar ajan tasarımı korur.
- Araştırmacı ajan bilgi toplar.
- Geliştirici ajan kod üretir.
- Kalite ajan doğrulama yapar.
- Web kazıma uzmanı sadece veri temini için kullanılır.

Bu yapı, hem genişletilebilir hem de denetlenebilir bir yapıdır.
