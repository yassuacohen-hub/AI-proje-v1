# Açık Veri ve Web Kazıma Politikası

Bağlantılar: [[00-Home]] · [[04_web_kazima_kaynak_arastirmasi]] · [[03_kvkk_ve_veri_politikasi]] · [[10_ankara_osb_sentez]] · [[project_state]]

**Tarih:** 2026-09-01
**Sürüm:** 1.0
**Karar referansı:** [[10_ankara_osb_sentez]] Karar 7

---

## 1. Amaç ve Kapsam

Bu belge, Ankara B2B Company Master V1.0 projesinde web kazıma (web scraping) ile veri toplama süreçlerinin kurallarını, sınırlarını ve en iyi uygulamalarını tanımlar.

**Kapsam:** Tüm açık ve yarı-açık web kaynaklarından (OSB siteleri, ASO, MERSİS, GİB, TÜİK, data.gov.tr, ticari rehberler) veri toplama işlemleri.

---

## 2. Temel İlkeler

1. **Halka açık veri öncelikli** — Resmi, kamu, açık kaynaklardan başla.
2. **Asgari gerekli veri** — Amacı aşan veri toplama.
3. **Şeffaflık** — User-Agent'ta iletişim bilgisi belirt.
4. **Saygı** — Rate limit, robots.txt, sunucu yükünü gözet.
5. **KVKK uyumu** — Hassas veri ayrıcalıklı yönetilir.
6. **Doğrulanabilirlik** — Kaynak URL, çekilme tarihi, hash saklanır.

---

## 3. Kaynak Tipleri ve Erişim Matrisi

| Kaynak Tipi | Erişim Yöntemi | Öncelik | Örnek |
|---|---|---|---|
| OSB/Resmi | GET + HTML parse | Yüksek | OSTİM, ASO 1 |
| Meslek Odası | GET + AJAX | Yüksek | ASO, ATO |
| Kamu Açık Veri | API veya CSV | En yüksek | data.gov.tr |
| Resmi Sicil | Form POST + Captcha | Orta | MERSİS, GİB |
| Teknopark | GET + HTML | Orta | ODTÜ TEKNOKENT |
| Ticari Rehber | GET + HTML | Düşük | firmarehberim.com |
| Sosyal Medya | API token gerekli | Düşük | LinkedIn |

---

## 4. Rate Limit ve Nezaket

| Kaynak | Min Aralık | Eşzamanlılık | Notlar |
|---|---|---|---|
| OSB websitesi | 3 sn | 1 thread | Küçük siteler |
| ASO / Oda | 2 sn | 1 thread | Orta siteler |
| data.gov.tr | 5 sn | 1 thread | Toplu indirme |
| MERSİS | 10 sn | 1 thread | Captcha + yavaş |
| Ticari rehber | 1 sn | 2 thread | Daha hızlı |

---

## 5. Veri Normalizasyon Kuralları

### 5.1 Telefon
- `90` ile başlayan 12 hane (ör. 903122221234)
- Sabit: 0 + 3/4 + 7 hane
- GSM: 0 + 5 + 7 hane
- Çoklu telefon `list[str]` olarak saklanır

### 5.2 Vergi No
- 10 veya 11 hane (gerçek/tüzel ayrımı)
- T.C. kimlik no ile karıştırma (KVKK riski!)

### 5.3 Unvan
- Tüm büyük harf dönüşümü (Türkçe karakter korunur)
- "A.Ş.", "Ltd. Şti.", "Tic." ekleri normalize
- "Türkiye İş Bankası A.Ş." → "TÜRKİYE İŞ BANKASI"

### 5.4 NACE Kodu
- 4 hane (ör. 25.11)
- Hiyerarşik: 25 → 25.1 → 25.11

### 5.5 Adres
- OSB parsel bilgisi (ada/parsels) eklenir
- İl, ilçe, mahalle, sokak, no standardizasyonu

---

## 6. Veri Kalite Skoru

Her firma için 0-100 arası skor:

| Bileşen | Puan |
|---|---:|
| vergi_no var | 15 |
| mersis_no var | 10 |
| unvan normalize | 5 |
| telefon(ler) var | 15 |
| email var | 10 |
| web_sitesi var | 10 |
| adres var | 10 |
| NACE kodu var | 10 |
| osb_id var | 5 |
| sektör detayı | 5 |
| sertifika(lar) | 5 |
| **Toplam** | **100** |

**Skor yorumu:**
- 80-100: Yüksek kalite
- 60-79: Orta kalite
- 40-59: Düşük kalite (LINT uyarısı)
- 0-39: UNKNOWN / quarantine

---

## 7. Depolama ve Güncelleme

- **Ham veri:** `data/raw/{kaynak}/{tarih}.jsonl`
- **Normalize:** `data/processed/companies.jsonl`
- **Veritabanı:** SQLite (`data/master.db`) veya PostgreSQL
- **Güncelleme sıklığı:** Aylık (Faz 1), haftalık (Faz 2+)
- **Diff/Version:** Her kayıt için `kaynak`, `cekilme_tarihi`, `versiyon`

---

## 8. Yasal Uyum

- **KVKK 6698** — Veri minimizasyonu, amaçla sınırlı işleme
- **Fikir ve Sanat Eserleri Kanunu** — Veri tabanı koruma
- **Türk Ceza Kanunu md. 243-245** — Bilişim suçları (yetkisiz erişim)
- **OSB websitesi kullanım şartları** — Her kaynak için ayrı kontrol

---

## 9. Etik Kod

1. Robots.txt'e uy
2. Sunucuyu yorma (rate limit)
3. Veriyi amacı dışında kullanma
4. Üçüncü partiye satma
5. Opt-out talebine saygı göster
6. Hata durumunda bildir

---

## 10. İlgili Wiki Sayfaları

- [[04_web_kazima_kaynak_arastirmasi]] — 12 kaynak detayı
- [[03_kvkk_ve_veri_politikasi]] — KVKK politikası
- [[01_veri_kaynagi_envanteri]] — Mevcut envanter
- [[10_ankara_osb_sentez]] — Kararlar