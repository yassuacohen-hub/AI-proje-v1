# Huginn Data Insights — Rekabet Analizi
**Rapor tarihi:** 14 Eylül 2026  
**Kapsam:** Doğrudan/dolaylı rakipler, sektör yoğunluğu, fiyat konumu ve stratejik öncelikler
## 1. Yönetici özeti
- Huginn'in savunulabilir alanı; OSB/imalat verisini ticari niyet, yetenek, tedarikçi eşleşmesi ve kanıt görünürlüğüyle birleştiren dikey ticari istihbarattır.
- 5.665 şirketin %56,52'si ilk beş sektörde toplanır; otomotiv, yapı/inşaat, makine, metal ve iş makinaları öncelikli adreslenebilir segmentlerdir.
- Ortalama tamamlama skoru 47,63'tür; VKN %0, NACE %11,84, telefon %11,33 ve OSB parseli %0,04 düzeyindedir.
- Organizasyon bazlı demo paketleri, kullanıcı başı fiyatlanan LinkedIn, HubSpot ve Zoho karşısında belirgin fiyat avantajı sağlar.
- Aktif kampanyalar %6,31 CTR, %3,27 CVR ve dönüşüm başına 170,73 TL üretir; en iyi CPA 147,06 TL ile teknoloji kampanyasındadır.
- Öncelik, düşük fiyat değil; eksik ve parçalı veriyi doğrulanmış, gerekçeli ve aksiyon alınabilir ticari sinyale dönüştürmektir.
## 2. Kapsam, yöntem ve sınırlar
- `multi_osb_merged.jsonl`: 5.665 şirket; sektör, OSB ve veri tamamlama alanları.
- `market_brain.py`: sektör payı, rekabet yoğunluğu ve çalışan bazlı üst şirket mantığı.
- `paketler.py` ve demo paket kayıtları: Temel, Standart, Profesyonel, Kurumsal ve ek giriş paketi Değer.
- `pazarlama.py`, kampanya ve segment demo kayıtları: hedefleme, bütçe, CTR, CVR ve CPA.
- Dış fiyat referansları: LinkedIn Sales Navigator, Kompass, Apify, HubSpot, Zoho ve Creditsafe resmî sayfaları.
- Dönüştürmelerde 1 Eylül 2026 TCMB satış kurları kullanıldı: 1 USD = 48,2759 TL; 1 EUR = 55,9776 TL.
**Veri sınırı:** Belirtilen `src/company_master/orchestrator/paketler.py` mevcut değildir; fiyat CRUD servisi `src/company_master/paketler.py`, fiyat tohumu `data/demo/paketler_demo.jsonl` konumundadır. Birleşik JSONL'de çalışan ve ciro alanları bulunmadığından pazar payı şirket adediyle, fiyat karşılaştırması demo katalogla yapılmıştır.
## 3. Doğrudan rakipler
Doğrudan rakipler aynı B2B karar vericiye şirket keşfi, kurumsal veri, ticari sinyal veya tedarikçi/satış istihbaratı sunar.

| Rakip tipi | Temsilî örnekler | Rakip avantajı | Rakip zayıflığı |
|---|---|---|---|
| OSB ve oda rehberleri | OSTİM, ASO | Yerel güven ve erişim | Statik kayıt; sinyal, API ve eşleşme zayıf |
| B2B veri platformları | Kompass | Geniş katalog, sınıflama ve doğrulama | OSB/üretim yeteneği ayrıştırma derinliği sınırlı |
| Sales intelligence | LinkedIn Sales Navigator | Kişi ağı, karar verici ve CRM entegrasyonu | Üretim yeteneği ve HS/iş eşleşmesi yok |
| Kredi ve risk istihbaratı | Creditsafe, D&B tipi sağlayıcılar | Finansal skor ve rapor geleneği | Anlık satın alma niyeti ve saha yeteneği odağı sınırlı |
| İhale ve iş gücü sinyal agregatörleri | EKAP, Kariyer.net, İŞKUR tipi çözümler | Güncel işlem ve ilan verisi | Eşleştirme ve fırsat yorumu kullanıcıya kalıyor |
| OSINT ve veri danışmanlığı | Özel çözüm üreticileri | Esnek kaynak ve entegrasyon | Standart SLA, skor ve tekrarlanabilirlik zayıf |

