# OSTİM Veri Kalite Raporu

**Tarih:** 2026-09-01T15:23:30
**Kaynak:** `firmalar_sayfa1.jsonl`
**Toplam Kayıt:** 312

## 1. Genel Kalite Skoru

| Metrik | Değer |
|---|---:|
| Ortalama skor | **69.7** / 100 |
| Yüksek (80-100) | 104 (%33.3) |
| Orta (60-79)    | 145 (%46.5) |
| Düşük (40-59)   | 54 (%17.3) |
| Çok Düşük (0-39) | 9 (%2.9) |

## 2. Alan Bazlı Doluluk

| Alan | Dolu | Yüzde |
|---|---:|---:|
| Ünvan | 312 | %100.0 |
| Telefon | 250 | %80.1 |
| E-posta | 236 | %75.6 |
| Web Sitesi | 185 | %59.3 |
| Adres | 211 | %67.6 |
| Sektör | 272 | %87.2 |

## 3. Çoklu Alan İstatistikleri

| Alan | Toplam | Ortalama/Firma |
|---|---:|---:|
| Telefon | 250 | 0.80 |
| E-posta | 236 | 0.76 |

## 4. Sektör Dağılımı

| Sektör | Firma |
|---|---:|
| Boş | 40 |
| Tekstil | 22 |
| Metalurji | 20 |
| Havacılık | 20 |
| Enerji | 20 |
| Bilgisayar | 20 |
| Bina | 20 |
| Ahşap | 20 |
| Makine | 19 |
| Kimya | 19 |
| Otomotiv | 18 |
| Plastik | 18 |
| Elektronik | 18 |
| Gıda | 18 |
| Biomedikal | 11 |
| Lojistik | 9 |

## 5. En Yüksek Kaliteli 5 Firma

### Sirket 155 OSTIM (skor: 100)
- Telefon: 0312 8084460
- E-posta: info-155@firma155.com
- Web: https://firma155.com

### Sirket 157 OSTIM (skor: 100)
- Telefon: 0312 8500938
- E-posta: info-157@firma157.com
- Web: https://firma157.com

### Sirket 176 OSTIM (skor: 100)
- Telefon: 0312 8105716
- E-posta: info-176@firma176.com
- Web: https://firma176.com

### Sirket 219 OSTIM (skor: 100)
- Telefon: 0312 8424998
- E-posta: info-219@firma219.com
- Web: https://firma219.com

### Sirket 25 OSTIM (skor: 95)
- Telefon: 0312 7901720
- E-posta: info-25@firma25.com
- Web: https://firma25.com

## 6. En Düşük Kaliteli 5 Firma (İyileştirme Gerekli)

### Sirket 281 OSTIM (skor: 10)
- Eksik alanlar: telefon, email, web, adres

### Sirket 151 OSTIM (skor: 25)
- Eksik alanlar: telefon, web, adres

### Sirket 147 OSTIM (skor: 30)
- Eksik alanlar: email, web, adres

### Sirket 283 OSTIM (skor: 30)
- Eksik alanlar: telefon, email, web

### Sirket 88 OSTIM (skor: 35)
- Eksik alanlar: telefon, web, adres

## 7. Sonraki Adımlar

1. **Detay sayfaları:** Liste sayfasında olmayan `web_sitesi`, `adres`, `sosyal_medya` alanları için detay scrape gerekli
2. **Adres çıkarımı:** Detay sayfalarındaki 'Adres' etiketli bölüm parse edilebilir
3. **Sosyal medya:** Logo/footer'dan LinkedIn, Twitter, Facebook, Instagram linkleri çıkarılabilir
4. **Cross-source merge:** vergi_no birincil anahtar olarak, OSTİM + MERSİS + ASO birleştirilecek
5. **Kalite iyileştirme:** 40'ın altında kalan firmalar için manuel doğrulama veya detay sayfası tekrar scrape
