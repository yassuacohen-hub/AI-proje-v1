---
name: data-quality-testing
description: >-
  Great Expectations ve Pandera standartlarında veri sözleşmeleri (Data Contracts),
  kural tabanlı doğrulama testleri, anomali tespiti ve veri kalitesi puanlama becerisi.
---

# Veri Kalitesi & Doğrulama Testi Becerisi (Data Quality Testing Skill)

Bu beceri, veri boru hatlarından (ETL/ELT) geçen veya veri ambarlarına aktarılan verilerin bütünlüğünü, eksiksizliğini ve doğruluğunu test etmek için kullanılır.

---

## 1. Temel Veri Kalitesi Boyutları (Data Quality Dimensions)

1. **Eksiksizlik (Completeness):** Kritik sütunlarda boş (Null/NaN) değer oranının belirlenen eşiği (örn: <%1) aşmaması.
2. **Benzersizlik (Uniqueness):** Birincil anahtar (Primary Key / ID) alanlarında mükerrer (duplicate) kayıt olmaması.
3. **Geçerlilik (Validity):** Değerlerin beklenen aralıklarda (örn: `0 <= Yaş <= 120`, `Fiyat > 0`) ve formatlarda olması.
4. **Tutarlılık (Consistency):** İlişkili tablolar arasındaki referans bütünlüğü (Foreign Key eşleşmeleri).
5. **Zamanlılık & Tazelik (Freshness):** Zaman damgalarının (timestamps) geleceğe dönük veya mantıksız geçmişe ait olmaması.

---

## 2. Kalite Skoru Hesaplama Formülü

$$\text{Kalite Puanı} = 100 \times \left( \frac{\text{Başarılı Test Sayısı}}{\text{Toplam Test Sayısı}} \right) - \text{Kritik Hata Cezaları}$$