**Sonuç:** Kompass ve OSB rehberleri veri erişiminde, LinkedIn karar verici ağında, kredi raporlayıcılar risk tarafında güçlüdür. Huginn bu katmanları OSB/imalat varlığı ve ticari niyet kararı etrafında birleştirmelidir.
## 4. Dolaylı rakipler

| Rakip tipi | Temsilî örnekler | Aynı ihtiyacı nasıl karşılar | Huginn'e tehdit |
|---|---|---|---|
| CRM ve satış otomasyonu | HubSpot, Salesforce, Zoho | Lead, pipeline ve iletişimi yönetir | Mevcut iş akışını koruyarak veri ihtiyacını içeri emer |
| No-code kazıma | Apify ve benzerleri | Müşteri kendi veri akışını kurar | Veri toplama bütçesini platforma kaydırır |
| BI, ERP ve gelişmiş Excel | Power BI, SAP/Logo/CANIAS | Mevcut veriyi raporlar ve işletir | İçerideki veri varsa ek istihbarat ihtiyacını azaltır |
| Arama ve sosyal ağlar | Google, LinkedIn, sektörel gruplar | Manuel firma ve kişi araştırması | Basit keşfi düşük nakit maliyetle karşılar |
| İş ilanı platformları | LinkedIn Jobs, Kariyer.net, İŞKUR | Büyüme ve işe alım sinyali sağlar | Niyet sinyali bileşenine alternatif olur |
| Danışmanlık ve saha doğrulama | Oda ve özel denetim firmaları | Proje bazlı güvenilir içgörü | Yüksek dokunuşlu kurumsal satın almaları kazanır |

**Sonuç:** CRM/BI “çalışma sistemi”, kazıma araçları “veri üretim sistemi” olarak bütçeyi ele geçirir. Huginn hazır entegrasyon ve kanıtlı karar çıktısı vermezse veri kaynağına indirgenebilir.
## 5. Rekabet manzarası ve sektör payı
Paylar 5.665 şirketlik örneklemde şirket adedine göredir; ulusal ciro veya kapasite pazar payı değildir. Kaynak sektör kodları temizlenerek 58 grup elde edilmiştir.

| Sektör | Şirket | Pay | Yoğunluk | Ort. tamamlama |
|---|---:|---:|---|---:|
| Otomotiv | 932 | %16,45 | Yüksek | 46,21 |
| Yapı ve İnşaat | 709 | %12,52 | Yüksek | 47,74 |
| Makine ve Makine Ekipmanları | 576 | %10,17 | Yüksek | 48,33 |
| Metal ve Metal İşleme | 509 | %8,98 | Yüksek | 47,59 |
| İş Makinaları | 476 | %8,40 | Yüksek | 47,06 |
| Çeşitli Ticari Faaliyetler | 395 | %6,97 | Yüksek | 46,67 |
| Hizmetler | 304 | %5,37 | Yüksek | 47,83 |
| Elektrik ve Elektronik | 284 | %5,01 | Yüksek | 47,90 |
| Teknik Malzeme, Tezgah ve Ekipman | 235 | %4,15 | Yüksek | 47,98 |
| Teknoloji ve Bilişim | 131 | %2,31 | Orta | 48,13 |
| Ambalaj, Kağıt, Baskı ve Kırtasiye | 93 | %1,64 | Orta | 47,69 |
| Gıda ve Endüstriyel Mutfak | 87 | %1,54 | Orta | 47,13 |

- İlk beş sektör %56,52, ilk on iki sektör %83,51 pay alır.
- 58 sektör için HHI 822'dir; şirket adedi bazında düşük yoğunlaşma ve çok sektörlü adreslenebilir pazar görünümü vardır.
- OSTİM 4.994 şirketle %88,16, ASO 671 şirketle %11,84 paydadır; örneklem kaynak dağılımı dengeli değildir.
- `competitive_analysis()` 200+ şirketi yüksek, 50-199 şirketi orta, daha düşük sayıları düşük yoğunlukta sınıflandırır.
### Veri kalitesi rekabet bariyeri

