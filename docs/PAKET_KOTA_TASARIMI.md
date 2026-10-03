# Paket · Kota · Kredi Cüzdanı — tasarım (2026-10-03)

**Durum:** Tasarım. Kod yok. Ürün sahibi kararı: "Başlangıç 0 ₺ olabilir; Premium daha fazla arama kotası + kredi bazlı detay rapor; ödeme esnek."

## 1. Mevcut (ölçüldü)

| Parça | Var mı | Nerede |
|---|---|---|
| `packages(name, price, features JSON, icon)` | var | `src/company_master/paketler.py` |
| `company_packages(firma, paket, durum)` | var | aynı |
| Kota sayacı | **yok** | `BORC-KREDI-PAKET-01` |
| Kredi cüzdanı | **yok** | aynı borç |
| Müşteri `plan` alanı dolduran kod | **yok** | `BORC-PLAN-ALANI-01` |
| Firma sosyal adresleri | **0 gerçek** | `BORC-SOSYAL-ADRES-SAHTE-01` |

## 2. İki sayaç — neden iki?

| Sayaç | Ne | Ne zaman sıfırlanır | Satın alınır mı |
|---|---|---|---|
| **Aylık kota** | pakete dahil arama/rapor hakkı | her ay başı | hayır, paketle gelir |
| **Kredi cüzdanı** | ek hak | hiç; birikir | evet, istendiği kadar |

Sıra: önce kota düşer, kota bitince cüzdan düşer, ikisi de 0 ise "kota bitti, kredi alın" mesajı. Fiyat/kota değişince yalnız `packages` satırı güncellenir; kod değişmez.

## 3. Başlangıç matrisi (öneri — ürün sahibi değiştirir)

| Paket | Fiyat | Mimir arama / ay | Detay rapor | Haber kaynakları |
|---|---|---|---|---|
| Başlangıç | 0 ₺ | 20 | kredi ile (1 rapor = 7 kredi) | DMO, RG |
| Pro | aylık | 200 | 5 dahil + kredi | + Google News, LinkedIn, patent |
| Premium | aylık | 1000 | 20 dahil + kredi | + Instagram, Facebook, iş ilanı |

Rakamlar **ölçülmedi**; sayı tutmak için ilk 30 gün gerçek kullanım loglanır, sonra düzeltilir.

## 4. `packages.features` şeması (yeni tablo YOK — tembel yol)

```json
{
  "arama_kota_ay": 200,
  "rapor_kota_ay": 5,
  "haber_kaynaklari": ["dmo", "rg", "google_news", "linkedin"],
  "arac_dongusu": true
}
```

Admin paneli: paket düzenleme ekranında 2 sayı kutusu + 6 onay kutusu. Rapor/haber üretilirken `firma_paketleri_getir()` → `features.haber_kaynaklari` filtre. `BORC-PLAN-ALANI-01` böylece kapanır (`plan` alanı yerine paket ilişkisi okunur).

**Yapılan (2026-10-03, daha tembel yol):** JSON yerine koda sabit sözlük `paketler.PAKET_KAYNAKLARI` (4 fiyat tier'ı → kaynak kümesi) + `firma_haber_kaynaklari(company_id)`. Ölçüm `scripts/paket_olc.py`: `packages` ve `company_packages` **boş** — panel kutuları ilk gerçek müşteriye kadar yazılmaz. Test `tests/test_paket_kaynaklari.py` (5).

## 5. Kullanım ve cüzdan — en az şema

| Tablo | Kolonlar | Not |
|---|---|---|
| `kullanim_log` | id, company_id, tur (`arama`/`rapor`), kaynak_adi, maliyet_kredi, ts | her çağrı 1 satır; kota = ay içi SUM |
| `kredi_hareket` | id, company_id, miktar (+/−), neden, ts | bakiye = SUM; ayrı bakiye kolonu tutulmaz |

İki tablo, iki SUM. Ödeme sağlayıcısı (iyzico/Stripe) webhook'u yalnız `kredi_hareket`'e + satır yazar; esneklik buradan gelir.

**Daha tembel alternatif:** `kredi_hareket` yok, yalnız `companies.kredi_bakiye` int kolon. İlk 10 müşteriye yeter; itiraz/iade gelince hareket tablosu eklenir.

## 6. Sosyal adres keşfi (önkoşul — `BORC-SOSYAL-ADRES-SAHTE-01`)

| Adım | Araç | Maliyet |
|---|---|---|
| 1 | kazıyıcıda `ostim` içeren href'i ele | 0 |
| 2 | brave `site:linkedin.com/company "<unvan>"` → ilk sonuç + güven puanı | 0 (9Router) |
| 3 | 100 firma pilot, elle %10 örnek doğrulama | 1 saat |
| 4 | admin panelde ✓/✗ onay sütunu | yarım gün |

Her ağ ayrı kolon, `kaynak_adi="brave-kesif"` (K-2).

## 7. Sıra

1. §4 `features` şeması + panel kutuları + rapor filtresi
2. §6 adım 1-3 (keşif pilotu)
3. §5 `kullanim_log` + kota düşümü
4. Kredi cüzdanı + ödeme webhook'u (ilk ödeme talebi gelince)
5. Apify pilot 10 firma (≤10 $)

## Öz-eleştiri
- Kota rakamları tahmin; ölçümsüz yazdım, §3'te işaretledim.
- Kredi cüzdanı YAGNI riski: ilk müşteri gelmeden yazılırsa boşa gider → sıra 4'e ittim.
- Sosyal adres "kısmen var" dediğim önceki beyan **yanlış çıktı** (0 gerçek); ölçmeden söylemiştim.

## Ilgili Nodlar
- [[BORC_DEFTERI]]
- [[SAGLAYICI_OLCUMU_2026-10-03]]
- [[mimir_sistem_promptu]]
- [[HEDEF_VERI_KAPSAMI]]
