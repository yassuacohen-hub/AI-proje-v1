# VERI-WEB-SITESI-ZENGINLESTIR-01 — Brief (utku)

**Başlık:** `[VERI] website_domain zenginleştirme kaynağını yaz -> unvan arama + canlı HTTP doğrulama, 7343 boş alana gerçek site (4s)`
**Öneren:** utku (ölçüm) · **Açan:** ihsan (D-58 kapısı, 2026-10-03)
**Öncelik:** P2 · **Kilitli dosyalar:** `src/company_master/etl/web_sitesi_zenginlestir.py`,
`tests/test_web_sitesi_zenginlestir.py`
**Hub:** [[hubs/PLAN_STRATEGY_HUB]]
**Kaynak bulgu:** `data/orchestrator/VERI-OSTIM-HREF-FILTRE-01_rapor_2026-10-03_uretim.md` §10.1

> ✅ Görev panoda: `durum=plan`, 2026-10-04 00:50 (D-58 ihsan). Kilitler `file_locks.json`'da.
>
> **Güncelleme 2026-10-04 (ihsan):** Sızıntı **kapandı** — goc `0052_website_sablon_kisiti.sql`
> uygulandı. 2666 şablon satır `NULL`'a çekildi (yedek: `yedekler/companies_website_sablon_20261004_0122.jsonl`),
> `companies_website_sablon` trigger'ı yeni şablon yazımını DB'de keser. **Adım 3 utku'dan düştü.**

---

## Neden

`website_domain` alanı **dolu görünüyordu ama yarısı sahteydi**. Canlı Supabase
ölçümü (10123 firma), goc 0052 **öncesi → sonrası**:

| Durum | Önce | Sonra (2026-10-04) |
|---|---|---|
| Dolu — gerçek site olabilir | 2780 | 2780 |
| Dolu — **kaynak sızıntısı** (OSB portalı) | 2666 | **0** |
| Boş | 4677 | **7343** (%72,5) |

Sahtelerin dağılımı: `isim.org.tr` ×2142, `ostimistihdam.com` ×474,
`ostimonline.com` ×50 — kazıyıcının sayfa şablonundan kapattığı OSB portalı
(D-245). Hepsi `NULL` oldu; ham değer `source_records.raw_payload`'de duruyor.

Boş kalan 4677'nin sebebi ölçüldü: ASO/OSTİM/İvedik/Baskent üye listeleri
**web sitesi alanı yayınlamıyor**; alanı dolduran tek yol o sayfadaki link,
o da bize firma sitesi değil OSB'nin kendi sitesini veriyor.

## Doğrulanacak varsayım (D-66)

Varsayım sabitlendi; **yoksa dur, panoya sorun aç, uydurma.**

| # | Varsayım | Eşik |
|---|---|---|
| 1 | Kaynak olmadan alan **boş** kalır | Boş firma sayısı yalnız **doğrulanmış** yazımla düşer; başlangıç 7343 |
| 2 | Sahte domain yazılmaz | `SABLON_WEB` sayacı **0 kalır** — trigger keser, ama kodun da `yazma_kapisi.kabul()` çağırması gerekir (D-246 tek kapı) |
| 3 | Doğrulama gerçekten çalışır | Yazılan her domain için HTTP 200 **ve** içerik doğrulaması |
| 4 | Yanlış pozitif oranı ölçülür | Elle denetim tablosu ≥20 firma, raporda |
| 5 | Alan **açık kalır** | 2780 gerçek site silinmez; global kapatma **yapılmaz** |

## Adımlar

1. ~~Önce kanıt: kaynak kırılımı~~ **YAPILDI (ihsan, 2026-10-04):** tek yazma
   yolu `ostim_scraper` şablon linki; `NULL`'a çekildi. Ölçüm betiği:
   `scripts/website_sablon_yedek.py` (prova = 2666).
2. **Alan sözleşmesi** (`docs/VERI_KALITE_SOZLESMESI.md`): `website_domain`
   için "kabul edilmez" maddesi yazılı değil — **önce o madde yazılır**
   (D-246). Kanonik liste: `yazma_kapisi.SABLON_WEB`; **ikinci liste yazma** (D-211).
3. ~~Kaynak sızıntısını engelle~~ **YAPILDI:** goc 0052 trigger
   `companies_website_sablon`. utku dokunmaz; yeni şablon bulursa
   `SABLON_WEB`'e ekler → mandal `tests/test_website_sablon_kisiti.py`
   SQL deseni eşitliğini zorlar (yeni goc gerekir).