| Gösterge | Dolu kayıt | Oran | Rekabet anlamı |
|---|---:|---:|---|
| Ortalama tamamlama skoru | 47,63/100 | - | Ham katalogdan istihbarata geçişte temel açık |
| E-posta | 3.048 | %53,80 | Orta erişilebilirlik |
| Telefon | 642 | %11,33 | Satış aktivasyonu için ciddi eksik |
| VKN | 0 | %0,00 | Kesin varlık eşleştirme yapılamaz |
| NACE | 671 | %11,84 | Sektör standardizasyonu zayıf |
| Ticaret sicil no | 671 | %11,84 | Kurumsal doğrulama sınırlı |
| Jenerik web adresi | 2.438 | %43,04 | Kaynak kalitesi ve domain güveni riski |
| OSB parseli | 2 | %0,04 | Konum ve kapasite bağlamı eksik |

## 6. Fiyat konumu
Demo katalogda dört ana pakete ek olarak 499 TL'lik Değer paketi bulunur. Fiyatlar KDV hariç ve aylıktır.

| Paket | Aylık fiyat | Kullanıcı | Günlük API | Kapsam |
|---|---:|---:|---:|---|
| Değer | 499 TL | 3 | 500 | Giriş seviyesi API ve depolama |
| Temel | 999 TL | 5 | 1.000 | Küçük ekipler için temel erişim |
| Standart | 2.999 TL | 25 | 50.000 | Raporlama ve orta ölçekli ekip |
| Profesyonel | 7.999 TL | 100 | 500.000 | API analitiği ve özel destek |
| Kurumsal | 19.999 TL | Sınırsız | Sınırsız | SLA %99,9 ve öncelikli destek |

- Fiyat artışları: Değer→Temel %100,2; Temel→Standart %200,2; Standart→Profesyonel %166,7; Profesyonel→Kurumsal %150.
- API birim maliyeti Değer/Temel'de yaklaşık 0,999 TL/işlem, Standart'ta 0,060 TL, Profesyonel'de 0,016 TL'dir.
- Beş demo firma kartında paket atamaları ciro ve çalışanla artar; ancak örneklem fiyat eşiği belirlemek için yetersizdir.
### Dış fiyat referansı

| Rakip / paket | Liste fiyatı | Yaklaşık TL | Fiyatlama birimi |
|---|---:|---:|---|
| LinkedIn Sales Navigator Core | 119,99 USD | 5.793 TL | Kullanıcı/ay |
| LinkedIn Sales Navigator Advanced | 159,99 USD | 7.724 TL | Kullanıcı/ay |
| Kompass KSales | 59 EUR | 3.303 TL | Aylık başlangıç |
| Kompass EasyBusiness | Özel teklif | - | Kullanıcı, ülke ve veri hacmi |
| Apify Starter | 19 USD | 917 TL | Platform/ay + kullanım |
| Apify Scale | 199 USD | 9.607 TL | Platform/ay + kullanım |
| HubSpot Sales Hub Starter | 15 USD | 724 TL | Kullanıcı/ay |
| Zoho CRM Standard | 20 USD | 966 TL | Kullanıcı/ay |
| Creditsafe | Özel teklif | - | Rapor/paket kullanımı |

**Konum:** Temel paket 5 kullanıcıya 999 TL ile kişi başı yaklaşık 200 TL sağlar ve kişi başı fiyatlanan rakiplerin çok altındadır. Standart paket Kompass başlangıç seviyesine yakın, LinkedIn Core'un belirgin altındadır. Profesyonel paket 100 kullanıcı dahil edildiğinde güçlü değer sunar. Kurumsal fiyatı ancak SLA, entegrasyon, doğrulanmış veri ve özel model yetenekleri paketin parçasıysa savunulabilir.
**Paket zayıflığı:** Özellikler ağırlıklı olarak kullanıcı, depolama ve API kotasıdır; HS eşleşmesi, ticari niyet, tedarikçi skoru, kanıt görünürlüğü ve model SLA'sı fiyat metriklerine bağlanmamıştır.
## 7. Rakip tiplerine göre güçlü ve zayıf yanlar

