# Y21 — İSKUR Kurumsal Eşleştirme Verisi (sahip: arastirmaci)

> Ana referans: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md` (V9)
> Bağlı görev: Y19 smart matching MVP (`/api/match` — canlı)

## Görev
İSKUR'dan **kurumsal işgücü sinyali** alıp eşleştirme motoruna (Y19) katkı sağlayıp sağlamayacağını değerlendir. Çıktı: erişim yöntemi + risk analizi + veri modeli önerisi.

## Koordinatör Risk Uyarıları (ÖNCE BUNLARI DOĞRULA)

| # | Risk | Önem | Doğrulama sorusu |
|---|------|------|------------------|
| 1 | **Kullanım şartları**: İSKUR scraping'e izin vermiyor olabilir; resmî izin olmadan kazıma yasal risk | 🔴 Yüksek | İSKUR'un resmî API'si / açık veri portalı var mı? robots.txt ne diyor? |
| 2 | **KVKK**: ilanlardaki iletişim bilgileri (İK yetkilisi e-posta/telefon) **bireysel veri** — ham aktarım KVKK kapsamı | 🔴 Yüksek | Hangi alanlar kamuya açık ve anonimleştirilebilir? (firma adı + pozisyon + NACE yeterli, kişi bilgisi toplanmamalı) |
| 3 | **Entity resolution yükü**: ilandaki firma adı serbest metin; mevcut 14k firma ile eşleşmeyen kayıtlar "karantina"ya düşer | 🟡 Orta | Örnek 50 ilanla eşleşme oranı tahmin edilebilir mi? |
| 4 | **Önyargı (model) riski**: "ilan yayınlamamış = pasif firma" TÜMDÜĞELİMİ; ilan yokluğu kapasite yokluğu değil | 🟡 Orta | Veri, pozitif sinyal olarak mi kullanılacak? (negatif etiket YASAK) |
| 5 | **Lisans/attribution**: verinin ticari platformda yeniden dağıtımı lisans gerektirebilir | 🟡 Orta | İSKUR veri lisans şartları + kaynak gösterme zorunluluğu |

## Aranacak Kanallar
1. **İSKUR resmî açık veri / API** (acikveri.biz.gov.tr, iskur.gov.tr veri paylaşım sayfası)
2. **e-Devlet servisleri** üzerinden firma işgücü sinyalleri
3. Alternatif: şirket kariyer sayfaları (P6-2 "Company Career Pages Scraper" göreviyle birleşebilir)

## Beklenen Çıktı
`workspace/external/<ajan>/output/Y21_iskur_analiz.md`
- Erişim yöntemi tablosu (kanal | veri | hukuki durum | KVKK notu | önerilen kullanım)
- İlk 3 öneri (sadece risk kontrolü geçen kanallar)
- Y19 match skoruna entegrasyon önerisi (örn. "ilan yayınlıyor" = +kanıt gücü, pozitif-only)

## Sistem V2 bağlamı
- Yerel PG ile test: `DATABASE_URL=postgresql+psycopg://huginn:huginn_local_dev@localhost:5433/huginn`
- Mevcut match: `web_app.py → _NACE_KOMSU`, `api_match()` — ilan sinyali `kanit` bileşenine eklenebilir
- KVKK maskeleme: `apply_kvkk_mask` — ham kişisel veri ASLA API'ye koyma
