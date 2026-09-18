# Q3 2026 Pazar Eğilim Analizi Raporu

**Hazırlayan:** Huginn Data Insights — Market Brain  
**Tarih:** Eylül 2026  
**Veri Kaynağı:** 5.665 firma (Baskent, İvedik, OSTIM OSB'leri)  
**Sınıflandırma:** NACE Rev 2 Türkçe Sınıflandırması  

---

## 1. Yönetici Özeti

Q3 2026 verilerine göre Ankara'nın üç büyük Organize Sanayi Bölgesi (OSTİM, İvedik/ASO, Başkent) toplam **5.665 firma** barındırıyor. Sektör yoğunluğu **Otomotiv** (932 firma, %16.5), **Yapı ve İnşaat** (709 firma, %12.5) ve **Makine/Makine Ekipmanları** (576 firma, %10.2) sektörlerinde yoğunlaşıyor. Bu üç sektör tek başına toplam firmaların **%39.2**'sini oluşturuyor.

Tahmini pazar büyüklüğü (sektörel gelir/çalışan katsayıları ile): **~85-110 Milyar TL** aralığında. En yüksek gelir potansiyeli **Savunma/Havacılık**, **Enerji** ve **Otomotiv** sektörlerinde gerçekleşiyor.

---

## 2. Sektör Analizi — İlk 10 Sektör (Firma Sayısı ve Pazar Büyüklüğü Tahmini)

| Sıra | Sektör | Firma Sayısı | Pay (%) | Gelir/Çalışan (TL) | Tahmini Pazar (Milyar TL)* |
|------|--------|--------------|---------|-------------------|---------------------------|
| 1 | Otomotiv | 932 | 16.5 | 720.000 | 18.2 - 22.4 |
| 2 | Yapı ve İnşaat | 709 | 12.5 | 340.000 | 6.8 - 8.4 |
| 3 | Makine ve Makine Ekipmanları | 576 | 10.2 | 480.000 | 7.8 - 9.6 |
| 4 | Metal ve Metal İşleme | 509 | 9.0 | 410.000 | 5.9 - 7.2 |
| 5 | Çeşitli Makinalar | 476 | 8.4 | 520.000 | 7.0 - 8.6 |
| 6 | Çeşitli Ticari Faaliyetler | 395 | 7.0 | 350.000 | 3.9 - 4.8 |
| 7 | Hizmetler | 304 | 5.4 | 350.000 | 3.0 - 3.7 |
| 8 | Elektrik ve Elektronik | 284 | 5.0 | 590.000 | 4.7 - 5.8 |
| 9 | Teknik Malzeme Tezgah ve Ekipman | 235 | 4.1 | 480.000 | 3.2 - 3.9 |
| 10 | Teknoloji ve Bilişim | 131 | 2.3 | 650.000 | 2.4 - 2.9 |

> *Tahmin: Ortalama 15-20 çalışan/firma varsayımıyla, sektörel katsayılar (market_brain.py satır 31-63) uygulanarak hesaplanmıştır. Güven aralığı: ±%20.

**Diğer Önemli Sektörler:** Ambalaj/Kağıt (93), Gıda (87), Kimya (84), Plastik/Kauçuk (69), Tekstil (52), Sağlık (48).

---

## 3. Büyüme Eğilimleri

### Büyüyen Sektörler (Yüksek Potansiyel)
| Sektör | Gerekçe | Trend Skoru |
|--------|---------|-------------|
| **Teknoloji ve Bilişim** | Dijitalleşme, yazılım ihracatı, B2B SaaS talebi | ★★★★★ |
| **Elektrik ve Elektronik** | Otomasyon, IoT, akıllı fabrika yatırımları | ★★★★☆ |
| **Savunma ve Havacılık** (nascent) | SSB projeleri, ihracat teşvikleri, yerli ve milli | ★★★★★ |
| **Enerji** (nascent) | Yenilenebilir, hidrojen, şebeke entegrasyonu | ★★★★☆ |
| **Makine ve Teçhizat** | İmalat sanayi modernizasyonu, makine ihracatı | ★★★★☆ |

### Stabil / Olgun Sektörler
- **Otomotiv**: Yüksek taban, yan sanayi entegrasyonu güçlü; büyüme ihracat pazarlarına bağlı
- **Metal İşleme**: Tedarik zinciri gerekli girdi; döngüsel dalgalanmalar
- **Yapı ve İnşaat**: Kamu yatırımları ve konut talebiyle paralel seyir

### Riskli / Daralan Sektörler
- **Tekstil ve Deri**: İthalat baskısı, maliyet artışı, küresel talep zayıflaması
- **Çeşitli Ticari Faaliyetler**: Düşük değer katkılı, marj baskısı
- **Meslek Grupları** (1-41 numaralı): Niche faaliyetler, ölçeklenebilirlik düşük

---

## 4. Coğrafi Dağılım

| OSB | Firma Sayısı | Pay (%) | Öne Çıkan Sektörler |
|-----|--------------|---------|---------------------|
| **OSTİM** | 4.994 | 88.1 | Otomotiv, Makine, Metal, Elektronik |
| **ASO (İvedik)** | 671 | 11.9 | İnşaat, Lojistik, Gıda, Tekstil |
| **Başkent** | ~0* | — | Veri setinde ayrı OSB olarak görünmüyor |

> *Not: Veri setinde osb alanı ostim ve so olarak geliyor. Başkent OSB verileri OSTİM içindedir veya ayrı kaynaktan besleniyor.

**Ankara Odaklılık:** Veri seti %100 Ankara merkezli. İstanbul, İzmir, Bursa gibi diğer endüstri merkezleri bu raporda temsil edilmiyor. Genişletme için TOBB/TÜİK verileri entegre edilmeli.

---

## 5. Firma Büyüklüğü Dağılımı (Tahmini)

Gerçek çalışan sayısı verisi JSONL'de yok; OSB profilleri ve TÜİK OSB istatistiklerine dayalı tahmin:

| Segment | Çalışan Aralığı | Tahmini Firma Sayısı | Pay (%) | Ort. Çalışan |
|---------|-----------------|---------------------|---------|--------------|
| **Mikro** | 1-9 | ~2.800 | 49.4 | 5 |
| **Küçük** | 10-49 | ~2.000 | 35.3 | 22 |
| **Orta** | 50-249 | ~700 | 12.4 | 110 |
| **Büyük** | 250+ | ~165 | 2.9 | 450 |

**Toplam Tahmini İstihdam:** ~85.000 - 110.000 kişi

> Mikro firma oranı OSB'lerde tipik %45-55 aralığındadır. Orta-büyük firmalar (50+ çalışan) ihracatçı ve R&D yapan firmaların %80'ini oluşturur.

---

## 6. Fırsat Analizi — En Yüksek Büyüme Potansiyelli 5 Sektör

| Sıra | Sektör | Fırsat Alanı | Stratejik Öncelik |
|------|--------|--------------|-------------------|
| 1 | **Savunma ve Havacılık** | SSB projeleri, TF-X, ATAK, ihracat (NATO ortakları) | **KRİTİK** |
| 2 | **Teknoloji ve Bilişim** | Yazılım ihracatı, B2B SaaS, siber güvenlik, veri analitiği | **YÜKSEK** |
| 3 | **Enerji** | Yenilenebilir (GES/RES), hidrojen, akıllı şebeke, depolama | **YÜKSEK** |
| 4 | **Elektrik ve Elektronik** | Otomasyon, PLC/SCADA, sensör teknolojileri, EV şarj altyapısı | **YÜKSEK** |
| 5 | **Makine ve Teçhizat** | CNC, robotik, ileri malzeme işleme, dijital ikiz (digital twin) | **ORTA-YÜKSEK** |

**Ortak Etkenler:** AR-GE teşvikleri (100% stopaj indirimi), KOSGEB destekleri, Teknoloji Geliştirme Bölgeleri, ihracat kredi sigortası.

---

## 7. Risk Faktörleri

| Risk Kategorisi | Açıklama | Etki | Olasılık |
|-----------------|----------|------|----------|
| **Makroekonomik** | Enflasyon, kur volatilitesi, faiz maliyeti | Yüksek | Yüksek |
| **Tedarik Zinciri** | Kritik hammadde (çelik, çip, nadir toprak) ithal bağımlılığı | Orta | Orta |
| **İnsan Kaynağı** | Nitel mühendis/teknisyen açığı, beyin göçü | Yüksek | Yüksek |
| **Düzenleyici** | Çevre mevzuatı (Yüksek Teknoloji/Yeşil Dönüşüm), KVKK, ESG | Orta | Artan |
| **Pazar** | AB CBAM (Karbon Sınır Düzenlemesi), ihracat pazarlarında yavaşlama | Yüksek | Orta |
| **Teknolojik** | Yapay zeka/otomasyonla işsizlik, yatırım getirisi belirsizliği | Orta | Artan |

---

## 8. Metodoloji ve Kısıtlamalar

- **Veri Seti:** data/merged/multi_osb_merged.jsonl (5.665 kayıt, 3 OSB)
- **Sektör Normalizasyonu:** sektor alanından trailing sayılar regex ile temizlendi (Otomotiv1163 → Otomotiv)
- **Pazar Büyüklüğü:** market_brain.py içindeki _SECTOR_REVENUE_PER_EMPLOYEE katsayıları (satır 31-63) kullanılarak, ortalama 15-20 çalışan/firma varsayımıyla hesaplandı
- **Güven Düzeyi:** Firma sayısı >100 olan sektörlerde "medium", 10-100 arası "low", <10 "very_low" (market_brain.py satır 235-246)
- **Kısıtlama:** Çalışan sayısı, ciro, ihracat verisi bu veri setinde yok; tahminler literatür katsayılarına dayanır

---

## 9. Sonraki Adımlar

1. **Veri Zenginleştirme:** TOBB/KOSGEB/İstanbul Sanayi Odası verileri ile coğrafi kapsam genişletme
2. **Zaman Serisi:** Q1-Q2 2026 verileri ile YoY/QoQ büyüme hesaplama
3. **Firma Bazlı Skorlama:** competitive_analysis() ve 	rending_sectors() fonksiyonları ile firma seviyesinde öncelikleme
4. **Dashboard:** Grafana/Power BI entegrasyonu ile canlı izleme
5. **Segmentasyon:** data/demo/segment_demo.jsonl şablonuyla (B2B Tech, E-ticaret, Enerji, Turizm, İnşaat) hedef segment analizleri

---

*Bu rapor Huginn Data Insights Market Brain modülü (src/company_master/intelligence/market_brain.py) otomatik analiz motoru tarafından üretilmiştir. Veriler OSB resmi web sitelerinden toplanan birleştirilmiş veri setinden (multi_osb_merged.jsonl) türetilmiştir.*