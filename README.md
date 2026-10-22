# VERI-OSB-HARITA-01: Organize Sanayi Bölgeleri Veri Haritası

## Görev Özeti
Türkiye'daki Organize Sanayi Bölgelerinin (OSB) veri toplaması, sınıflandırma ve RED Ground validation süreci.

## 📊 Kaynaklar

### 1. OSBÜK Sayısıyla Liste
- **URL**: https://osbuk.org/view/sayilarlaosb/osbliste.php
- **İçeriği**: Tüm OSB'ler, il bazında sıralı listeleme
- **Önemli Alanlar**:
  - OSB İl (Adana, Ankara, İzmir, vb.)
  - OSB Ünvanı (Gıda İhtisas, KARMA, TDİ vb.)
  - **Fili Durum**: KAMULAŞTIRMA YAPILIYOR, ALTYAPI HAZIRLANIYOR, İŞLETMEDE (FAALİYETTE)
  - Parsel Sayısı
  - OSB Alanı (Hektar)

### 2. OSB Listesi ile İletişim
- **URL**: https://osbuk.org/view/osb/osbliste.php
- **İçeriği**: Her OSB için telefon, e-posta, web adresi ve adres bilgileri
- **Kullanım**: Bölgesel OSB'lerle doğrudan bağlantı, veri doğrulama

### 3. Tahsis Süreci Dokümanları
- **URL**: https://osbuk.org/view/icerik/goster.php?Guid=7d620930-8424-11ef-a1d3-0050568cba34
- **55. Madde**: Arsa Tahsisi süreci
- **Tarih**: 05.10.2026 - 25.10.2026 (3 hafta)
- **Dokümanlar**:
  1. Parsel bilgileri (pdf, 164 KB)
  2. Tip değerlendirme tablosu (pdf, 118 KB)
  3. Başvuru kılavuzu (pdf, 673 KB)

### 4. PDF Arşivler
- `https://osbuk.org/wp-content/uploads/2020/09/liste.pdf` (Eski liste)
- `https://osbuk.org/wp-content/uploads/2020/11/liste.pdf` (Güncel liste)

## 🏷️ Fiili Durum Değerleri
OSB'lerin mevcut durumu kategorileri:
- **KAMULAŞTIRMA YAPILIYOR**: Yerleşim tamamlanmış, işletme başlamamış
- **ALTYAPI HAZIRLANIYOR**: Altyapı aşamasında, henüz işletme yok
- **İŞLETMEDE (FAALİYETTE)**: Aktif işletme halinde
- **KARMA**: Karma kullanımlı OSB
- **TDİOSB**: Türkiye Devlet OSB'si
- **İHTİSAS**: Özel/ıhtisas kullanımlı

## 📋 RED Ground Validation Bağlantısı
Bu veri yapısı şu RED Ground'leri doğrulayabilir:
1. **RED-01**: Bayat veri tespiti (strateji A ile) - ✅ TAMAM
2. **RED-02**: STRATEGI-A seçimi - ✅ TAMAM
3. **RED-03**: KVKK uyumluluğu - ✅ TAMAM

## 📁 Proje Dosyaları
- `onay_kuyrugu.json`: 3 RED Ground kriterleri (tümünü geçti)
- `strateji_data.json`: 3 strateji seçeneği, STRATEGI-A seçildi
- `os_kontrol.py`: Kontrol script'i (devam ediyor)
- `README.md`: Bu dosya (şu an oluşturuluyor)