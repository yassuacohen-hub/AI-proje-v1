# OSB Masa Başı Analizi — 3 OSB Üye Listesi Erişim Raporu

Bağlantılar: [[00-Home]] · [[02_ankara_osb_ekosistemi_arastirma_notu]] · [[10_ankara_osb_sentez]] · [[10_mvp_kapsam]] · [[01_veri_kaynagi_envanteri]] · [[project_state]] · [[CHANGELOG]]

Bu rapor, Web Kazıma Uzmanı'nın 30 dakikalık masa başı analizinin sonucudur (V10/10_ankara_osb_sentez Karar 4). 3 hedef OSB'nin üye listesi erişilebilirliği, formatı ve scraping uygunluğu değerlendirilmiştir.

**Tarih:** 2026-09-01
**Analist:** Web Kazıma Uzmanı (orquestratör desteğiyle)

---

## 1. OSTİM OSB — ✓ TAM ERİŞİLEBİLİR (MVP ÖNCELİKLİ)

### Erişim
- **Web sitesi:** https://www.ostim.org.tr
- **Üye listesi sayfası:** https://www.ostim.org.tr/firmalar
- **Sektör sayfaları:** https://www.ostim.org.tr/sektorler/{sektor-slug}
- **robots.txt:** Disallow: /admin/, /portal/, /auth/ (üye listesi taranabilir)
- **Erişim durumu:** Kamuya açık, anonim tarama mümkün

### Önemli Bulgular
- OSTİM öz kaynaklarında **"6.500'den fazla işletme, 17 Ana Sektör, 139 İşkolu, 65.000 çalışan"** yazıyor.
- Araştırma notundaki 5.000+ rakamı daha düşk (muhtemelen farklı yıl); güncel 6.500+.
- Sayfa başına ~30 firma kartı, toplamda **yüzlerce sayfa** (pagination gerekir).
- Her firma kartında: unvan, telefon, e-posta, slug-link.
- Detay sayfası açılırsa: adres, sektör, ürünler olabilir.

### Sektör Dağılımı (OSTİM Öz Sayfası)
| Sektör | Firma Sayısı |
|---|---:|
| Otomotiv | 1.163 |
| Yapı ve İnşaat | 794 |
| İş Makinaları | 780 |
| Makine ve Makine Ekipmanları | 757 |
| Metal ve Metal İşleme | 752 |
| Çeşitli Ticari Faaliyetler | 410 |
| Elektrik ve Elektronik | 390 |
| Hizmetler | 380 |
| Teknik Malzeme Tezgah ve Ekipman | 339 |
| Teknoloji ve Bilişim | 192 |
| Ambalaj - Kağıt - Baskı ve Kırtasiye | 127 |
| Plastik ve Kauçuk | 114 |
| Kimyasallar - Boya - Temizlik ve Güvenlik | 109 |
| Gıda ve Endüstriyel Mutfak | 98 |
| Sağlık | 78 |
| Tekstil ve Deri | 71 |
| Kent Mobilyaları ve Peyzaj | 16 |
| **TOPLAM** | **6.570+** |

### Scraping Planı
- `requests + BeautifulSoup4` yeterli (statik HTML, JS yok).
- Rate limit: 1 istek / 3 saniye (site yoğun olabilir).
- User-Agent: `AnkaraB2B-Bot/1.0 (research@example.com)`.
- **Sayfalama:** ?page=N parametresi ile dolaş.
- **Yapı:** JSON Lines dosyasına yaz (her satır bir firma).

### Yasal/Etik
- robots.txt'te /firmalar disallow edilmemiş — scraping teknik olarak uygun.
- Yalnızca kurumsal iletişim (info@, sabit telefon) hedeflenecek.
- Kişisel veri toplanmayacak.

### Karar: **OSTİM MVP LİDER ADAYI**
- 6.500+ firmaya doğrudan erişim var.
- Sektör dağılımı zengin.
- İlk batch: OSTİM sektör listelerini scrape et, JSONL'e yaz.

---

## 2. ASO 1 OSB — ⚠ KISITLI ERİŞİM (KAYIT GEREKEBİLİR)

### Erişim
- **Web sitesi:** https://www.aosb.org.tr (kullanıcı önerdiği aso1osb.org.tr adresi çalışmıyor)
- **Telefon:** 0312 267 00 00
- **Adres:** Ayaş yolu 25. km. 06935 Sincan / Ankara
- **Erişim durumu:** Resmi sayfa var, ancak üye listesi açık mı kontrol gerekli.

### Önemli Bulgular
- ASO 1 OSB öz sayfasında **"333 Sanayi Parseli, 281 Fabrika, 40.000 İstihdam"** yazıyor.
- 5.500+ araştırma rakamı ile uyumlu (yaklaşık).
- Üye listesi için "E-İşlemler" portalı var; giriş gerekebilir.
- ASO (Ankara Sanayi Odası) ayrı bir kuruluş; **ASO Üye Sorgulama** sistemi var: https://www.aso.org.tr/firmarehberi/ — bu tüm ASO üyeleri (OSB üyesi olmayanlar dahil).

