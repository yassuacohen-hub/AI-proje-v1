# MERSİS/Ticaret Sicili API Araştırma

## GİB Açık Veri Durumu
- e-Fatura/Kayıtlı Kullanıcılar: Acik veri **yok** (KVKK/gizlilik nedeniyle)
- e-Arşiv Sorgulama: Tekil VKN sorgulama **mumkun**, toplu indirilemez
- acikveri.gib.gov.tr: Sadece istatistiksel veri

## Alternatif Stratejiler

### 1. MERSİS API (mersis.gov.tr)
- Araç: https://mersis.gov.tr/ares/ws/getAresDetayCevapV2?VKN=XXXXX
- Gerekli: API Anahtari / Otorisasi
- Sinir: Rate limit, toplu sorgu desteklenmez
- Uygulama: Tek tek VKN dogrulama icin kullanilabilir

### 2. Ticaret Sicili (tsb.gov.tr)
- Araç: Şirket Arama Sistemi
- Kriter: Unvan + VKN eslesmesi
- API: Resmi portalda API yok, manual/otomasyonlu scraping gerekebilir

### 3. Acik Veri / Diger Kaynaklar
- TOBB Oda Kayitlari: Genel erisim, daha fazla alan (faaliyet kodu, adres vb.)
- Belediye Isyeri Kayitlari: Sehir belediyelerinde, yillik olarak
- Tum Veri Portali: acikveri.gib.gov.tr (sadece istatistik)

## Basvuru Sreci
1. MERSİS API: api@mersis.gov.tr adresinden talep
2. Ticaret Sicili: TSB musteri servisi uzerinden
3. Test: Ucretsiz deneme API anahtari almak mumkun olabilir

## Not
- Tum sorgulama KVKK uyumlu olmali
- Veri saklama suresi ve amac bildirimi zorunlu
- Kisisel veriler (TC, telefon) icin ek izin gerekir

## VKN/TC Kimlik No Notu
- VKN genellikle 10 haneli (kurumsal)
- TC Kimlik No 11 haneli (sahis firmalari icin)
- 10-11 haneli her sayi vergi/tc kimlik adayi olabilir
- Footer da vergi/vkn anahtar kelimesiyle birlikte gelen sayi oncelikli
