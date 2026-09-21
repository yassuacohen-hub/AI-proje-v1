# ASO ve OSTİM Veri Kalite Raporu (P7-24)

**Üretim tarihi:** 2026-09-13 08:52  
**Üreten:** `scripts/quality_report.py`  
**Skor formülü:** VKN 15 + adres 15 + telefon 15 + e-posta 15 + web 10 + NACE 15 + parsel 10 + sektör/ticaret adı 5 (tavan 100) — `scripts/quality_recalc_fast.py` ile aynı ağırlıklar.

## 1. Özet

| Kaynak | Kayıt | Ort. Skor (temiz) | Ort. Skor (ham) | Şişme | Kopya Ünvan Grubu |
|---|---:|---:|---:|---:|---:|
| `aso` | 785 | 49.64 | 49.64 | +0.0 | 39 |
| `ostim` | 8313 | 36.61 | 36.61 | +0.0 | 44 |
| `ostim_detayli` | 5485 | 50.44 | 51.3 | +0.86 | 403 |

## 2. Kaynak: `aso`

- **Dosya:** `data\aso\aso_full.jsonl`
- **Toplam kayıt:** 785

### 2.1 Alan Doluluk

| Alan | Dolu | Oran |
|---|---:|---:|
| unvan | 785 | %100.0 |
| vkn | 0 | %0.0 |
| adres | 783 | %99.75 |
| telefonlar | 0 | %0.0 |
| epostalar | 768 | %97.83 |
| web | 0 | %0.0 |
| nace | 785 | %100.0 |
| parsel | 0 | %0.0 |
| sektor | 785 | %100.0 |

### 2.2 Format Geçerliliği

| Alan | Dolu | Geçerli | Hatalı | Geçerlilik |
|---|---:|---:|---:|---:|
| vkn | 0 | 0 | 0 | %0.0 |
| telefon | 0 | 0 | 0 | %0.0 |
| eposta | 768 | 767 | 1 | %99.87 |
| nace | 785 | 785 | 0 | %100.0 |

### 2.3 Kirlilik (Portal Kaynaklı Sahte Zenginlik)

- Web sitesi dolu: **0**
- Bunların portal kaynaklı olanı: **0** (%0.0)
- Gerçek firma web sitesi: **0**
- Sosyal medyası portal hesabı olan kayıt: **0**

### 2.4 Kopya / Tekillik

- Benzersiz ünvan: **716**
- Kopya ünvan grubu: **39** (fazladan 69 kayıt)
- Kopya VKN grubu: **0**
- Ünvansız kayıt: **0**
- Örnek kopyalar:
  - `i flas nedeni yle tasfi ye hali nde anadolu elektri k sanayi ve ti caret anoni m si rketi` → 3 kez
  - `i flas nedeni yle tasfi ye hali nde arasta uluslararasi yatirim fi nans danismanlik hi zmetleri i nsaat enerji gida tarim hayvancilik emlak ti caret li mi ted si rketi` → 3 kez
  - `i flas nedeni yle tasfi ye hali nde ardam atik yoneti mi ve depolama sanayi ve ti caret anoni m si rketi` → 3 kez
  - `i flas nedeni yle tasfi ye hali nde avrasya enerji i nsaat turi zm ve ti caret anoni m si rketi` → 3 kez
  - `i flas nedeni yle tasfi ye hali nde basari tutkum bi li si m proje ve loji sti k anoni m si rketi` → 3 kez

### 2.5 Kalite Skoru Dağılımı

- Ortalama (temiz): **49.64** | Ortalama (ham): 49.64 | Kirlilik şişmesi: **+0.0 puan**
- Min / Medyan / Maks: 35.0 / 50.0 / 50.0

| Kova | Kayıt |
|---|---:|
| 40-59 (orta) | 766 |
| 20-39 (zayif) | 19 |

## 2. Kaynak: `ostim`

- **Dosya:** `data\ostim\firmalar_full.jsonl`
- **Toplam kayıt:** 8313

### 2.1 Alan Doluluk

| Alan | Dolu | Oran |
|---|---:|---:|
| unvan | 8313 | %100.0 |
| vkn | 0 | %0.0 |
| adres | 0 | %0.0 |
| telefonlar | 7650 | %92.02 |
| epostalar | 3668 | %44.12 |
| web | 0 | %0.0 |
| nace | 7047 | %84.77 |
| parsel | 0 | %0.0 |
| sektor | 5770 | %69.41 |

### 2.2 Format Geçerliliği

| Alan | Dolu | Geçerli | Hatalı | Geçerlilik |
|---|---:|---:|---:|---:|
| vkn | 0 | 0 | 0 | %0.0 |
| telefon | 7650 | 7645 | 5 | %99.93 |
| eposta | 3668 | 3661 | 7 | %99.81 |
| nace | 7047 | 7047 | 0 | %100.0 |

### 2.3 Kirlilik (Portal Kaynaklı Sahte Zenginlik)

- Web sitesi dolu: **0**
- Bunların portal kaynaklı olanı: **0** (%0.0)
- Gerçek firma web sitesi: **0**
- Sosyal medyası portal hesabı olan kayıt: **0**

### 2.4 Kopya / Tekillik

- Benzersiz ünvan: **8267**
- Kopya ünvan grubu: **44** (fazladan 46 kayıt)
- Kopya VKN grubu: **0**
- Ünvansız kayıt: **0**
- Örnek kopyalar:
  - `deser ki mya sanayi ve ti caret ltd sti` → 3 kez
  - `zi ya comertoglu i lave di ngi l damper i ns tur ti c ltd sti` → 3 kez
  - `asay lazer kesi m savunma si stemleri maki na i malat san ve ti c ltd sti` → 2 kez
  - `atasam saglik ve saglik si stemleri san ve ti c ltd sti` → 2 kez
  - `bnb mekatroni k savunma sanayi ve ti c ltd sti` → 2 kez

