# API Sorun Teşhis Playbook'u

> Sahip talimatı (2026-09-17): *"BU ÇALIŞMA GÜZEL OLDU KAYDET, SONRAKİ TARİHLERDE BU TİP SORUNLARI BU ŞEKİLDE ÇALIŞALIM."*
> Bir API anahtarı / sağlayıcı çalışmadığında izlenecek sabit sıra. Tahmin yok, kanıt var.
>
> İlgili: [docs/API_ANAHTARLARI.md](API_ANAHTARLARI.md) (envanter) ·
> [docs/ARASTIRMA_API_PLAN_2026-09-17.md](ARASTIRMA_API_PLAN_2026-09-17.md) (örnek vaka raporu)

## Adım 1 — Ölç, tartışma

```
python scripts/api_anahtar_testi.py            # tüm sağlayıcılar
python scripts/api_anahtar_testi.py groq       # tek sağlayıcı
```

Script yalnız **son 4 karakter** basar; anahtar tam değeri asla terminale/loga yazılmaz.
Yeni sağlayıcı eklemek = `SAGLAYICILAR` tuple'ına **tek satır**.

## Adım 2 — HTTP kodunu oku, kodun söylediğini yap

| Kod | Anlam | İlk aksiyon |
|-----|-------|-------------|
| 200 | çalışıyor | iş bitti |
| 400 | istek gövdesi hatalı | **bizim** test/istek gövdesini düzelt (sağlayıcı suçlu değil) |
| 401 | anahtar geçersiz / iptal | panelden yeni anahtar üret |
| 402 | bakiye yok | ödeme kararı sahibe |
| 403 | anahtar geçerli, **yetki/plan kapalı** | kredi · şart kabulü · org izni · proje eşleşmesi |
| 404 | yol yanlış | `*_BASE_URL` / endpoint yolunu doğrula |
| 410 | endpoint **kalıcı kapalı** | o yolu bırak, resmî alternatifi bul |
| 429 | kota / devre kesici | eşiği yükselt ya da bekle |

**Kural:** 403 ≠ 401. 403'te anahtar üretmek çoğu zaman işe yaramaz — nitekim BazaarLink'te yaramadı.

## Adım 3 — Önce env, sonra sağlayıcı

Hata sağlayıcıda sanılıp aslında bizde çıkan tipik bulgular (gerçek vakalar):
- `GROQ_BASE_URL=https://groq.com` → doğrusu `https://api.groq.com/openai/v1`
- `.env` ile `.env.example` ad uyuşmazlığı (`BAZARLINK_URL` vs `BAZARLINK_API_URL`, `FRECLAW` vs `FIRECRAWL`)
- Anahtar adında Türkçe karakter / ASCII dışı ad
- Kodun okuduğu ad ile `.env`'deki ad farklı (örn. kod yalnız `APIFY_TOKEN` okur)

Bu üçü temizlenmeden sağlayıcı suçlanmaz.

## Adım 4 — Sağlayıcının kendi duyurusunu oku

Panel ekranı yetmez; **ana sayfa duyurusu + docs + changelog** okunur.
BazaarLink vakasında kök neden ancak böyle bulundu: `/api/v1/agents/register`
**2026-09-05'te 410** olmuş, o uç noktadan dağıtılan tüm anahtarlar iptal edilmiş.
Panel bunu söylemiyordu.

Araç: `tavily`/`exa`/`brave` + `firecrawl` ile sayfa metnini çek, geçici script `data/_tmp/`'ye yaz, iş bitince **sil**.

## Adım 5 — Terim uydurma yasağı

Panelde gördüğün **makine çevirisi** terimi olduğu gibi aktarma, aslını bul.
Örnek hata (roo): "Hasar Temsilcisi" → "temsilci botu" diye aktarıldı; aslı **"Claim Agent"**,
düğme **"Claim"**. Bot yok. Yanlış terim sahibi yanlış ekrana gönderir.

## Adım 6 — Yaz, sonra kapat

1. `docs/API_ANAHTARLARI.md` envanter satırını güncelle (durum + neden + aksiyon).
2. Açık vaka için tarihli rapor: `docs/ARASTIRMA_API_PLAN_<tarih>.md` — teşhis, kanıt, **sahip için numaralı adımlar**, kalırsa hata tablosu.
3. Sahibin yapması gerekeni ve **roo'nun neden yapamayacağını** açıkça yaz (e-posta doğrulaması, ödeme, hesap açma).
4. Geçici script/çıktıları sil.
5. Bloke iş yoksa **öncelik: düşük** yaz ve ertele. Çalışan alternatif varken ölü sağlayıcı kovalanmaz.

## Sahip için sabit not

Sahip istediği zaman **"API araştırma planı raporu"** ister; rapor dosyası bu yüzden
her zaman güncel, tarihli ve kanıtlı tutulur.
