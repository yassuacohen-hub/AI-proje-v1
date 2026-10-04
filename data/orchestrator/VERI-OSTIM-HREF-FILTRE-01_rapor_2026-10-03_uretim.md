# VERI-OSTIM-HREF-FILTRE-01 — Rapor

- **Ajan:** UTKU · **Tarih:** 2026-10-03 · **Durum:** `review`
- **Kilitli dosyalar:** `src/company_master/etl/scrapers/ostim_detail_scraper.py`, `tests/test_ostim_detail_scraper.py`
- **Brief:** `plans/brief_utku_VERI-OSTIM-HREF-FILTRE-01.md`
- **Kalıcı araçlar:** `scripts/ostim_href_olc.py` · `scripts/ostim_pilot_firma_sec.py` · `scripts/ostim_pilot_denetim.py` · `scripts/ostim_websitesi_temizle.py`

## 1. Sonuç (tek cümle)

`web_sitesi` alanı OSTİM kaynağında **%100 sızıntıdır** — 1555 dolu kaydın 1555'i OSB portal adresidir, gerçek firma sitesi **0**; filtre düzeltildi, ama **asıl bulgu ölçüm aracındaki hataydı**: kendi kuralını taşıyan ölçüm betiği 140 gösterirken gerçek tablo 1555'ti.

**Karar (§10, ölçüm dayalı):** alan **açık kalır**, OSB portal domain'i bu
kaynak için **kaynak bazlı** yazılmaz; gerçek web adresleri ayrı görevle
(`VERI-WEB-SITESI-ZENGINLESTIR-01`) unvan → arama → canlı HTTP 200 + içerik
doğrulama yoluyla zenginleştirilir. Görevin puan etkisi ölçüldü: **+0,3 / 10
puan (tam kapsamada %3,8)** → öncelik **P2**.

## 2. Varsayım kırıldı (D-217) — iki kez

### 2.1 Brief varsayımı: "kaç kayıt sosyal/harita/mailto içeriyor?"

Brief'in regex'iyle **140 (%9,0)**. Bu **yanlış güven** verdi (D-245: doluluk ≠ geçerlilik).

| tekrar | adres | ne |
|---:|---|---|
| 1415 | `https://nsosyal.com/ostim_osb` | OSTİM OSB'nin kendi sosyal sayfası |
| 140 | `https://www.ostimonline.com/Home/OstimMain` | OSTİM portal ana sayfası |
| **1555** | toplam | **gerçek yanlış-pozitif = %100** |

Açıklama: brief regex'inde `nsosyal.com` **yoktu**. `ostimonline` 140'ı yakaladı, `nsosyal` 1415'i kaçırdı. Gerçek tablo 1555/1555.

### 2.2 Kendi ölçüm betiğim de kırıktı (asıl bulgu)

İlk ölçüm betiği üreticiden **ayrı** bir `KOTU_DESEN` regex'i taşıyordu — yani **ikiz yapı** (D-211) ve kendi hatasını gizliyordu:

```
--detay 10, ilk hali : YANLIS-POZITIF 140 (%9.0)   <- YANLIŞ
uretici kuralıyla    : YANLIS-POZITIF 1555 (%100.0) <- DOĞRU
```

Bu, D-309/1'in ("aracın yeşil demesi kanıt değil") taze örneği: ölçüm aracı, ölçtüğü şeyin kuralını **kendi kopyasından** okuyunca kendi kör noktasını üretmez, **gizler**.

**Düzeltme (D-211 / D-266):** betik artık üreticinin kendi kuralını ithal ediyor — `from ...ostim_detail_scraper import WEB_BLOCKLIST, _is_company_website`. İki kopya yok, sapma imkânsız. Mandal: `tests/test_ostim_detail_scraper.py::TestOlcumTekKaynak` (betik `KOTU_DESEN` tanımlayamaz + iki sızıntı adresinin ikisini de reddedeceğini ölçer).

### 2.3 Pilot seçimi de hatalıydı (KAHİN: "firma türü anonim şirket A.Ş. olsun")

İlk seçim tek seferlik `python -c` ile, ASCII regex'le yapılmıştı. Ölçülen mekanizma:

| ölçüm | sonuç |
|---|---:|
| eski regex `A\.\s*S\.\|ANONIM\|SIRKETI` + `re.I` | **385** |
| Unicode normalize + `A.Ş.` / `ANONİM ŞİRKETİ` | **991** |