### 2.5 Kalite Skoru Dağılımı

- Ortalama (temiz): **36.61** | Ortalama (ham): 36.61 | Kirlilik şişmesi: **+0.0 puan**
- Min / Medyan / Maks: 0.0 / 35.0 / 50.0

| Kova | Kayıt |
|---|---:|
| 40-59 (orta) | 3313 |
| 20-39 (zayif) | 3900 |
| 0-19 (cok zayif) | 1100 |

## 2. Kaynak: `ostim_detayli`

- **Dosya:** `data\ostim\firmalar_detayli.jsonl`
- **Toplam kayıt:** 5485

### 2.1 Alan Doluluk

| Alan | Dolu | Oran |
|---|---:|---:|
| unvan | 5485 | %100.0 |
| vkn | 3 | %0.05 |
| adres | 5483 | %99.96 |
| telefonlar | 5085 | %92.71 |
| epostalar | 2701 | %49.24 |
| web | 5483 | %99.96 |
| nace | 0 | %0.0 |
| parsel | 5 | %0.09 |
| sektor | 5485 | %100.0 |

### 2.2 Format Geçerliliği

| Alan | Dolu | Geçerli | Hatalı | Geçerlilik |
|---|---:|---:|---:|---:|
| vkn | 3 | 3 | 0 | %100.0 |
| telefon | 5085 | 5081 | 4 | %99.92 |
| eposta | 2701 | 2701 | 0 | %100.0 |
| nace | 0 | 0 | 0 | %0.0 |

### 2.3 Kirlilik (Portal Kaynaklı Sahte Zenginlik)

- Web sitesi dolu: **5483**
- Bunların portal kaynaklı olanı: **474** (%8.64)
- Gerçek firma web sitesi: **5009**
- Sosyal medyası portal hesabı olan kayıt: **0**
- En sık domainler:
  - `isim.org.tr` → 2273
  - `ostimistihdam.com` → 474 ⚠️ portal
  - `akifsan.com` → 9
  - `aymakine.com` → 5
  - `korcelik.com.tr` → 5
  - `ozbensavunma.com` → 5
  - `babacanrubber.com` → 4
  - `scturbofiltre.com` → 3
  - `anadoluotocam.com` → 3
  - `aymasdisli.com` → 3

### 2.4 Kopya / Tekillik

- Benzersiz ünvan: **5041**
- Kopya ünvan grubu: **403** (fazladan 444 kayıt)
- Kopya VKN grubu: **0**
- Ünvansız kayıt: **0**
- Örnek kopyalar:
  - `akifsan mak hirdavat san ve tic ltd sti` → 9 kez
  - `arif yilmaz ay makine` → 5 kez
  - `stg muhendislik` → 5 kez
  - `anadolu oto cam san tic ltd sti` → 3 kez
  - `aymas di sli maki na sanayi ti caret a s` → 3 kez

### 2.5 Kalite Skoru Dağılımı

- Ortalama (temiz): **50.44** | Ortalama (ham): 51.3 | Kirlilik şişmesi: **+0.86 puan**
- Min / Medyan / Maks: 20.0 / 45.0 / 75.0

| Kova | Kayıt |
|---|---:|
| 60-79 (iyi) | 2568 |
| 40-59 (orta) | 2229 |
| 20-39 (zayif) | 688 |

## 3. Kaynaklar Arası Tamamlayıcılık

| Alan | aso | ostim | ostim_detayli |
|---|---:|---:|---:|
| unvan | %100.0 | %100.0 | %100.0 |
| vkn | %0.0 | %0.0 | %0.05 |
| adres | %99.75 | %0.0 | %99.96 |
| telefonlar | %0.0 | %92.02 | %92.71 |
| epostalar | %97.83 | %44.12 | %49.24 |
| web | %0.0 | %0.0 | %99.96 |
| nace | %100.0 | %84.77 | %0.0 |
| parsel | %0.0 | %0.0 | %0.09 |
| sektor | %100.0 | %69.41 | %100.0 |

**Belirgin tamamlayıcılık (≥50 puan fark):**

- adres: ostim_detayli (%99.96) >> ostim (%0.0)
- telefonlar: ostim_detayli (%92.71) >> aso (%0.0)
- epostalar: aso (%97.83) >> ostim (%44.12)
- web: ostim_detayli (%99.96) >> aso (%0.0)
- nace: aso (%100.0) >> ostim_detayli (%0.0)

## 4. Bulgular ve Öneriler

1. **Portal kaynaklı web/sosyal medya verisi skoru şişiriyor.** `ostimistihdam.com` gibi OSB portal adresleri firmanın kendi sitesi değildir; ETL aşamasında `website_domain` alanına yazılmadan önce elenmelidir.
2. **ASO ve OSTİM tamamlayıcıdır.** ASO NACE/adres/ticaret sicil tarafında güçlü, OSTİM ise parsel/sektör ve iletişim tarafında daha zengin. Birleştirme (dedup) ünvan normalizasyonu + VKN üzerinden yapılmalıdır.
3. **VKN doluluğu darboğaz.** VKN olmayan kayıtlar tekilleştirmede ünvan benzerliğine mahkûm kalıyor; VKN zenginleştirme (Ticaret Sicil Gazetesi / e-fatura mükellef listesi) öncelikli iş olmalı.
4. **Kopya ünvanlar dedup öncesi temizlenmeli.** Rapordaki kopya ünvan grupları, aynı firmanın farklı sayfalardan iki kez çekildiğine işaret ediyor.

