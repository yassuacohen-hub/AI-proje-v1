---
tarih: 2026-09-28
karar: D-250
sozlesme: K-6
durum: OLCULDU
firma_sayisi: 9412
puan_surumu: v1
---

# Kimlik Dosyası Tamlığı — Başlangıç Ölçümü

> Bu belge **başlangıç fotoğrafıdır**. Ağırlık seti değişirse yeniden ölçülür ve
> yeni tarihli belge yazılır; bu belge silinmez (kıyas tabanı).

## 1. Ne ölçüyoruz

**Kimlik Dosyası Tamlığı (0–10):** her işletmenin kimlik dosyasının ne kadar
dolu olduğu. Düşük puan firmanın kusuru değil, **bizim toplama boşluğumuzdur**.

Ağırlık seti: sözleşme K-6 (10.0 puan, kimlik omurgası 6.0 + erişim 4.0).

## 2. Alan doluluğu

| Alan | Ağırlık | Dolu | Oran |
|---|---|---|---|
| Ticaret unvanı | 1.0 | 9412 | %100 |
| NACE kodu | 1.0 | 8294 | %88.1 |
| Telefon | 1.5 | 8255 | %87.7 |
| Adres | 1.5 | 5798 | %61.6 |
| İnternet sitesi | 0.3 | 5449 | %57.9 |
| E-posta | 0.7 | 4038 | %42.9 |
| VKN | 1.5 | 770 | %8.2 |
| Vergi dairesi | 0.5 | — | **KOLON YOK** |
| MERSİS no | 1.0 | — | **KOLON YOK** |
| Ticaret sicil no | 1.0 | — | **KOLON YOK** (620 değer bekliyor) |

Tam kimlik dosyası: **128 firma (%1.4)**.
VKN hariç hepsi tam: **2157 firma (%22.9)**.

## 3. Ulaşılabilir tavan — bugün 6.0 / 10

```
10.0  toplam ağırlık
−2.5  vergi dairesi (0.5) + MERSİS (1.0) + sicil (1.0) — kolon yok, kaynak yok
−1.5  VKN — kaynak yok (GİB erişimi belirsiz)
─────
 6.0  bugünkü tavan
```

**Bugün hiçbir firma 10 alamaz.** Panelde bu satır sabit gösterilir.
Ortalama puanın yükselmesi değil, **tavanın yükselmesi** gerçek ilerlemedir.

Tavan yükselme senaryoları:

| Adım | Yeni tavan |
|---|---|
| SEMA-VKN-01: 3 kolon eklenir + 620 sicil taşınır | 7.0 |
| MERSIS-KAYNAK-01 başarılı | 8.0 |
| MERSİS → VKN türetilir | 9.5 |
| GİB e-arşiv listesi + vergi dairesi | 10.0 |

## 4. Kayıp tablosu — yol haritası budur

`eksik firma × ağırlık = kayıp puan`. En büyük kayıp = sıradaki iş.

| Sıra | Alan | Eksik | Ağırlık | Kayıp |
|---|---|---|---|---|
| 1 | **VKN** | 8642 | 1.5 | **12963** |
| 2 | MERSİS no | 9412 | 1.0 | 9412 |
| 3 | Ticaret sicil no | 9412 | 1.0 | 9412 |
| 4 | Adres | 3614 | 1.5 | 5421 |
| 5 | Vergi dairesi | 9412 | 0.5 | 4706 |
| 6 | E-posta | 5374 | 0.7 | 3762 |
| 7 | Telefon | 1157 | 1.5 | 1736 |
| 8 | NACE kodu | 1118 | 1.0 | 1118 |
| 9 | İnternet sitesi | 3963 | 0.3 | 1189 |
| 10 | Ticaret unvanı | 0 | 1.0 | 0 |

Tablo kendi kendini günceller: bir alan doldukça kaybı düşer, sıralama değişir,
öncelik tartışması ortadan kalkar.

