[[Huginn Data Insights/data/orchestrator/AR-03_kullanici_persona_yol_haritasi.md]]

# Huginn Data Insights — Kullanıcı Persona ve Yol Haritası

**Doküman:** AR-03  
**Tarih:** 2026-09-14  
**Amaç:** Segment, paket, kampanya ve önbellek verilerine dayalı kullanıcı odaklı büyüme, benimseme ve elde tutma planı.  
**Kapsam:** Demo veri seti üzerinden persona hipotezleri ve ölçülebilir ürün aksiyonları; gerçek kullanıcı davranışı yerine doğrulama bekleyen hipotezler içerir.

## 1. Veri tabanı ve karar bağlamı

- **Firma kartları:** 5 firma, toplam 46,5 milyon TL ciro ve 1.075 çalışan; firma başına ortalama 9,3 milyon TL ciro ve 215 çalışan.
- **Paket dağılımı:** Temel 2 firma (%40), Standart 1 firma (%20), Profesyonel 1 firma (%20), Kurumsal 1 firma (%20).
- **Çalışan başına ciro:** Temel firmalarda yaklaşık 33.333–37.500 TL, Standart firmada 33.333 TL, Profesyonel firmada 40.000 TL, Kurumsal firmada 50.000 TL.
- **Kampanya havuzu:** 3 aktif kampanya 298.000 gösterim, 18.800 tıklama, 615 dönüşüm ve 105.000 TL bütçe üretmiştir; gösterim-tıklama oranı %6,31, tıklama-dönüşüm oranı %3,27, bütçe başına dönüşüm maliyeti 170,73 TL'dir.
- **Tüm yürütülmüş kampanyalar:** 354.000 gösterim, 22.600 tıklama, 735 dönüşüm ve 230.000 TL bütçe; gösterim-tıklama oranı %6,38, tıklama-dönüşüm oranı %3,25, bütçe başına dönüşüm maliyeti 312,93 TL'dir.
- **Kampanya durumu:** CMP-003 (Enerji) taslak ve sıfır teslimat; CMP-005 (İnşaat) incelemede; CMP-004'ün bitiş tarihi 2026-08-31 olmasına rağmen hâlâ aktif görünmektedir.
- **Segmentasyon kaynakları:** `segment_demo.jsonl` segment kriterlerini; `market_brain.py` sektör sayımı, pazar büyüklüğü, rekabet analizi ve trend sektör skorlarını sağlar.
- **Paket ve cache kaynakları:** `paketler.py` paket-katalog ve firma-paket ilişkisini; `caching.py` Redis/in-memory fallback, 30–300 saniyelik TTL ve prefix ile geçersiz kılma politikasını tanımlar.
- **Veri kalitesi notu:** İstenen paket fiyatları Temel 499 TL, Standart 2.999 TL, Profesyonel 7.999 TL ve Kurumsal 19.999 TL olarak esas alınmıştır. Demo paket kataloğunda Temel 999 TL ve ek “Değer” 499 TL kaydı bulunduğundan fiyat katalogu ürün kararıyla tutarlı hâle getirilmelidir.
- **Eşleşme notu:** E-ticaret firmasının cirosu 1,5 milyon TL iken “E-ticaret Buyuk” kriteri 5 milyon TL ister; turizm kartında premium alanı yoktur; inşaat segmenti pasiftir. Bu kayıtlar segment eligibility ve aktivasyon akışında düzeltilmelidir.

## 2. Kullanıcı personası

### Persona 1 — Büyüme ve Pazarlama Lideri: B2B Teknoloji

- **Temsili firma:** Ankara Teknoloji A.Ş.; 5 milyon TL ciro, 150 çalışan, Standart paket.
- **Segment sinyali:** B2B Teknoloji; teknoloji sektörü, B2B firma tipi ve minimum 1 milyon TL hacim kriteri.
- **Rol ve bağlam:** Pazarlama bütçesini nitelikli fırsat ve kısa satış döngüsü ile ilişkilendirmekle sorumludur; satış, ürün ve yönetici raporlarını tek bakışta görmek ister.
- **Ana hedefler:** Yüksek niyetli B2B hesaplar bulmak, kampanya verimliliğini artırmak, rakip hareketlerini erken görmek ve paket değerini ciro ile kanıtlamak.
- **Başarı metrikleri:** Nitelikli fırsat sayısı, kampanya dönüşüm oranı, fırsat başına maliyet, rakip izleme sıklığı ve aylık aktif kullanıcı.
- **Davranış hipotezi:** 6,80% gösterim-tıklama ve %4,00 tıklama-dönüşüm oranıyla en güçlü demo kampanya sinyalini verir; raporlama ve API limitleri büyüdükçe Profesyonel pakete geçebilir.
- **Ürün beklentisi:** Sektör trendi, rekabet analizi, kampanya hunisi, KPI özeti ve 60 saniyelik güncel dashboard.