Kök neden: Python `re.IGNORECASE` **U+0130 (İ) ile ASCII "I"yı eşler**, ama **U+015E (Ş) ile ASCII "S"yi eşlemez** (ölçüldü: `re.search('SIRKETI','ŞİRKETİ',re.I)` → False). Yani "A.Ş." yazımı görünmezdi:

- `A\.\s*S\.` dali → ASCII "A.S." 88 kayıt
- `ANONIM` dali → "ANONİM ŞİRKETİ" 296 kayıt (İ eşleştiği için)
- **Görülmeyen**: "A.Ş." (cedillalı Ş) yazılı **607 kayıt** → toplam 606 A.Ş. firma elendi.

Düzeltme: `scripts/ostim_pilot_firma_sec.py` — `unicodedata.normalize` tabanlı, `Şube` kayıtlarını eleyen, sektör puanlayan kalıcı seçim aracı. Ölçüm: **8313 kayıt → 969 A.Ş. uygun → 60 sektör odaklı → 100 seçildi**.

## 3. Neden sızdı — canlı sayfa ölçümü (10/10)

`data/_tmp/ostim_pilot_10_denetim.md` — 10 A.Ş. sayfası canlı açıldı:

| ölçüt | sonuç |
|---|---:|
| HTTP 200 | **10/10** |
| `Web Sitesi` etiketi tasiyan sayfa | **0/10** |
| sayfa başına dış adres | **33–34** (toplam 334) |
| yeni `web_sitesi` dolu | **0** |

Sayfadaki tüm bağlantılar OSB portalının kendi ayakları: `isim.org.tr`, `ostimradyo.com`, `ostimsavunma.org`, `ostimvakfi.org`, `ostimyatirim.com.tr`, `htk.org.tr`, `odtuteknokent.com.tr`, `kaucukteknolojileri.com`, `nsosyal.com/ostim_osb`, `wa.me/905304828110`, `facebook.com/OstimOSB`, `linkedin.com/company/ostim-osb`.

Dış kontrol: `https://nsosyal.com/ostim_osb` → **403 "Just a moment..."** (Cloudflare); `ostimonline.com/Home/OstimMain` portal ana sayfası.

**Sonuç: OSTİM detay sayfalarında firma web sitesi alanı hiç yok.** Bu alan bu kaynaktan üretilemez.

## 4. Ölçüm öncesi / sonrası

| Ölçüt | Önce (9051 satır) | Sonra (pilot 100 A.Ş.) |
|---|---:|---:|
| `web_sitesi` dolu | 1555 | **0** |
| Yanlış-pozitif | **1555 (%100)** | **0 (%0)** |
| Gerçek firma sitesi | **0** | 0 (kaynakta yok) |
| Bloklist girdisi | 9 | **36** |

> Doluluk %17,2 → %0. Bu bir **kayıp değil, gerçeğin ortaya çıkması**.

## 5. Pilot satır denetimi (D-292) — 10/10 canlı

Kaynak: `data/_tmp/ostim_pilot_10_denetim.md` · üreten: `scripts/ostim_pilot_denetim.py`

| # | Firma (A.Ş.) | slug | HTTP | dış adres | etiket | gerçek site (E/H) |
|---|---|---|---:|---:|---|---|
| 1 | 3En Mekanik Savunma Ve Havacılık Sistemleri | `3en-mekanik-savunma-ve-havacilik-sistemleri-as` | 200 | 33 | yok | **H** |
| 2 | AATG Savunma Havacılık ve Uzay Teknolojileri | `aatg-savunma-havacil` | 200 | 33 | yok | **H** |
| 3 | Aril Havacılık Savunma | `aril-havacilik-savunma-as` | 200 | 34 | yok | **H** |
| 4 | Aryasis Makina Savunma ve Havacılık | `aryasis-makina-savunma-ve-havacilik-as` | 200 | 34 | yok | **H** |
| 5 | ASECRON Savunma ve Havacılık | `asecron-savunma-ve-h` | 200 | 33 | yok | **H** |
| 6 | DT Savunma ve Havacılık | `dt-savunma-ve-havacilik-as` | 200 | 34 | yok | **H** |
| 7 | Epsilon Havacılık Uzay ve Savunma | `epsilon-havacilik-uzay-ve-savunma-san-tic-as` | 200 | 34 | yok | **H** |
| 8 | MRT Savunma ve Havacılık | `mrt-savunma-ve-havacilik-san-tic-as` | 200 | 33 | yok | **H** |
| 9 | Smart Aerospace Solutions | `smart-aerospace-solu` | 200 | 33 | yok | **H** |
| 10 | Taelco Havacılık ve Savunma | `taelco-havacilik-ve` | 200 | 33 | yok | **H** |

