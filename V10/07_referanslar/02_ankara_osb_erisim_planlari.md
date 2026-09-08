# Ankara OSB Erisim Planlari

Baglantilar: [[00-Home]] · [[01_veri_kaynagi_envanteri]] · [[01_veri_toplama_modeli]]

Bu belge, [[01_veri_kaynagi_envanteri]] sonucu tespit edilen 4 OSB (Ivedik, ASO 1, ASO 2-3, Baskent) icin fiili erisim yontemini, robots.txt durumunu, yasal dayanak ve teknik uygulama planini icerir.

## 1. Ivedik OSB

- **Web sitesi:** https://www.ivedik.org.tr
- **robots.txt:** https://www.ivedik.org.tr/robots.txt
- **Erisim yontemi:** Manuel indirme (PDF/Excel uye listesi) + sekreterlik talebi
- **Yasal dayanak:** OSB Kanunu (4562 sayili) md. 9 - uye listeleri kamuya acik bilgi kategorisindedir; sekreterlik yazili talep ile paylasim yapar
- **Teknik uygulama plani:**
  1. `robots.txt` indirilip `Allow: /` (veya `Disallow:` bos) oldugu dogrulanir
  2. Web sitesinde liste yayinlanmiyorsa OSB sekreterligine resmi yazi ile Excel/PDF talep edilir
  3. Alinan dosya `scripts/ingest_ivedik.py` ile normalize edilip `source_records` tablosuna yazilir
  4. Yenileme sikligi: Ceyreklik (3 ayda bir)
- **Guven skoru:** 0.85 (OSB tarafindan dogrulanmis veri, guncellik garantisi yuksek)
- **Risk:** Sekreterlik yaniti 2-4 hafta gecikebilir; arada web sitesinde yayinlanan haberler/duyurular ile capraz kontrol onerilir
- **Gerekli:** Hukuk onayi (KVKK ve OSB Kanunu md.9)

## 2. ASO 1. OSB (Ankara Sanayi Odasi 1. OSB)

- **Web sitesi:** https://www.aso1osb.org.tr
- **robots.txt:** https://www.aso1osb.org.tr/robots.txt
- **Erisim yontemi:** Python Custom Script (web scraping) - dinamik liste
- **Yasal dayanak:** ASO mevzuatinda uye listeleri acik; OSB uyelik kosullari kamuya acik bilgi
- **Teknik uygulama plani:**
  1. `robots.txt` kontrol edilir; `Disallow: /` yoksa scraping uygundur
  2. Sayfa kaynagi (JS veya SSR) analiz edilir; gerekirse Selenium/Playwright kullanilir
  3. `src/company_master/etl/scrapers/aso1_scraper.py` yazilir: pagination, rate-limit 2 sn, 50 firma/sayfa
  4. Capraz dogrulama: ASO merkezi uye veritabani ile VKN eslestirme
- **Guven skoru:** 0.90
- **Risk:** JS tabanli sayfa ise scraper kirilgan; her 3 ayda regression testi zorunlu
- **Gerekli:** Rate-limit, log dosyasi `logs/aso1_scrape.log`, hata izolasyonu

## 3. ASO 2-3 OSB

- **Web sitesi:** https://www.aso2-3.org.tr (yoksa ASO ana site uzerinden)
- **robots.txt:** Teyit edilecek (muhtemelen yok)
- **Erisim yontemi:** Manuel indirme (ASO merkez koordinasyonu)
- **Yasal dayanak:** ASO 2 ve 3 tekil web sitesine sahip degil; ASO genel sekreterligi uzerinden toplu talep
- **Teknik uygulama plani:**
  1. ASO genel sekreterligine yazili talep ile uye listesi (Excel) istenir
  2. Manuel olarak indirilen dosya `data/aso2-3/uyeler.xlsx` olarak kaydedilir
  3. `scripts/ingest_aso23.py` ile normalize + `source_records`a yukleme
  4. Manuel kontrol: vergi_no, adres, telefon alanlari bos firma orani
