# Veri Kaynağı Envanteri

Bağlantılar: [[00-Home]] · [[01_sirket_master_ana_belgesi]] · [[01_veri_toplama_modeli]] · [[06_web_kazima_uzmani]]

Bu belge, [[01_sirket_master_ana_belgesi]] sonundaki "sonraki teknik adım" gereği her veri kaynağı için source → alanlar → erişim yöntemi → güncelleme sıklığı → yasal durum → güven skoru matrisini tutar.

## Kaynak matrisi

| Kaynak | Tür | Alanlar | Erişim yöntemi | Güncelleme sıklığı | Yasal durum | Güven skoru |
|---|---|---|---|---|---|---|
| OSTİM OSB | osb | Üye firma listesi, adres, telefon, web | Python Scraper | Çeyreklik | Kamuya açık, izin gerekli | 0.95 |
| İvedik OSB | osb | Üye firma listesi, adres, telefon, web | Manuel indirme | Çeyreklik | Kamuya açık, izin gerekli | 0.85 |
| ASO 1. OSB | osb | Üye firma listesi, adres, telefon, web | Python Custom Script | Çeyreklik | Kamuya açık, izin gerekli | 0.90 |
| ASO 2-3 OSB | osb | Üye firma listesi, adres, telefon, web | Manuel indirme | Çeyreklik | Kamuya açık, izin gerekli | 0.85 |
| Başkent OSB | osb | Üye firma listesi, adres, telefon, web | Manuel indirme | Çeyreklik | Kamuya açık, izin gerekli | 0.80 |
| Diğer sanayi bölgeleri | osb | Üye firma listesi, adres | Manuel toplama | Yıllık | Kamuya açık, izin gerekli | 0.70 |
| Oda/kuruluş kaynakları | chamber | Üye firma listesi, iletişim | Resmi talep | Yıllık | Üyelik gerektirir | 0.80 |
| GİB e-Fatura mükellef listesi | government | VKN, unvan, adres, NACE | Resmi API | Aylık | Kamuya açık | 0.95 |
| Şirket web siteleri | company_website | İletişim, ürünler, adres, telefon | Hedefli scraping | Yıllık | KVKK-uyumlu | 0.65 |

## Doldurma kuralları

- source_type değerleri master belge §3.12 ile uyumlu olmalıdır: government, osb, chamber, company_website, public_registry, search_engine, manual, other
- Her kaynak için legal_basis ve uthority_score doldurulmadan üretim toplaması başlatılmaz.
- Kaynak listesi sabit değildir; kaynaklarla doğrulanır ve genişletilir.
- Yeni satır eklendiğinde bu belge güncellenir; eski satırlar silinmez, durum alanı güncellenir.

## İlişkili tablolar (master §3)

- sources — kaynağın kimliği, türü, yetki skoru, yasal dayanak
- source_records — ham kayıt; silinmez, denetim için saklanır
## OSB detay kayıtları

### İvedik OSB
- erisim_yontemi: Manuel indirme (PDF/Excel üye listesi)
- guncelleme_sikligi: Çeyreklik
- yasal_durum: Kamuya açık, izin gerekli
- guven_skoru: 0.85
- not: Web sitesi üzerinden doğrudan API yok; OSB sekreterliğinden talep edilerek alınır.

### ASO 1. OSB
- erisim_yontemi: Python Custom Script (web scraping)
- guncelleme_sikligi: Çeyreklik
- yasal_durum: Kamuya açık, izin gerekli
- guven_skoru: 0.90
- not: Üye listesi web sitesinde dinamik olarak sunulur; otomatik scraper ile çekilebilir.

### ASO 2-3 OSB
- erisim_yontemi: Manuel indirme
- guncelleme_sikligi: Çeyreklik
- yasal_durum: Kamuya açık, izin gerekli
- guven_skoru: 0.85
- not: Tekil web sitesi yok; ASO merkezi koordinasyonunda toplu talep edilir.

### Başkent OSB
- erisim_yontemi: Manuel indirme
- guncelleme_sikligi: Çeyreklik
- yasal_durum: Kamuya açık, izin gerekli
- guven_skoru: 0.80
- not: Üye listesi offline paylaşılır; e-posta/yazılı talep ile temin edilir.