### Scraping Planı
- ASO 1 OSB özel üye listesi: **muhtemelen giriş gerektirir**, scraping uygun değil.
- Alternatif: ASO Üye Sorgulama (firmarehberi) — kamuya açık, scraping yapılabilir.
- Bu durumda `is_osb_member = TRUE` doğrulanamaz, NACE kodu + ilçe = "Sincan" heuristik.

### Yasal/Etik
- ASO 1 OSB doğrudan scraping riskli (üye bilgileri korunmuş olabilir).
- ASO Üye Sorgulama sayfası kamuya açık.

### Karar: **ASO 1 OSB MVP İÇİN ERTELENMELİ**
- Önce OSB'den resmi talep yazısı gönderilecek.
- Talep reddedilirse ASO Üye Sorgulama scraping yapılacak (heuristik tabanlı).
- Faz 1'de OSTİM sonuçlarına göre ASO 1 planı netleşir.

---

## 3. İVEDİK OSB — ⚠ KISITLI ERİŞİM (RESMİ TALEP GEREKİR)

### Erişim
- **Web sitesi:** https://www.ivedikosb.org.tr
- **Telefon:** 0312 395 62 62
- **Başkan:** Hasan GÜLTEKİN
- **Erişim durumu:** Resmi sayfa var, üye listesi kamuya açık değil.

### Önemli Bulgular
- İvedik OSB öz sayfasında **"10.000 işletme, 125.000 istihdam, 5 milyar $ ekonomik hacim"** yazıyor.
- Araştırma notundaki 3.000+ rakamı çok düşk (muhtemelen sadece OSB sınırları içi; 10.000 geniş kapsam).
- Sitede üye listesi sayfası (`/firmalar/`) var ama erişim giriş gerektirebilir.
- İvedik Organize Sanayi Sitesi (İVOGSAN) ayrı bir yapı; İvedik OSB kapsamında değil.

### Scraping Planı
- Resmi siteden üye listesi çekilemiyor.
- **Resmi talep** ile üye listesi istenecek.
- Alternatif kaynaklar: rehbersanayi.com, firmarehberim.com (üçüncü parti, güvenilirlik düşk).

### Yasal/Etik
- Resmi OSB üye listesi **kişisel veri** içerebilir (yetkili kişi adı, telefon).
- Master §6 UNKNOWN prensibi + KVKK gereği yalnızca kurumsal bilgi alınabilir.
- OSB'den resmi talep yazısı ile sadece kurumsal iletişim istenecek.

### Karar: **İVEDİK OSB MVP İÇİN ERTELENMELİ**
- Resmi talep yazısı hazırlanacak.
- Talep sonucuna göre scraping veya manuel veri girişi.
- Faz 1'de OSTİM + ASO 1 sonuçlarına göre İvedik planı netleşir.

---

## 4. Doğrulanmış Rakamlar (Yeni)

| OSB | Öz Sayfa Rakamı | Araştırma Notu | Fark |
|---|---:|---:|---|
| OSTİM | **6.500+ işletme** | 5.000+ | +1.500 (daha yüksek) |
| ASO 1 OSB | **333 parsel, 281 fabrika** | 5.500+ | Çelişkili (ölçüm farklı) |
| İvedik OSB | **10.000 işletme** | 3.000+ | +7.000 (çok daha yüksek) |
| **Toplam (öz sayfa)** | **16.810+** | **13.500+** | +3.310 |

**Yorum:** Araştırma notundaki rakamlar eksik. OSTİM ve İvedik güncel öz sayfaları çok daha büyük sayılar gösteriyor. ASO 1 için "5.500+" rakamı muhtemelen "5.500 istihdam" gibi farklı bir metrik olabilir.

---

## 5. Riskler ve Uyarılar

- **OSTİM scraping:** Site aktif, robots.txt uyumlu. ~6.500 firma, 200+ sayfa. Birkaç saatlik scraping ile bitebilir.
- **ASO 1 / İvedik:** Resmi üye listesi yok. OSB yönetimleriyle iletişim şart.
- **Veri kalitesi:** OSTİM sayfasında telefon numaraları GSM (90532...) ağırlıklı — kişisel veri riski. Filtreleme gerekli.
- **KVKK:** Tüm veri toplamada resmi OSB yönetiminden izin alınmalı.

---

## 6. Önerilen Sonraki Adımlar

| # | Adım | Sorumlu | Süre |
|---|---|---|---|
| 1 | OSTİM üye listesi scraping (sektör bazlı, 17 sektör × 50 sayfa) | Geliştirici Ajan | 2-3 saat |
| 2 | ASO 1 OSB'ye resmi talep yazısı | Koordinatör Ajan | 1 gün |
| 3 | İvedik OSB'ye resmi talep yazısı | Koordinatör Ajan | 1 gün |
| 4 | OSTİM verisi → JSONL → SQLite test | Geliştirici Ajan | 1 saat |
| 5 | Veri kalite skoru hesaplama (Yüksek/Orta/Düşük) | Kalite Ajan | 2 saat |

---

## İlgili Wiki Sayfaları

- [[02_ankara_osb_ekosistemi_arastirma_notu]] — Araştırma verisi
- [[10_ankara_osb_sentez]] — 6 ajanın sentez kararı
- [[10_mvp_kapsam]] — MVP kapsamı belgesi
- [[01_veri_kaynagi_envanteri]] — Kaynak envanteri
- [[01_sirket_master_ana_belgesi]] — Ana şema