- **Guven skoru:** 0.85
- **Risk:** Tekil OSB'ler arsinda veri tutarsizligi (alan farkliliklari); normalize sirasinda `nace_code` bos firma icin fallback
- **Gerekli:** Tek seferlik hukuk onayi; yenileme talebi her ceyrek

## 4. Baskent OSB

- **Web sitesi:** https://www.baskentosb.org.tr
- **robots.txt:** https://www.baskentosb.org.tr/robots.txt
- **Erisim yontemi:** Manuel indirme (offline paylasim)
- **Yasal dayanak:** OSB Kanunu md.9; yazili/e-posta talep ile uye listesi
- **Teknik uygulama plani:**
  1. robots.txt kontrol edilir; site acik olsa da liste yayinlanmiyor olabilir
  2. OSB bilgi istek formu doldurulur, resmi yazi ile talep edilir
  3. Gelen Excel `data/baskent/uyeler.xlsx` olarak saklanir
  4. `scripts/ingest_baskent.py` ile normalize
  5. Veri kalitesi: sektor ve adres alanlari genelde dolu, vergi_no ve parsel genelde bos
- **Guven skoru:** 0.80
- **Risk:** OSB yanit suresi degisken; 1-2 ay gecikebilir
- **Gerekli:** Her ceyrek otomatik hatirlatma scripti

## 5. Ortak Uygulama Kurallari

| Kural | Aciklama |
|---|---|
| Rate-limit | Web scraping kaynaklarinda en az 2 sn; manuel indirilen veri icin gerek yok |
| robots.txt | Her scrape oncesi kontrol; `Disallow: /` ise scrape durdurulur |
| KVKK | Bireysel email filtrelenir (`gmail.com`, `hotmail.com` vb.); telefon KVKK kapsaminda kisisel veri sayilir, acik riza olmadan paylasilmaz |
| Loglama | Her OSB icin ayri `logs/<osb>_scrape.log`; hata ve basarili kayit sayisi |
| Idempotency | `content_hash` ile tekrar eden kayitlar eklenmez; yeniden calistirma guvenli |
| Yenileme | Ceyreklik otomatik hatirlatma; `scripts/remind_osb_renewal.py` ile Telegram bildirimi |
| Hata izolasyonu | Bir OSB basarisiz olursa digerleri etkilenmez; ayri try/except bloklari |

## 6. Yasal Uyumluluk Kontrol Listesi

- [ ] OSB Kanunu md.9 - uye listelerinin acik bilgi sayilmasi
- [ ] KVKK - acik riza olmadan kisisel veri paylasimi yasak
- [ ] 5651 sayili Kanun - web scraping icin "hukuka aykiri erisim" riski; robots.txt ve ToS kontrolu
- [ ] Ticari veri paylasim sinirlari - ucretli/devlet kaynakli verilerin kullanimi
- [ ] Sozlesme - OSB ile veri paylasim protokolu (uzun vadeli)

## 7. Sonuc ve Aksiyon Plani

| OSB | Aksiyon | Sorumlu Ajan | Tarih |
|---|---|---|---|
| Ivedik | Yazili talep gonder + scraper draft | Gelistirici + Arastirmaci | Eylul 2026 |
| ASO 1 | robots.txt + scraping PoC | Gelistirici | Eylul 2026 |
| ASO 2-3 | ASO merkez talep | Arastirmaci | Ekim 2026 |
| Baskent | Bilgi istek formu + scraper | Gelistirici + Arastirmaci | Ekim 2026 |

## 8. Referanslar

- [[01_veri_kaynagi_envanteri]] - temel envanter tablosu
- OSB Kanunu (4562 sayili) - yasal dayanak
- KVKK (6698 sayili) - kisisel veri koruma
- V10/09_kurallar_ve_promptlar/10_vpn_kurali - VPN uyarisi (erisim hatasi durumunda)