### Persona 2 — Dijital Büyüme Operasyon Yöneticisi: E-ticaret

- **Temsili firma:** Istanbul Yazilim Ltd.; 1,5 milyon TL ciro, 45 çalışan, Temel paket.
- **Segment sinyali:** Kart “E-ticaret” olarak işaretlenmiştir; ancak “E-ticaret Buyuk” segmenti minimum 5 milyon TL hacim şartı koşar.
- **Rol ve bağlam:** Sınırlı bütçeyle kanal performansı, stok/kampanya zamanlaması ve hızlı dönüşüm iyileştirmeleri arasında denge kurar.
- **Ana hedefler:** Düşük maliyetli trafik kazanmak, kampanya dönüşümünü yükseltmek, çalışan başına verimi izlemek ve gereksiz paket maliyetinden kaçınmak.
- **Başarı metrikleri:** Tıklama başına maliyet, dönüşüm oranı, kampanya başına bütçe kullanımı, 30 günlük aktif kullanım ve Temel→Standart yükseltme niteliği.
- **Davranış hipotezi:** 6,33% gösterim-tıklama ve %2,90 tıklama-dönüşüm oranı, mesaj/landing page iyileştirmesi için yeterince güçlü bir taban sunar.
- **Ürün beklentisi:** Hazır segment şablonu, basit kampanya raporu,限额 aşım uyarısı ve paket karşılaştırma; segment uygunluk hatası kullanıcıya açıklanmalıdır.

### Persona 3 — Strateji ve Kurumsal Geliştirme Direktörü: Enerji

- **Temsili firma:** Anadolu Enerji A.Ş.; 12 milyon TL ciro, 300 çalışan, Profesyonel paket.
- **Segment sinyali:** Enerji sektörü ve minimum 5 milyon TL hacim kriteri; firma kriteri karşılar.
- **Rol ve bağlam:** Yeni pazar, regülasyon, tedarik ve rekabet sinyallerini yönetim kuruluna kanıtlı biçimde sunar.
- **Ana hedefler:** Pazar büyüklüğü ve trend skorunu izlemek, rakip yoğunluğunu anlamak, kurumsal rapor üretmek ve destekle hızlı sorun çözmek.
- **Başarı metrikleri:** Rapor paylaşımı, kanıtlı fırsat oranı, veri tazelik skoru, API analitik kullanımı ve yönetici benimseme oranı.
- **Davranış hipotezi:** CMP-003 taslak olduğu için teslimat yoktur; önce küçük pilot ve ölçüm planı açılmalı, ardından Profesyonel→Kurumsal genişleme değerlendirilmelidir.
- **Ürün beklentisi:** Market Brain pazar büyüklüğü, trend sektörler, rekabet analizi, API analitiği, özel destek ve 300 saniyelik API-kullanım görünümü.

### Persona 4 — Gelir ve Talep Yöneticisi: Turizm Premium

- **Temsili firma:** Deniz Turizm A.Ş.; 3 milyon TL ciro, 80 çalışan, Temel paket.
- **Segment sinyali:** Turizm segmenti; “premium” niteliği firma kartında doğrulanmamıştır.
- **Rol ve bağlam:** Mevsimsel talebi erken yakalar, kampanya takvimini doldurur ve gelir yöneticisine uygulanabilir öneri verir.
- **Ana hedefler:** Sezon öncesi talep yaratmak, kampanya bitiş ve bütçe durumunu takip etmek, düşük performanslı kanalları hızla ayırmak.
- **Başarı metrikleri:** Sezon başı aktivasyon, dönüşüm oranı, kampanya sonlandırma doğruluğu, tekrar kullanım ve sezonluk yenileme.
- **Davranış hipotezi:** 5,47% gösterim-tıklama ve %2,32 tıklama-dönüşüm oranı demo içinde en düşük dönüşüm seviyesidir; segment doğrulaması ve kreatif test önceliklidir.
- **Ürün beklentisi:** Mevsimsel segment şablonu, kampanya durumu uyarısı, basit raporlama ve düşük bütçeli Temel paket kontrolü.

