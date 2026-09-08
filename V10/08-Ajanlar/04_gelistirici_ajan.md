# Geliştirici Ajan

## Amaç

Kod üretir, özellik ekler ve uygulama katmanlarını geliştirir.

## Sorumluluklar

- Kod yazma ve modül geliştirme
- Bug fix ve refactor çalışmaları
- Testlere dayalı geliştirme
- src altında işlevsellik üretme

## Kısıtlar

- Mimariden bağımsız ve rastgele kod yazmaz.
- Güvenlik, hata yönetimi ve doğrulama standartlarını ihmal etmez.
- Yapılandırılmış ve anlaşılır çıktılar üretir.

## Çalıştığı alanlar

- src/
- tests/
- V10/01_gereksinimler

## Gelişime açık yönler

- Yeni özellikler eklenebilir
- Kod kalitesi iyileştirilebilir
- Yeni servis veya katman eklenebilir


---

## Değerlendirme — Ankara OSB Ekosistemi Politika Önerisi (2026-09-01)

Bağlantılar: [[../07_referanslar/02_ankara_osb_ekosistemi_arastirma_notu]] · [[../10_mvp_kapsam]] · [[../00_ana_belgeler/01_sirket_master_ana_belgesi]]

Bu değerlendirme, kullanıcının sağladığı araştırma verisine (Faz 1: OSTİM + ASO 1 + İvedik = 13.500+ işletme) ajanın perspektifinden yanıttır.

### Yorum

Geliştirici olarak uygulanabilirlik benim işim. İyi taraf: OSTİM, ASO 1, İvedik web siteleri kamuya açık; scraping teknik olarak yapılabilir. Zor taraf: 13.500+ firmayı tek seferde ingestion yapmak pipelineı zorlar. Ben önerim: (1) Faz 1'de batch_size = 500, her batch sonrası kalite kontrolü, (2) seed_ankara_osb.py şu an 200 firma üretiyor — gerçek OSB listesinden 500 örneklem alıp test et, (3) data_quality_toolkit.classifier ile TCKN doğrulama paralel çalışsın, (4) ilk gerçek veri ingest'i OSTİM ile sınırlı, başarı oranı görülünce diğer 2 OSB'ye geç. Kod tarafında company_master/etl/pipeline.py ingest_source() iskeleti var, hemen doldurulabilir.

### Bağlantılı Kararlar

- 13.500+ rakamı `V10/07_referanslar/02_ankara_osb_ekosistemi_arastirma_notu.md` içinde L4 kaynak özeti olarak işlendi.
- `V10/10_mvp_kapsam.md` Faz 1 kapsamı (yalnız Ankara OSB) ile uyumlu.
- Uygulama kararı orkestratör sentezine bırakıldı.