4. **Zenginleştirme yolu:** unvan → arama → aday domain → **canlı HTTP 200** →
   **içerik doğrulama** (firma adı geçiyor mu) → `kabul()` → kaydet.
   Doğrulamasız aday **yazılmaz**. Getirme için önce
   `scripts/kazima_jina_fallback.py` (9Router `/v1/web/fetch`, ucuz) — yeni
   HTTP istemcisi yazma.
5. **Siteye bakmışken al (ürün sahibi isteği):** doğrulanan sayfadan
   `primary_phone`, `primary_email`, `address` adaylarını da çıkar; **yalnız
   boş alana** yaz, dolu alana dokunma; her yazım `source_records`'a kaynak
   `web_sitesi` ile iz bırakır. NACE/sektör ipucu sadece `raw_payload`'a (puanlanmaz).
6. **Ağırlık kararı (KAHİN):** `website_domain` ağırlığı **0,3/10** olarak
   kalacaksa dokunulmaz. Değiştirilecekse ölçüm aşağıda.

## Kabul kriteri

- Sahte domain sayacı **0 kalır** (ölçüm sonrası tablo raporda).
- Her yazım `yazma_kapisi.kabul()`'dan geçer; `kabul` red sebepleri raporda sayılır.
- Yazılan her domain için HTTP 200 + içerik doğrulaması kanıtı.
- Siteden alınan telefon/e-posta/adres: kaç alan doldu, ≥10 elle denetim.
- Elle denetim tablosu ≥20 firma: gerçek / yanlış / belirsiz.
- `ostim_scraper.py` ve diğer OSB kazıyıcıları **dokunulmaz** (D-290 kaynak kilidi).
- pytest yeşil; kodlama denetimi temiz.

## Puan etkisi — beklenti yönetimi (ölçüldü)

Bu görevin **skor motoruna etkisi küçüktür.** Ağırlık **0,3 / 10 puan** =
toplam puanın **%3'ü**.

| Senaryo | Ortalama `identity_completeness` |
|---|---|
| 0052 öncesi (sahteler dahil) | 3,71 |
| **Şimdi** — sahteler temizlendi | **3,63** (düştü — haksız puan gitti) |
| Boş 7343'ün tamamı site bulur | ~3,85 |

**Tam kapsama = +0,14 puan (+%3,8).** Karşılaştırma:

| Alan | Ağırlık | Kaybedilen puan |
|---|---|---|
| tax_number (VKN) | 1,5 | **15 177** |
| address | 1,5 | 5 424 |
| primary_email | 0,7 | 3 770 |
| website_domain | 0,3 | max 3 037 |

**Bu yüzden görev P2'dir.** VKN kaynağı (GIB-MUKELLEF-01) bir gün açılırsa
+1,5 puan (%40) — web sitesi tamamen çözülse +%3,8.

## Ajan chat zorunlu (D-210 · D-217)

Varsayım tutmuyorsa / faz tıkandıysa sorun aç, uydurma, durma:

```bash
python scripts/ajan_chat.py ac ihsan VERI-WEB-SITESI-ZENGINLESTIR-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-WEB-SITESI-ZENGINLESTIR-01
```

## Teslim

Rapor + B-14 hub izi + `gorev_kutusu.py teslim` → ardından
`python scripts/gorev_kutusu.py nobet --ajan utku`.

## Ilgili Nodlar

- [[src/company_master/schema/migrations/0052_website_sablon_kisiti.sql]] (sızıntı kapısı, uygulandı)
- [[src/company_master/schema/migrations/down/0052_website_sablon_kisiti.down.sql]]
- [[tests/test_website_sablon_kisiti.py]] (mandal: SQL deseni == `SABLON_WEB_DESEN`)
- [[src/company_master/db/yazma_kapisi.py]] (`SABLON_WEB`, `kabul()`)
- [[scripts/website_sablon_yedek.py]] (yedek + prova)
- [[scripts/kazima_jina_fallback.py]] (ucuz sayfa getirme)
- [[data/orchestrator/VERI-OSTIM-HREF-FILTRE-01_rapor_2026-10-03_uretim]]
- [[plans/brief_utku_VERI-OSTIM-HREF-FILTRE-01]]
- [[hubs/PLAN_STRATEGY_HUB]]
- [[docs/VERI_KALITE_SOZLESMESI]] (alan sözleşmesi)
- [[docs/BORC_DEFTERI]] (D-245, D-246)