### Persona 5 — Kurumsal Satın Alma ve İş Geliştirme Lideri: İnşaat Yüksek

- **Temsili firma:** Yapı Merkezi A.Ş.; 25 milyon TL ciro, 500 çalışan, Kurumsal paket.
- **Segment sinyali:** İnşaat ve minimum 10 milyon TL hacim kriteri karşılanır; segment kaydının `is_active=false` olması ticari akışı bloke eder.
- **Rol ve bağlam:** Büyük hacimli tedarik, alt yüklenici ve pazar fırsatlarını çok kaynaklı kanıtlarla değerlendirir; servis kesintisine tahammülü düşüktür.
- **Ana hedefler:** Güvenilir pazar ve rakip istihbaratı, yüksek API kapasitesi, SLA, öncelikli destek ve denetlenebilir karar süreci.
- **Başarı metrikleri:** Kuruluş geneli aktivasyon, API kullanım oranı, SLA uygunluğu, fırsat başına kanıt sayısı ve yenileme/nps.
- **Davranış hipotezi:** 6,79% gösterim-tıklama ve %3,16 tıklama-dönüşüm oranı ilgiyi gösterir; incelemedeki CMP-005 ve pasif segment nedeniyle karar aşaması gecikir.
- **Ürün beklentisi:** Sınırsız kullanıcı/API, 99,9% SLA, özel güncelleme, öncelikli destek, performans dashboard'u ve 30 saniyelik cache freshness göstergesi.

## 3. Kullanıcı yolculuğu haritası

| Aşama | Kullanıcı ihtiyacı ve soru | Temas noktası / içerik | Ürün aksiyonu | Ölçülebilir başarı sinyali |
|---|---|---|---|---|
| **Farkındalık** | “Bu platform benim segmentimde fırsat bulur mu?” | Sektör trendi, pazar büyüklüğü, örnek başarı hikâyesi, segment bazlı kampanya | Market Brain ile sektör sayısı ve trend skoru göster; anonim/self-servis pazarlama kancası sun | Kampanya CTR, segment sayfası görüntüleme, demo talep oranı |
| **Değerlendirme** | “Veri güvenilir mi ve hangi paket yeterli?” | Segment kriteri, firma kartı, rekabet analizi, paket karşılaştırma | Uygunluk sonucunu ve eksik alanları göster; Temel/Standart/Profesyonel/Kurumsal eşleştirmesi yap | Paket sayfası tamamlama, demo tamamlama, uygunluk doğrulama oranı |
| **Karar** | “Yatırımın geri dönüşü nedir?” | Kampanya hunisi, bütçe/dönüşüm, SLA, API limitleri, referans | Kısa pilot, başarı kriteri ve karar defteri oluştur; CMP-003/CMP-005 için durum engellerini kaldır | Pilot başlatma, satın alma, karar süresi, ilk değerli aksiyon |
| **Benimseme** | “İlk faydayı ne zaman göreceğim?” | Hoş geldin akışı, hazır dashboard, segment kaydı, kampanya şablonu | 7 günlük onboarding; KPI, rapor, API ve cache freshness eğitimini rol bazlı aç | 7/30 gün aktivasyon, ilk rapor, ilk API çağrısı, ilk kampanya |
| **Sadakat** | “Platform büyümeme ve karar kaliteme katkı sağlıyor mu?” | Aylık değer raporu, yenilik bülteni, kullanım ve destek incelemesi | Düşük kullanım, segment bozukluğu ve paket limiti tetiklerini yakala; QBR ve yükseltme öner | 30/90 gün elde tutma, genişleme MRR, destek yanıtı, NPS |

- **Farkındalıkta öncelik:** B2B Teknoloji kampanyası %6,80 CTR ile referans kreatif/segment kombinasyonu olabilir; Turizm’in %5,47 CTR ve %2,32 dönüşümü ayrı test gerektirir.
- **Değerlendirmede öncelik:** Segment kriteri ile firma kartı arasındaki üç uyumsuzluğu (E-ticaret hacmi, Turizm premium alanı, İnşaat aktifliği) kullanıcıya şeffaf göster.
- **Karar anında öncelik:** Enerji kampanyası taslakken satış vaadi sunma; önce ölçüm planı ve küçük pilot ile kanıt üret.
- **Benimsemede öncelik:** Temel paket kullanıcılarına ilk raporu 7 günde, Profesyonel/Kurumsal kullanıcılara ilk API ve yönetici raporunu 14 günde teslim et.
- **Sadakatte öncelik:** 30–300 saniyelik cache TTL’lerini ekranda “son güncelleme” ile göster; veri değişiminde prefix invalidation çalıştığını doğrula.

