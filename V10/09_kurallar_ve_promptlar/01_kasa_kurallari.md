# Kasa Kuralları



Bağlantılar: [[09_kurallar_ve_promptlar/README]] · [[README]] · [[00-Home]] · [[01_sirket_master_ana_belgesi]]



Bu belge, V10 kasasının belge yönetimi standartlarını tek yerde toplar. Ayrıntılı klasör açıklamaları için [[README]] geçerlidir; buradaki kurallar özet ve bağlayıcıdır.



## 1. Klasör yapısı



- `00_ana_belgeler/` — Ana proje ve ana bağlam belgeleri

- `01_gereksinimler/` — İş gereksinimleri, kapsamı ve tanım belgeleri

- `02_is_modeli/` — İş akışları, roller, sorumluluklar ve paydaş ilişkileri

- `03_mimari/` — Sistem mimarisi, bileşenler ve veri akışı

- `04_karşılaştırmalar/` — Versiyon veya belge karşılaştırmaları

- `05_versiyonlar/` — Tarihsel veya sürüm bazlı bağlam belgeleri

- `06_arsiv/` — Eski taslaklar ve geçmiş notlar

- `07_referanslar/` — İç ve dış referans belgeleri

- `08-Ajanlar/` — Ajan tanımları ve sorumluluk alanları

- `09_kurallar_ve_promptlar/` — Kasa kuralları, çalışma kuralları ve prompt kütüphanesi

- `templates/` — ADR, Bug, Spec şablonları



## 2. Adlandırma



- Klasör başlıkları Türkçe olmalıdır.

- Dosya isimleri numaralı ve açıklayıcı olmalıdır (`01_...`, `02_...`).

- Sürüm bilgisi dosya içinde ve dosya adında net görünmelidir.



## 3. Yeni belge ekleme sırası



1. Ana belgeyse → `00_ana_belgeler`

2. Gereksinim ise → `01_gereksinimler`

3. İş modeliyse → `02_is_modeli`

4. Mimariyse → `03_mimari`

5. Karşılaştırma ise → `04_karşılaştırmalar`

6. Versiyon ise → `05_versiyonlar`

7. Eski veya geçici belgeyse → `06_arsiv`

8. Referans ise → `07_referanslar`

9. Kural veya prompt ise → `09_kurallar_ve_promptlar`



## 4. Obsidian bağlantı kuralı



Her yeni belge eklendiğinde:



1. Dosyanın başına en az 2 adet bağlantı eklenir.

2. Bağlantılar ana belgeye ve ilişkili belgeye yönlendirilir.

3. Ana belge olarak README, ana bağlam belgesi ve en yakın versiyon / karşılaştırma notu bağlanır.

4. Bağlantı formatı mutlaka `[[README]]` olmalıdır.

5. Her belge en az bir üst bağlamı ve bir ilgili bağlamı göstermelidir.

6. Amaç, graph görünümünü dağıtmadan gezinilebilir tutmaktır.



Örnek:



```md

Bağlantılar: [[README]] · [[01_sirket_master_ana_belgesi]] · [[01_v9_ile_karsilastirma]]

```



## 5. Versiyon ve arşiv



- Geçmiş sürümler ana akışta değil `05_versiyonlar` veya `06_arsiv` altında tutulur.

- Eski belge silinmez; arşive taşınır ve başına arşiv notu eklenir.