## 5. Kritik içgörü — MERSİS numarası VKN'yi *içinde taşır*

**Ürün sahibi bilgisi (2026-09-28):**

> Tüzel kişilerde 16 haneli MERSİS numarasının **ilk 10 hanesi = VKN.**

Bu, "MERSİS VKN'yi de getirir" tahminini kesinleştirir ve daha güçlü hâle
getirir: VKN **ikinci bir sorguyla toplanmaz, aritmetikle türetilir.**

```
MERSİS: 0123456789 01234
        └── VKN ──┘
vkn = mersis_no[:10]
```

Sonuçları:

1. **Kayıp tablosunun 1. ve 2. sırası tek alanla kapanır** — 12963 + 9412 =
   **22375 puan**, toplam kaybın %48'i. Tek kaynak, tek hamle.
2. **Çift doğrulama bedava gelir.** Türetilen VKN mod-11 sağlamasından geçmezse
   MERSİS numarası yanlış okunmuş demektir. Yani VKN sağlaması, MERSİS alanının
   da denetleyicisidir. Ek kod yok — `kimlik_dogrula()` zaten var (K-1).
3. **MERSİS toplama GİB'den önce gelir.** GİB e-arşiv listesi yalnızca
   *e-belge kullanan* mükellefleri kapsar (kısmi); MERSİS ise tescilli her
   tüzel kişiyi kapsar ve VKN'yi doğrudan verir.

⚠️ **Sınır — gerçek kişi işletmeleri.** Bu kural **tüzel kişi** içindir. Şahıs
firmalarında kimlik numarası TCKN'dir ve MERSİS numarasının ilk 10 hanesinden
TCKN türetilemez (TCKN 11 hane). Türetim yalnızca `tuzel_tip = 'tuzel'` için
uygulanır; aksi hâlde 8642 firmaya yanlış VKN yazılır — D-245'in aynısı
(doluluk ≠ geçerlilik) yeni kılıkta.

⚠️ MERSİS **erişimi** hâlâ **ÖLÇÜLMEDİ** — `MERSIS-KAYNAK-01` açık. Bilinen
şey türetme kuralı; bilinmeyen şey numaranın toplanabilirliği.

## 6. Ölçüm öncesi düzeltilen hatalar

| Bulgu | Etki |
|---|---|
| 2 çelişen puan formülü (`quality_metrics.py` + panel SQL) | Aynı firma iki farklı puan gösteriyordu |
| 583 bayat skor | Ağırlık değişince eski puan sessizce yanlış kaldı → `puan_surumu` kolonu kararı (D-250/6) |
| 6344 firmanın `source_records` bağı kopuk, 8748 kayıt yetim | `VERI-KAYNAK-BAG-01` açık, ayrı iş |
| Kolon adı `data_quality_score` | "Firma kalitesi" sanılıyordu; asıl ölçülen bizim toplama başarımız → ad değişti |

## 7. Uygulama sırası

1. `SEMA-VKN-01` — 4 kolon göçü (`vergi_dairesi`, `mersis_no`,
   `ticaret_sicil_no`, `sicil_dairesi`) + `puan_surumu`
2. 620 sicil değerini `sicil_dogrula()` üzerinden yeni kolonlara taşı
3. `kimlik_tamligi()` tek kapısı — ağırlık sözlüğü + sürüm, eski 2 formül silinir
4. Mandal: ağırlık toplamı 10.0 · doğrulanmamış değer 0 puan · sürüm eşleşmesi
5. Panel: dağılım + tavan satırı + kayıp tablosu
6. `MERSIS-KAYNAK-01` erişim denemesi
7. Yeniden ölç → bu belgenin yeni tarihli sürümü

## İlgili Nodlar

- [[../AGENTS]]
- [[VERI_KALITE_SOZLESMESI]]
- [[KAPSAM_KIYASI_2026-09-28]]