## 4. Personaya göre ağrı noktaları

| Persona | Ağrı noktası | Kanıt / etki | Öncelikli çözüm |
|---|---|---|---|
| B2B Teknoloji | Raporlar ile satış çıktısı arasında bağ eksikliği | En yüksek demo dönüşüm oranı %4,00; fırsat kalitesi izlenmiyor | Kampanya dönüşümünü nitelikli fırsat ve paket kullanımına bağla |
| E-ticaret | Segment uygunluğu ve bütçe belirsizliği | 1,5 milyon TL firma, 5 milyon TL büyük segment kriterinin altında | eligibility kontrolü, düşük bütçe uyarısı, Temel paket limiti |
| Enerji | Taslak kampanya ve kanıt eksikliği | CMP-003 sıfır gösterim/tıklama/dönüşüm | Pilot yayını, ölçüm planı, kanıt ve güven skoru |
| Turizm | Mevsimsel durum ve segment doğrulaması | Kampanya bitmiş ancak aktif; premium alanı yok | tarih durumu senkronizasyonu, premium doğrulama, sezon takvimi |
| İnşaat Yüksek | Pasif segment ve inceleme kuyruğu | CMP-005 review; segment `is_active=false` | segment aktivasyon onayı, SLA ve karar zamanı takibi |

## 5. Özellik benimseme matrisi

**Not:** Aşağıdaki matris demo veriden türetilmiş hedef benimsemedir; gerçek event log yoktur. `●` çekirdek, `◐` destekleyici, `○` sonraki faz, `—` düşük öncelik.

| Özellik | B2B Teknoloji | E-ticaret | Enerji | Turizm | İnşaat Yüksek |
|---|:---:|:---:|:---:|:---:|:---:|
| Segment bazlı firma keşfi (`sector_count`) | ● | ● | ◐ | ◐ | ● |
| Pazar büyüklüğü tahmini (`market_size_estimate`) | ◐ | ○ | ● | ○ | ● |
| Rekabet analizi (`competitive_analysis`) | ● | ◐ | ● | ○ | ● |
| Trend sektör skoru (`trending_sectors`) | ● | ◐ | ● | ◐ | ◐ |
| Kampanya gösterim/tıklama/dönüşüm hunisi | ● | ● | ◐ | ● | ◐ |
| Paket karşılaştırma ve çapraz satış | ◐ | ● | ◐ | ● | ◐ |
| KPI özeti (`/api/kpi`, TTL 60 sn) | ● | ● | ● | ● | ● |
| Raporlama | ● | ◐ | ● | ◐ | ● |
| API kullanım analitiği (TTL 300 sn) | ◐ | ○ | ● | ○ | ● |
| Performans ve cache sağlığı (TTL 30 sn) | ◐ | ○ | ● | ○ | ● |
| Özel destek / SLA | ○ | — | ● | — | ● |

- **Temel:** Segment keşfi, KPI ve temel kampanya raporu; API 500 işlem/gün ve 3 kullanıcı olarak konumlandırılmalıdır.
- **Standart:** Raporlama, 25 kullanıcı ve 50.000 işlem/gün; büyüme sinyali veren B2B ve E-ticaret için ana basamak.
- **Profesyonel:** API analitiği, raporlama, 100 kullanıcı ve özel destek; Enerji gibi kanıt ve yönetici raporu isteyen segmentlerde çekirdektir.
- **Kurumsal:** Sınırsız kullanıcı/API, 99,9% SLA, özel güncelleme ve öncelikli destek; İnşaat Yüksek gibi yüksek hacimli ve düşük toleranslı hesaplarda zorunludur.
- **Cache etkisi:** KPI ve bekleme listesi 60 sn, API kullanımı/kategoriler 300 sn, performans 30 sn cachelenir. Karar ekranlarında tazelik etiketi ve değişim sonrası invalidation görünmelidir.

## 6. Elde tutma stratejisi

