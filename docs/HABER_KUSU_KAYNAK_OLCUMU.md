# Haber Kuşu Kaynak Ölçümü — F2 (ALTYAPI-MIMIR-HABER-KUSU-01)

**Tarih:** 2026-10-03 · **Ölçülen:** `src/company_master/odin_ai/arac_dongusu.py::KAYNAK_HARITASI`
**Yöntem:** 3 tur, toplam 38 aday adres. Her adres `urllib` + tarayıcı UA ile
GET; ölçülen HTTP durum kodu, süre (sn), gövde karakter sayısı ve **içerik sinyali**.

> **Kural (ölçüm ilkesi):** HTTP 200 tek başına kanıt **değildir**. Gövde
> giriş duvarı / boş JS kabuğu ise adres haritaya giremez. "TEMIZ" = gövdede
> `giriş yap / log in / enable javascript / captcha` işareti yok **ve** etiketli
> metin 200 karakteri aşıyor.

## Kabul Edilenler (haritaya giren 7 adres)

| # | paket kodu | etiket | adres | HTTP | sn | karakter | sinyal |
|---|---|---|---|---:|---:|---:|---|
| 1 | `dmo` | DMO yayındaki ihaleler | `https://www.dmo.gov.tr/Ihale/Liste?type=1` | 200 | 1.86 | 143105 | TEMİZ |
| 2 | `dmo` | DMO Sağlık Market ihaleleri | `https://www.dmo.gov.tr/SM/Ihale` | 200 | 1.84 | 133697 | TEMİZ |
| 3 | `rg` | Resmî Gazete (bugünkü sayı) | `https://www.resmigazete.gov.tr/` | 200 | 2.56 | 200839 | TEMİZ |
| 4 | `rg` | Resmî Gazete (eski sayılar arşivi) | `https://www.resmigazete.gov.tr/eskiler/` | 200 | 0.88 | 200992 | TEMİZ |
| 5 | `patent` | TÜRKPATENT (patent kaydı) | `https://www.turkpatent.gov.tr/` | 200 | 1.01 | 440512 | TEMİZ |
| 6 | `is_ilani` | Eleman.net (iş ilanları) | `https://www.eleman.net/` | 200 | 0.88 | 326547 | TEMİZ |
| 7 | `google_news` | Google Haberler RSS (TR) | `https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr` | 200 | 1.11 | 114395 | TEMİZ |

Paket kodu dağılımı: `dmo` 2 · `rg` 2 · `patent` 1 · `is_ilani` 1 · `google_news` 1.

## Reddedilenler — gerekçesiyle

| adres | HTTP | karakter | sinyal | neden haritaya GİRMEDİ |
|---|---:|---:|---|---|
| `linkedin.com` | 200 | 143285 | `log in` / `sign in` | Giriş duvarı; içerik okunmuyor |
| `instagram.com` | 200 | 645756 | TEMİZ | Metin = sadece `Instagram` — 645 KB JS kabuğu, haber yok |
| `facebook.com` | 400 | 0 | — | HTTP 400 |
| `linkedin` / `instagram` / `facebook` paket kodu | — | — | — | `PAKET_KAYNAKLARI`'nda var ama **adres ölçülemedi** |
| `turkpatent.gov.tr/Tarama/` | 200 | 52804 | TEMİZ | Gövde metni `Hata 404 Anasayfaya Dön` — sahte 200 |
| `turkpatent.gov.tr/Basvuru/` | 200 | 52804 | TEMİZ | Aynı sahte 404 |
| `dmo.gov.tr/SM/` | 200 | 42277 | `login` | Giriş duvarı |
| `dmo.gov.tr/eSatis/FaturaIslemleri` | 404 | 0 | — | Yol yok |
| `resmigazete.gov.tr/ihale/` | 500 | 0 | — | Sunucu hatası |
| `resmigazete.gov.tr/mevzuat/` | 500 | 0 | — | Sunucu hatası |
| `resmigazete.gov.tr/eskiler/2026-10-03.htm` | 404 | 0 | — | Tarihli dosya yolu şema dışı |
| `kap.org.tr/tr` | 200 | 163124 | TEMİZ | **Paket kodu yok** (`PAKET_KAYNAKLARI` 8 kod: dmo, rg, google_news, linkedin, patent, instagram, facebook, is_ilani) |
| `kap.org.tr/tr/pazarlar` · `/tr/sirketler` · `/tr/bildirim/` | 404 | 0 | — | Yol yok |
| `tobb.org.tr/` · `/tr/basin-odasi` | URLError | 0 | — | DNS/TLS + **paket kodu yok** |
| `ticaret.gov.tr/tr/` | 200 | 5839 | TEMİZ | Gövde `Internal Server Error 404` + paket kodu yok |
| `ihale.gov.tr/` | 200 | 57324 | `bot` | "Tarayıcı sürümü desteklenmiyor" bot duvarı |
| `ilan.gov.tr` | URLError | 0 | — | Erişilemedi |
| `ispisi.com` | URLError | 0 | — | Erişilemedi |
| `kariyer.net/is-ilanari` | 404 | 0 | — | Yol yok |
| `spk.gov.tr` | 200 | 35096 | TEMİZ | İçerik temiz ama **paket kodu yok** |
| `mevzuat.gov.tr` | 200 | 549140 | `giriş yap` | Giriş duvarı + paket kodu yok |
| `google_news` `?q=şirket` RSS | 200 | 139121 | `bot` | Alt bilgi satırında bot üstbilgisi; içerik gerçek ama genel başlık akışı, firma hedefli değil |
| `yenibiris.com` | 403 | 0 | — | Erişim reddi |
| `iskur.com.tr` | URLError | 0 | — | Erişilemedi |
| `ekapv2.kik.gov.tr` | — | — | — | **Kapsam dışı** (Cloudflare, `BORC-EKAP-CLOUDFLARE-01`) |

## Köprü: etiket → paket kodu

`KAYNAK_HARITASI` anahtarları **insan dili** etikettir (model promptunda görünür);
`KAYNAK_PAKET_ADI` aynı anahtarları **makine dili** paket koduyla eşler
(`paketler.PAKET_KAYNAKLARI`). İki alan ayrı eksenlerdir — ikiz yapı değil:

- etiket → *hangi sayfa* (prompt davranışı)
- kod → *hangi pakette açık* (kota kararı, `firma_haber_kaynaklari()`)

İkinci bir kaynak listesi **açılmadı**; ikinci kaynak listesi açmak D-211 (ikiz yapı)
ihlali olurdu. Kalan 3 paket kodu (`linkedin`, `instagram`, `facebook`) ölçülebilir
bir adres vermediği için köprüde **yoktur** — uydurulmadı.

## Ölçüm Betikleri

`scripts/_haber_kusu_olcum.py` (1. tur) · `_olcum2.py` (2. tur, içerik sinyali eklendi)
· `_olcum3.py` (3. tur, 6. adres arayışı). Üçü de geçici betiktir, görev sonunda silinir.

## Sonuç

`KAYNAK_HARITASI` 3 → **7 adres**; hepsi 200 + gerçek içerik satırıyla kanıtlı.
Kabul kriteri (≥ 6 adres, hepsi ölçüm dokümanında 200) **karşılandı**.

## İlgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/docs/PAKET_KOTA_TASARIMI]]
- [[Huginn Data Insights/docs/SAGLAYICI_OLCUMU_2026-10-03]]
- [[Huginn Data Insights/docs/BORC_DEFTERI]]
- [[Huginn Data Insights/src/company_master/odin_ai/arac_dongusu]]
- [[Huginn Data Insights/src/company_master/paketler]]