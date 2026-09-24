# MVP Gereksinimleri

Bağlantılar: [[00-Home]] · [[01_sirket_master_ana_belgesi]] · [[01_etl_mimarisi]] · [[01_kasa_kurallari]]

Bu belge, [[01_sirket_master_ana_belgesi]] (Company Master V1.0) §10'dan türetilmiş MVP gereksinim önceliğidir. Bağlayıcı kaynak master belgedir; buradaki içerik özet niteliğindedir.

## Kapsam

Ankara B2B şirket evreni için arama, filtreleme ve firma profili görüntüleme. Amaç önceden belirlenmiş firma sayısına ulaşmak değil, **mümkün olan en kapsamlı ve doğrulanabilir Ankara B2B Company Universe** oluşturmaktır.

## P0 — Zorunlu

- company_id
- unvan
- VKN varsa
- il / ilçe
- adres
- web sitesi
- telefon
- sektör
- NACE varsa
- kaynak
- son doğrulama
- entity confidence
- data quality

## P1 — Çok Değerli

- OSB
- ürünler
- üretici/satıcı ilişkisi
- lokasyon türü
- alternatif şirket isimleri

## P2 — Intelligence Hazırlığı

- evidence
- events
- commercial signals
- company state
- momentum

## Kapsam dışı (master §17)

- satın alma tahmini
- bütçe tahmini
- fırsat skoru
- müşteri ürün uyumu
- karar verici tahmini
- satış kazanma tahmini

Bunlar ileride ilgili Intelligence Engine'lerinin sorumluluğudur.

## Kabul ölçütleri (master §16)

- Coverage, Entity Accuracy, Duplicate Rate, Field Completeness, Freshness, Source Reliability, Search Quality, Profile Accuracy, Evidence Coverage
