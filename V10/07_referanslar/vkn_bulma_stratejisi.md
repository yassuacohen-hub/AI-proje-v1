# VKN Bulma Stratejisi — Firma Web Siteleri

> **Tarih:** 2026-09-06 · **Durum:** Aktif araştırma (P0-3 destek)
> **İlgili görevler:** [[../TODO|TODO P0-3]], P1-4, P2-1
> **Araç:** `scripts/vkn_web_scraper.py`

## 1. Neden Web?

- OSTİM rehberinde VKN yok (5485 kayıtta `vergi_no` ~boş), ASO'da yalnız
  ticaret sicil no var. MERSIS API başvurusu dış bağımlı (P2-1, bekliyor).
- **Firma web siteleri** VKN'nin en erişilebilir kamuya açık kaynağı:
  yasal zorunluluk gereği footer'da ve KVKK/aydınlatma metnlerinde
  şirket kimliği + Vergi No gösterilir.
- Kaynak önceliği (entity_resolution.py `SOURCE_PRIORITY` uyumlu): mersis >
  gib > aso > ostim > web > diger. Web kazıması "ostim/aso sonrası" doldurucu.

## 2. VKN Sitede Nerede Bulunur? (öncelik sırası)

| Yer | Bulunma olasılığı | Not |
|-----|------------------|-----|
| Footer (her sayfada) | Yüksek | `Vergi No: 1234567890` / `V.D. Ankara No: ...` |
| KVKK / Aydınlatma Metni | Yüksek | Şirket unvan + adres + vergi no formda |
| İletişim sayfası | Orta | Form alt bilgisi veya kurumsal bilgi bloğu |
| Hakkımızda / Kurumsal | Orta | Tarihçe + yasal künye |
| E-fatura / E-arşiv bilgisi | Orta-Düşük | "e-fatura mükellefiyiz, VKN: ..." |
| Çerez/gizlilik politikası | Düşük | Şirket künyesi bölümü |

## 3. Çıkarma Yöntemi (`vkn_web_scraper.py`)

1. **Aday siteler:** merged veride `web_sitesi` dolu + `vergi_no` boş firmalar.
2. **Yol denemesi:** `/`, `/hakkimizda`, `/iletisim`, `/kurumsal`, `/kvkk`,
   `/hakkinda`, `/tr/hakkimizda`, `/tr/iletisim`, `/about`, `/contact`.
3. **Regex desenleri:** `Vergi No[:]? 10 hane`, `V.D. ... 10 hane`,
   `Vergi Dairesi ... 10 hane`, `Tax No ... 10 hane`.
4. **Checksum doğrulama (zorunlu):** Türk VKN kontrol toplamı —
   `vkn_gecerli_mi()`. Bu adım telefon (312/5xx başlangıçlı 10 hane),
   sicil no, parsel no gibi yanlış pozitifleri büyük oranda eler.
5. **Nazik kazima:** robots.txt kontrolü (alinamazsa çekim yok),
   2 sn gecikme, site başına maks. 2 VKN, sayfa başına tek istek.

## 4. Yanlış Pozitif Riskleri ve Önlemler

| Risk | Önlem |
|------|-------|
| Telefon numaraları (10 hane) | Checksum + "vergi/v.d." bağlam şartı |
| Tescil/sicil numaraları | Checksum |
| Sayfadaki başka firmanın VKN'si (partner referansı) | İlk 2 geçerli aday alınır + insan onayı örneklemi |
| Matematiksel geçerli ama sahte numara | VKN sorgu servisi ile çapraz kontrol (ileri) |

## 5. Hukuk / KVKK Notu

- VKN, ticari işletme kimlik bilgisidir; kamuya açık yayım amaçlıdır ve
  işletme verisi kapsamında değerlendirilir.
- Yalnızca şirket kimlik bilgisi toplanır; kişisel veri (yetkili adı vb.)
  bu kazımanın hedefi değildir.
- robots.txt'ye uyulur; engellenen siteler atlanır ve kayıt altına alınır.

## 6. Operasyon

```bash
# Parça parça koştur (VPN aktifken ağ hataları olabilir — VPN kuralı 10_vpn_kurali.md):
python scripts/vkn_web_scraper.py --limit 50

# Çıktı: data/merged/vkn_web_bulunan.jsonl
# Sonraki adım: bulunan VKN'leri companies.tax_number'a yaz (update scripti)
```

## 7. Web Dışı Alternatifler (web yetersiz kalırsa)

1. **GİB VKN Doğrulama** (vkn.gov.tr) — sorgu servisi captcha/bot korumalı;
   tekil doğrulama için uygun, toplu kazımaya uygun değil.
2. **MERSİS** — P2-1 API başvurusu beklemede; onay gelirse birincil kaynak.
3. **e-Fatura portalı firmaları listesi** — VKN içerir, erişim koşulları araştırılacak.
4. **Ticaret odası rehberleri** (ASO, TOBB) — üyelik/erasılım koşullu.
5. **Google/arama motoru** `"firma unvanı" vergi no` — elle/iç ajan kontrolü,
   yüksek doğruluk, ölçeklenmesi zor.

## 8. Başarı Ölçütü

- P0-3 hedefi: kalite skoru 39.97 → 50+. VKN doluluğu ağırlığı %20.
- Web kazıması %15-25 verimle (web'i dolu kayıtlar içinde) skoru
  yaklaşık 4-7 puan yükseltmelidir. Ölçüm: her 100 sitelik parti sonrası
  kalite raporu.
