# V10 Master Belgeleri

Bu klasör, proje belgelerinin Türkçe, düzenli ve sürdürülebilir bir yapıda saklanması için hazırlanmıştır.

## Amaç

- Proje bağlamını tek bir yerden takip etmek
- Sistem, iş modeli ve gereksinim belgelerini ayrıştırmak
- Versiyon geçmişini net tutmak
- Yeni belge eklenirken aynı standartların korunmasını sağlamak

## Temel kurallar

- Klasör başlıkları Türkçe olmalıdır.
- Dosya isimleri numaralı ve açıklayıcı olmalıdır.
- Yeni belge eklendiğinde uygun kategoriye yerleştirilmelidir.
- Geçmiş sürümler, ana akışta değil versiyon veya arşiv bölümünde tutulmalıdır.
- Sürüm bilgisi dosya içinde ve dosya adında net şekilde görünmelidir.

## Klasör yapısı

- 00_ana_belgeler/
  - Ana proje ve ana bağlam belgeleri
  - Örnek: 01_sirket_master_ana_belgesi.md
- 01_gereksinimler/
  - İş gereksinimleri, kapsamı ve tanım belgeleri
- 02_is_modeli/
  - İş akışları, roller, sorumluluklar ve paydaş ilişkileri
- 03_mimari/
  - Sistem mimarisi, bileşenler ve veri akışı
- 04_karşılaştırmalar/
  - Versiyon ya da belge karşılaştırmaları
  - Örnek: 01_v9_ile_karsilastirma.md
- 05_versiyonlar/
  - Tarihsel veya sürüm bazlı bağlam belgeleri
  - Örnek: 01_versiyon_6_baglam_dokumani.md
- 06_arsiv/
  - Eski taslaklar ve geçmiş notlar
- 07_referanslar/
  - İç ve dış referans belgeleri

## Yeni belge ekleme prensibi

Yeni bir belge eklenirken aşağıdaki sıra takip edilmelidir:

1. Ana belgeyse 00_ana_belgeler içine
2. Gereksinim ise 01_gereksinimler içine
3. İş modeliyse 02_is_modeli içine
4. Mimariyse 03_mimari içine
5. Karşılaştırma ise 04_karşılaştırmalar içine
6. Versiyon ise 05_versiyonlar içine
7. Eski veya geçici belgeyse 06_arsiv içine
8. Referans ise 07_referanslar içine

## İlişkili belgeler

- [[01_sirket_master_ana_belgesi]]
- [[01_v9_ile_karsilastirma]]
- [[01_versiyon_6_baglam_dokumani]]
- [[01_versiyon_7_baglam_dokumani]]
- [[01_versiyon_8_baglam_dokumani]]
- [[01_versiyon_9_baglam_dokumani]]
- [[00-Home]]

## Obsidian bağlantı kuralı

Her yeni belge eklendiğinde şu standart uygulanmalıdır:

1. Dosyanın başına en az 2 adet bağlantı eklenir.
2. Bağlantılar, ana belgeye ve ilişkili belgeye yönlendirilir.
3. Ana belge olarak README, ana bağlam belgesi ve en yakın versiyon / karşılaştırma notu bağlanır.
4. Bağlantı formatı mutlaka Obsidian link formatında olmalıdır: `[[README]]`
5. Her belge, en azından bir üst bağlamı ve bir ilgili alt bağlamı göstermelidir.
6. Bu kural, graph görünümünü dağınık hale getirmemek için uygulanır.

Örnek kullanım:

```md
Bağlantılar: [[README]] · [[01_sirket_master_ana_belgesi]] · [[01_v9_ile_karsilastirma]]
```

## Not

Bu dizin yapısı, belge yönetimini sade, anlaşılır ve genişletilebilir tutar. Yeni dosya eklendikçe aynı standart korunur.