**10/10 elinde doğrulandı: gerçek firma sitesi yok.**

## 6. Yapılan değişiklikler

| Değişiklik | Gerekçe |
|---|---|
| `WEB_BLOCKLIST` 9 → **36** girdi | Canlı sayfa taramasıyla ölçülen 10 portal alan adı + sosyal + harita + `mailto:`/`tel:`/`javascript:`/`sms:` |
| `startswith("http")` → `IZINLI_SEMALAR = ("http://", "https://")` | `httpfoo://` kabul ediliyordu |
| `/index.html`, `/home` reddi korundu, **`/` reddi kaldırıldı** | `https://firma.com.tr/` firma sitesinin kendisidir; portal kökü zaten blokliste |
| `_etiketten_site()` eklendi, "ilk http adresi" kuralı **kaldırıldı** | Sayfa şablonu sızıntısının kökü; etiket yoksa **boş kalır, tahmin edilmez** |
| `run_scraper(cikti=…, girdi=…)` | Pilot izole çalışsın, kanonik çıktı kirlenmesin (D-241/D-243) |
| `ostim_href_olc.py` → **üretici kuralını ithal eder** | Kendi regex'ini taşıyordu; 140 yerine gerçeği (1555) göstermesi gerekiyordu (D-211/D-266) |
| `ostim_pilot_firma_sec.py` **yeni** | Unicode normalize + şube elemesi; eski seçim 606 A.Ş. firmayı elemişti |
| `ostim_pilot_denetim.py` **yeni** | D-292 tablosu elle yazılmak yerine canlı sayfadan ölçülür |
| `ostim_scraper.py` (liste kazıyıcı) | **Dokunulmadı** (D-290 kaynak kilidi) |

## 7. Test

```
python -m pytest tests/test_ostim_detail_scraper.py -q   -> 24 passed
python -X utf8 scripts/kodlama_denetim.py                -> 4 dosyam temiz
```

