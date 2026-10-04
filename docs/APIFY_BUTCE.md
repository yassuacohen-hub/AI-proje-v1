# Apify Kullanım Bütçesi ve 10 USD Tavanı

**Görev:** `VERI-APIFY-BUTCE-01` · **Ölçüm tarihi:** 2026-10-03
**Kural:** D-66 (brif varsayımı ölçülür) · D-245/D-249 (beyan değil ölçüm, bilinmeyen 0 yazılmaz) · D-260 (ayar sonrası değer API'den okunur) · D-243 (prova diske yazmaz)

---

## 1. Ölçülen Durum (API'den okundu — ekran görüntüsü değil)

| Ölçüm | Değer | Kaynak |
|---|---|---|
| **Aylık harcanan** | **0.0000152605 USD** | `GET /v2/users/me/limits` → `data.current.monthlyUsageUsd` |
| **Konsolda ayarlı tavan** | **10 USD** | `GET /v2/users/me/limits` → `data.limits.maxMonthlyUsageUsd` |
| Tavan kullanım oranı | %0.0002 | ölçüm ÷ 10 |
| Fatura döngüsü | 2026-09-10 → 2026-10-09 | `data.monthlyUsageCycle` |
| Plan | `FREE` (`isPaying: false`) | `GET /v2/users/me` |
| Aylık ücretsiz kredi | 5 USD | `plan.monthlyUsageCreditsUsd` |
| Aylık taban ücret | 0 USD | `plan.monthlyBasePriceUsd` |
| Çalıştırılmış Actor | 0 (`actorCount`, `actorTaskCount`) | `data.current` |
| Harcama bileşeni | yalnız dış veri transferi 0.0000706 GB | `monthlyExternalDataTransferGbytes` |

**Yedek ölçüm (limits erişilemezse):** `GET /v2/users/me/usage/monthly` →
`data.totalUsageCreditsUsdAfterVolumeDiscount` = **0.0000152605 USD** (aynı değer).

> Harcama **artan** bir sayaçtır; iki ölçüm arasındaki fark yeni API çağrısından
> gelen dış veri transferidir. Tavanı etkilemez — ölçümü tekrarlamak değeri
> değiştirir, sıfırlamaz.

> Alan adları **tahmin edilmedi**, canlı yanıt üzerinden okundu. İlk denemede
> ölçülemedi sanıldı; sebep `/v2/v2` yol hatasıydı (aşağıya "Tavan" bölümü).

### Ölçüm komutu

```
python scripts/apify_butce_olc.py --tavan 10
python scripts/apify_butce_olc.py --tavan 10 --json
```

Çıkış kodu: `0` tavan içinde · `2` tavan aşıldı **veya** platform tavanı yerel
tavandan büyük · `3` ölçülemedi (token yok / ağ / 401 / alan bulunamadı).

---

## 2. Tavan: 10 USD

**Hedef durum:** Apify aylık harcama tavanı **10 USD**.

**Doğrulama (D-260):** Tavan konsolda **zaten 10 USD** olarak ayarlıydı. Değişiklik
gerekmedi; bu yüzden bu görevde konsola müdahale edilmedi. Ayar sonrası değer
API'den geri okunarak yukarıdaki tabloda belgelendi:

```
data.limits.maxMonthlyUsageUsd = 10
```

### Tavanı değiştirmek / kapatmak (gerektiğinde)

1. Apify Konsolu → **Billing** (Faturalama) → **Limits** → **Max monthly usage**
2. Değeri `10` USD olarak gir, **Save** de.
3. **Doğrulama zorunlu** — konsol değil, API:

```
python scripts/apify_butce_olc.py --tavan 10
```

`[PLATFORM TAVANI]` satırı `10` yazmalı. `10`'dan büyükse yerel bütçe
platformda **korunmuyor** demektir ve araç `rc=2` döner.

> Bir tuş: tavanı sıfırlamak da bir ayarlamadır — `10 USD` kuralı gereği tavan
> **silinmez**, her zaman `10` kalır.

### Kritik: `/v2` yol tuzağı

`.env` içindeki `APIFY_API_BASE_URL` değeri `.../v2` ile **bitiyor**. Buna bir de
`/v2` eklenirse istek `/v2/v2/...` olur ve Apify **404** döner; ölçüm "başarısız"
görünür ama sebep yanlıştır. `scripts/apify_butce_olc.py::api_kok()` son segment
`/v2` ise atıp bir kez ekler; her iki yazım biçimini de kabul eder ve test edilir.

---

## 3. Gerçek Fatura Riski

Üç ölçülen gerçek birlikte okunmalı:

1. `isPaying: false`, plan `FREE`, taban ücret **0 USD** → **şu an ücret kesilme riski 0 USD.**
2. Aylık **5 USD** ücretsiz kredi var; 10 USD tavanı bu kredinin üzerinde, yani
   ücretsiz planda platform 10 USD'ye değil **5 USD kredi bitiminde** durur.
3. Dolayısıyla 10 USD tavanı **yükseltme (upgrade) sonrası için güvenlik sınırıdır**,
   mevcut durumda bir fatura kalemi değildir.

**Kural:** Tavan `10`'da kalır ve ücretli plana geçişte de **ayarlanmadan önce**
bu belge + ölçüm aracıyla yeniden doğrulanır. `plan.id != FREE` olduğu anda
`docs/APIFY_BUTCE.md` elle güncellenir — araç planı sorgulamaz, dolayısıyla plan
değişimi tek başına `rc=2` üretmez. `rc=2` yalnız **ölçülen** iki durumda gelir:
tavan aşıldı, ya da `[PLATFORM TAVANI]` yerel tavandan büyük.

---

## 4. Güvenlik Notları

- Token **hiçbir koşulda** stdout'a yazılmaz; `Authorization` başlığı loglanmaz
  (`tests/test_apify_butce_olc.py::test_cikti_token_sicmaz`).
- Ölçüm **salt okunur** (`GET`). Hiçbir yerde limit değiştirme/varsayma yapılmaz.
- Bilinmeyen değer `0` **yazılmaz**; `rc=3` döner ve "ölçülemedi" denir (D-249).
  Böylece sıfır harcama ile ölçülememe ayırt edilir.
- Token yoksa araç `rc=3` verir ve belge "doc-only" kalır; uydurma limit yazılmaz.

## 5. Testler

```
python -m pytest tests/test_apify_butce_olc.py -q
```

**17 passed** — kapsam: `/v2` yol birleştirme (5 durum), `.env` ayrıştırma,
token sızıntısı, ölçülememe durumları, tavan aşımı, platform tavanı > yerel
tavan güvenlik açığı, `usage/monthly` yedeğine düşme, JSON/metin çıktı.