| Rakip tipi | Güçlü yan | Zayıf yan | Huginn'in karşılığı |
|---|---|---|---|
| OSB/oda rehberleri | Yerel güven | Statik ve düşük otomasyon | Canlı sinyal, API ve eşleşme skoru |
| B2B veri platformları | Geniş ve sınıflı katalog | Dikey üretim bağlamı sınırlı | NACE/HS/yetkinlik ve OSB derinliği |
| Sales intelligence | Karar verici ağı ve CRM | Üretim/tedarik zinciri bağlamı eksik | Hesap sinyali ile kişi ve yeteneği birleştirme |
| Risk/kredi sağlayıcıları | Finansal skor | İleriye dönük niyet zayıf | Niyet, zamanlama ve kanıt katmanları |
| Sinyal agregatörleri | Güncel resmi veri | Parçalı ve yorumsuz | Varlık çözme ve fırsat kapıları |
| CRM/BI/ERP | Yerleşik iş akışı | Dış niyet üretmez | Çift yönlü entegrasyon ve karar çıktısı |
| No-code kazıma | Esneklik ve kontrol | Kurulum, proxy ve bakım yükü | Yönetilen, izinli ve kalite kapılı akış |

## 8. Kampanya ve segment kanıtları
- 5 kampanyanın 3'ü aktif, 1'i taslak, 1'i inceleme aşamasındadır.
- Aktif kampanyalar: 105.000 TL bütçe, 298.000 gösterim, 18.800 tıklama ve 615 dönüşüm.
- Aktif kampanya CTR'si %6,31, CVR'si %3,27 ve CPA'sı 170,73 TL'dir.
- En iyi sonuç 147,06 TL CPA ve %4,00 CVR ile teknoloji karşılama kampanyasındadır.
- İnşaat kampanyası 375 TL CPA ile zayıftır; taslak kurumsal kampanyanın 80.000 TL bütçesi vardır fakat teslimatı sıfırdır.
- Kampanya ve segment adları yalnızca 1/5 oranında tam eşleşir; pasif inşaat segmenti ile incelemedeki kampanya uyumsuzdur.
## 9. Stratejik öneriler
1. **Veri kalitesini ürüne çevirin:** 90 günde VKN, NACE, telefon ve gerçek web sitesi doluluğunu artırın; her değere kaynak ve güven katmanı ekleyin.
2. **Taksonomiyi standartlaştırın:** OSTİM etiketleri ile ASO meslek gruplarını NACE Rev.2 eşlemesine taşıyın ve sürümlenen çapraz referans kullanın.
3. **Çalışan ve ciroyu kanıtlı açın:** Eksik değerlerde kaynak, tahmin yöntemi ve güven aralığını gösterin; tahmini değeri gerçek gibi sunmayın.
4. **Dikey farkı paketleyin:** HS ikamesi, tedarikçi yetkinliği, ihale/iş ilanı niyeti, kanıt skoru ve karar gerekçesini görünür metrik yapın.
5. **Sonuç birimiyle fiyatlayın:** API yanında doğrulanmış firma, aktif sinyal ve eşleşme kredisi kotaları tanımlayın; depolamayı ikincil tutun.
6. **Dört paketi netleştirin:** Temel giriş, Standart KOBİ ölçeklenme, Profesyonel yoğun API, Kurumsal SLA ve özel entegrasyon katmanı olsun.
7. **Değer avantajını koruyun:** Organizasyon bazlı fiyatlamayı sürdürün; Kurumsal hacmi tekliflendirirken uygulama ve destek maliyetlerini ayırın.
8. **Segment şemasını düzeltin:** Serbest metin yerine `segment_id` kullanın; eşleşmeyen, pasif veya kriter dışı segmentleri otomatik engelleyin.
9. **Bütçeyi kanıta kaydırın:** Kurumsal kampanyayı yayına almadan büyük bütçe ayırmayın; inşaat CPA'sını 170 TL altına indirmeden ölçeklendirmeyin.
10. **Rakip satış kartları kurun:** Kompass'a karşı OSB/NACE/HS, LinkedIn'e karşı üretim niyeti, CRM'e karşı entegrasyon, Apify'a karşı yönetilen kalite mesajını kullanın.
## 10. Kaynaklar ve notlar
- İç kaynaklar: `data/merged/multi_osb_merged.jsonl`, `market_brain.py`, `paketler.py`, `pazarlama.py`, `kampanya_demo.jsonl`, `firma_karti_demo.jsonl`.
- Ürün sınırları: V9 ana bağlam; EKAP, iş ilanı, ticari niyet, kanıt ve belirsizlik prensipleri.
- Dış referanslar: LinkedIn, Kompass, Apify, HubSpot, Zoho ve Creditsafe resmî fiyat/ürün sayfaları.
- Dış fiyatlar 14 Eylül 2026'da erişilen liste fiyatlarıdır; KDV, bölge fiyatı, indirim ve sözleşme koşulları dahil değildir.