- 4 doğru + 4 yanlış href (brief'in istediği 8 örnek) + şema/kancalama + etiket-ankrajı testleri
- Ölçüm tek-kaynak testleri (2) + pilot seçimi testleri (4)
- **Kırma denemesi (D-256/4):** `nsosyal.com` bloklistten çıkarıldı → **4 kırmızı**, geri alındı → 24 yeşil. Mandal gerçekten kırılıyor.

## 8. Diskteki 1555 bozuk satır — KAHİN kararı: **DOKUNULMADI**

KAHİN talebi: *"Sadece raporla, dokunma."*

Bu bir açık kapıdır: `run_scraper()` slug'ı `completed_slugs` içinde gördüğü için bozuk satırları **asla** yeniden çekmez. Filtre düzeltmesi tek başına diskteki değerleri düzeltmez.

Hazır, çalıştırılmamış araç: `scripts/ostim_websitesi_temizle.py`
- varsayılan **prova** (dosyaya yazmaz): `1555 silinecek, 0 kalacak gerçek`
- `--yaz`: `yedekler/ostim_firmalar_detailed_<tarih>.jsonl` yedeği alır, 1555 satırı boşa çeker, sonra yeniden ölçer; yedek satır sayısı eşleşmezse iptal eder (D-244)

## 9. Öz-eleştiri

| Eksik bıraktığım / yanlış yaptığım | Neden |
|---|---|
| **Ölçüm betiğim kendi kuralını taşıyordu** (asıl hata) | D-211 ikiz yasağını bilerek değil, reflekse uydum; regex'i hızlıca genişletmeye çalıştım. Ölçüm aracı üreticiden **ithal etmeliydi** |
| İlk raporu "ölçüm kendisi yanlış soruyordu" diye yazdım, ama ölçümün kendi hatasını gizlediğini fark etmedim | 140 rakamına güvendim, üretici kuralıyla karşılaştırmadım. D-224: iddia değil ölçüm |
| Pilot seçimini `python -c` tek seferlik yaptım | 606 A.Ş. firma sessizce elendi. D-86 zaten tek satır `python -c`'yi yasaklıyor — kuralı bilmemek yerine ölçüm de yaptırmadım |
| Kırma testinin **ilk örneğini yanlış yazdım** | "re.I İ'yi eşlemez" dedim; ölçtüm, eşlediğini gördüm (`İ`→`I` eşleşiyor, `Ş`→`S` eşleşmiyor). Varsayımı ölçümle düzelttim |
| Bloklist sayısını raporda "9 → 30" yazmışım | Gerçek 36. Sayıyı ölçmedim, tahmin ettim — D-309/1 |

## 10. Öneri ve karar (KAHİN kararı)

**Karar (KAHİN, 2026-10-03):** Ölçüm dayalı 3. seçenek benimsenmiştir —
**kaynak bazlı kapatma + alan açık + ayrı zenginleştirme görevi (P2).**
Ölçüm yapılmadan karar verilmedi; aşağıdaki tablo kararın dayanağıdır.

### 10.1 Ölçüm (canlı Supabase / aws-0-eu-west-2.pooler, 10123 firma)

| Durum | Firma | % |
|---|---:|---:|
| Dolu — gerçek site olabilir | 2780 | %27,5 |
| Dolu — **kaynak sızıntısı** (OSB portalı) | **2666** | **%26,3** |
| Boş | 4677 | %46,2 |

Sızıntı dağılımı: `isim.org.tr` ×2142 · `ostimistihdam.com` ×474 ·
`ostimonline.com` ×50. Boş kalanların sebebi ölçüldü: ASO/OSTİM/İvedik/
Baskent üye listeleri **web sitesi alanı yayınlamıyor**; alanı dolduran tek
yol o sayfadaki link, o da OSB'nin kendi portalı.

### 10.2 Neden (a) değil — alan bu kaynak için kapanmaz

Alan global kapanırsa **2780 gerçek site de kaybolur**. Kaynak bazlı
kapatma seçildi: yalnız OSB/oda kaynaklarının portal domain'i
`website_domain`'e **yazılmaz**, ham değer `source_records.raw_payload`
içinde kalır (D-246/4: kaynağı olan değer silinmez).

### 10.3 Neden (b) tek başına değil

Ayrı kaynak açılması tek başına hiçbir şey yapmaz; (a) ve (b) birlikte
uygulanır.

### 10.4 Puan etkisi — beklenti yönetimi (ölçüldü)

| Alan | Ağırlık | Kaybedilen puan |
|---|---:|---:|
| `tax_number` | 1,5 | **15177** |
| `address` | 1,5 | 5424 |
| `primary_email` | 0,7 | 3770 |
| `website_domain` | **0,3** | max 3037 |

`website_domain` ağırlığı **0,3 / 10 puan** = toplam puanın **%3'ü**.
Tam kapsama ortalama puanı **3,71 → ~3,85 (+%3,8)** çıkarır. Bu yüzden
görev **P2**'dir: VKN kaynağı (`GIB-MUKELLEF-01`) bir gün açılırsa +1,5
puan (**+%40**).

Önemli yan ölçüm: sahteleri temizlemek ortalamayı **düşürür** (3,71 → 3,63),
çünkü 2666 firma haksız 0,3 puan alıyor. Bu D-245'un düzeltilmesidir,
kayıp değildir.

### 10.5 Açılan görev

`VERI-WEB-SITESI-ZENGINLESTIR-01` — "unvan → arama → canlı HTTP 200 +
içerik doğrulama → kaydet". Brif: `plans/brief_utku_VERI-WEB-SITESI-ZENGINLESTIR-01.md`
(D-66 ölçülebilir kabul kriterleri + 5 sabit varsayım).

**D-58 nedeniyle utku görevi açamadı** (`aktif: ihsan, cagiran: utku` ile
reddedildi); komut kopyala-yapıştır olarak `ajan_chat.py` ile ihsan'a iletildi.

### 10.6 Diğer maddeler

- **Aynı desen tüm OSB kazıyıcılarında aranmalı:** "ilk `http` adresi" kuralı her yerde aynı sızıntıyı üretir.
- **Ölçüm araçları kural taşımamalı** — üreticiden ithal etmeli (D-211/D-266). Bu, `scripts/` altındaki diğer olçüm betikleri için de geçerli.

## İlgili Nodlar
- [[plans/brief_utku_VERI-OSTIM-HREF-FILTRE-01]]
- [[plans/brief_utku_VERI-WEB-SITESI-ZENGINLESTIR-01]]
- [[hubs/PLAN_STRATEGY_HUB]]
- [[docs/BORC_DEFTERI]] (D-292, D-245)
- [[src/company_master/etl/scrapers/ostim_detail_scraper]]
- [[tests/test_ostim_detail_scraper]]
- [[scripts/ostim_href_olc]] · [[scripts/ostim_pilot_firma_sec]] · [[scripts/ostim_pilot_denetim]] · [[scripts/ostim_websitesi_temizle]]