| Persona | Tetikleyici | Müdahale | Başarı ölçütü |
|---|---|---|---|
| B2B Teknoloji | 14 gün rapor açılmaması veya CTR düşüşü | Haftalık fırsat bülteni, rakip ve trend özeti, Standart→Profesyonel değer simülasyonu | 30 gün aktiflik, rapor paylaşımı, yükseltme niteliği |
| E-ticaret | API limitinin %80’i veya segment reddi | Limit uyarısı, kampanya şablonu, uygun segment alternatifi ve 30 günlük koçluk | İlk kampanya, limit aşım önleme, Temel→Standart |
| Enerji | Taslak kampanya veya kanıt eksikliği | 2 haftalık pilot, yönetici raporu, özel destek toplantısı ve API analitik onboarding | Pilot dönüşümü, ilk kanıtlı fırsat, Kurumsal genişleme |
| Turizm | Sezon dışı kampanya veya düşük dönüşüm | Mevsim takvimi, bitiş tarihi senkronizasyonu, kreatif A/B testi ve yenileme hatırlatıcısı | Sezon başı aktivasyon, dönüşüm iyileşmesi, sezon yenileme |
| İnşaat Yüksek | API/SLA riski veya review kuyruğu | QBR, öncelikli destek, segment aktivasyon onayı, kuruluş içi eğitim | 90 gün elde tutma, SLA uyumu, genişleme MRR |

## 7. Büyüme fırsatları

1. **Segment veri kalitesini ürün kapısına bağlayın:** 5 segmentten 3’ünde uyumsuzluk veya pasiflik vardır. Eligibility skoru, eksik alan açıklaması ve onay akışı eklenirse karar güveni artar.
2. **B2B Teknoloji kampanyasını ölçeklendirin:** %6,80 CTR ve %4,00 tıklama-dönüşüm oranı demo içinde en güçlü kombinasyondur; kreatif, kanal ve segment varyasyonlarıyla nitelikli fırsat maliyetini ölçün.
3. **Enerji için kanıtlı pilot açın:** 80.000 TL bütçeli CMP-003 tamamen taslaktır. Küçük yayın, net dönüşüm olayı ve Market Brain raporunu birleştiren pilot, Profesyonel değerini doğrular.
4. **Turizm’de mevsimsel otomasyon kurun:** Bitmiş kampanyanın aktif kalması operasyon güvenini zedeler. Tarih durumu, bütçe ve segment niteliği için otomatik kontrol eklenirse tekrar kullanım artar.
5. **İnşaat Yüksek segmentini ticari akıma alın:** 25 milyon TL ciro ve 500 çalışanla en yüksek çalışan başına ciro (50.000 TL) bu firmadadır. Pasif segment ve review durumu kaldırıldığında Kurumsal genişleme potansiyeli yüksektir.
6. **Paket basamaklarını kullanım sinyaline göre önerin:** Temel firmalar toplam firmanın %40’ıdır; çalışan başına ciro 33.333–37.500 TL aralığındadır. API limiti, rapor paylaşımı ve ekip büyümesi sinyalleriyle Standart/Profesyonel yükseltme önerisi üretin.
7. **Cache’i güven unsuru hâline getirin:** 30–300 sn TTL’li KPI, API kullanımı ve performans verilerini “son güncelleme”, cache durumu ve manuel yenileme ile gösterin; stale karar riskini azaltın.
8. **90 günlük büyüme hedefi önerisi:** Segment uygunluğu doğrulama %95+, ilk 7 gün aktivasyon %70+, 30 gün elde tutma %80+, aktif kampanya dönüşüm oranı %3,5+ ve Kurumsal/Profesyonel genişleme MRR’si pozitif olarak izlensin.

## 8. Kaynaklar ve izlenebilirlik

- `src/company_master/intelligence/market_brain.py`: sektör sayımı, pazar büyüklüğü, rekabet analizi ve trend sektör skorları.
- `data/demo/firma_karti_demo.jsonl`: segment, paket, ciro ve çalışan dağılımı.
- `data/demo/segment_demo.jsonl`: segment kriterleri, aktiflik ve demo segment kayıtları.
- `data/demo/kampanya_demo.jsonl`: gösterim, tıklama, dönüşüm, bütçe ve kampanya durumu.
- `src/company_master/paketler.py`: paket-katalog ve firma-paket ilişkisi; raporda istenen fiyat tier’ları esas alınmıştır.
- `src/company_master/admin/caching.py`: Redis/in-memory fallback, TTL, cache key ve prefix invalidation politikası.
- **Yorum:** Persona ve yolculuk önerileri demo örneklerden türetilmiştir; üretim kararı öncesinde segment eşleşmesi, fiyat kataloğu, kampanya durumu ve gerçek kullanım eventleri doğrulanmalıdır.
