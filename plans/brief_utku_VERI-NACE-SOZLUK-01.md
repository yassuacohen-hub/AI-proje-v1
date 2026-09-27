# Brif — VERI-NACE-SOZLUK-01: Resmi NACE listesini yaz → nace_codes tablosu

**Sahip:** utku · **Öncelik:** P0 · **Süre:** 3s · **Veren:** ihsan (orkestratör)
**Tarih:** 2026-09-27 · **Ölçüm yeri:** CANLI Supabase (`aws-0-eu-west-2.pooler.supabase.com:6543`)

---

## 1. Neden P0 — ölçülen durum

`nace_codes` sözlük tablosu **0 satır**. Buna karşılık `companies.nace_code`
**8900 satırda dolu**. Yani firmalara atanmış hiçbir NACE kodu bir referans
listeyle doğrulanamıyor. Eşleştirme referanssız yapılmış.

Sonuç — kodlar yanlış. Kanıt (canlı sorgu, ünvanla karşılaştırma):

| Kod | Atanan firma | Gerçek anlamı | Örnek atanmış ünvanlar |
|-----|--------------|---------------|------------------------|
| `10.11` | 911 | Etlerin işlenmesi | 3E ELEKTRO OPTİK SİSTEMLER, A ARTI ULUSLARARASI ÇEVİRİ HİZM., ACAR FAKTORİNG A.Ş. |
| `01.13` | 178 | Sebze yetiştirme | ADA KONKASÖR MAK., AKKOR ISIL İŞLEM ÇELİK, ALEMDARLAR İNŞ. |
| `29.10` | 1882 | Motorlu taşıt imalatı | AA RAS SİGORTA ARACILIK, 3S DEMIR ÇELIK, 312 PROJE TASARIM |
| `62.01` | 634 | Bilgisayar programlama | 06 SIHHAT İŞ GÜVENLİĞİ OSGB, 3E YALITIM HIRDAVAT |

Bunlar tek tek hata değil; **dağılımın tamamı güvenilmez**.

Ek kirlenme: `nace_code` içinde NACE olmayan değerler var —
`'1163'` (168 firma), `'794'` (54), `'757'` (53), `'780'` (62), `'410'` (68).
Bunlar OSTİM sektör sayfalarındaki **sektör sayaçları**, NACE kodu değil.
Tamamı `nace_source='unknown'` (2433 satır).

Köken dağılımı (canlı):

| nace_source | Firma | Yorum |
|-------------|-------|-------|
| `unknown` | 7622 | kökeni bilinmiyor; 2433'ünde yine de kod atanmış |
| `sector_default` | 5705 | sektör varsayılanı — firmaya özel değil |
| `fallback` | 655 | çaresizlik değeri |
| `title_default` | 21 | ünvandan tahmin |

**Gerçek NACE ataması olan firma sayısı: 0.** 8900'ün tamamı ya varsayılan,
ya fallback, ya kökeni bilinmeyen.

İyi haber: `source_records.raw_nace` **7595 satırda dolu** — kaynaktan gelen
NACE değerleri duruyor, kaybedilmemiş. Ham veri elde.

## 2. Ürün sahibi kararı

> "NACE kodları devlet tarafından zamanla güncelleniyor, resmi güncel NACE kodu
> listesinin sürekli sistemde durması gerekir, ana veri kaynaklarından bir
> tanesidir, eşleştirme için lazım."

## 3. Kaynak — erişim ölçüldü (HTTP 200)

Sayfa: `https://ticaret.gov.tr/esnaf-sanatkarlar/esnaf-ve-sanatkar-meslek-kollari/sektor-meslek-nace-listeleri/guncel-liste`

İndirilebilir dosya (HEAD ile doğrulandı, indirilmedi):

| Durum | Boyut | Dosya |
|-------|-------|-------|
| 200 | 0.13 MB | **`SektörMeslekNace_2026.01.01 güncel Mayıs 2026.xlsx`** ← hedef |
| 200 | 3.58 MB | Ekonomik Görünüm 2026 Ağustos.pdf (ilgisiz) |
| 200 | 0.41 MB | Çerez Politikası.pdf (ilgisiz) |

Dosya adında sürüm bilgisi var (`2026.01.01`, `Mayıs 2026`) — güncelleme
takibi için kullanılabilir.

**Dosya indirildi ve yerine kondu:**
`data/nace/sektor_meslek_nace_2026-05_resmi.xlsx` (131 KB)

## 3.1 İçeriği ölçüldü — beklenenden değerli

Ürün sahibi: *"hangi NACE neler yapabilir, hangi işleri yapabilir kısmını
gösteriyor, değerli veri."* Ölçüm bunu doğruladı.

1 sayfa, **1531 satır**, 6 kolon — düz bir eşleme tablosu:

| # | Kolon | Örnek |
|---|-------|-------|
| 0 | SEKTOR KODU | `D` |
| 1 | SEKTOR TANIM | `AĞAÇ İŞLERİ` |
| 2 | MESLEK KODU | `A.01` |
| 3 | MESLEK TANIM | `İkinci el eşya ticareti` |
| 4 | NACE REV. 2.1 KODU | `47.79.04` |
| 5 | NACE REV.2.1 TANIM | `Kullanılmış mobilya, elektrikli ev eşyası...` |

Bu sadece kod sözlüğü değil — **sektör → meslek → NACE üçlü köprüsü**. Yani:

- "Ağaç işleri sektöründe hangi NACE kodları var?" → cevaplanabilir
- "47.79.04 kodlu firma ne iş yapar?" → resmi tanım geliyor
- OSTİM sektör adlarımızı resmi sektör tanımlarına bağlama imkânı doğuyor

Essiz NACE kodu: **1531**. Essiz uzun faaliyet tanımı: **1681** — tanımlar
gerçekten ayrıntılı (örn. *"Adi metalden dişli kapaklar (şişe kapağı vb.) ve
tıpalar ile tıkaçlar ve kapakların imalatı"*).

### 🔒 D-234 — KURAL (ürün sahibi onayladı, ölçümle sabit)

İki madde de **bağlayıcı**. Mandal: `tests/test_nace_referans_kurali.py` (6 test yeşil).

**1. Seviye korunur, kısaltılmaz.** 6 hane (`47.79.04`) **asıl** olarak yazılır
(`level=6`); 4 hane (`47.79`, `level=4`) ve 2 hane (`47`, `level=2`) ondan
**türetilip ayrıca** yazılır. "6 varken 4 yazmak yanlış" itirazı haklı — bu
yüzden 4 hane asılın *yerine* değil, *yanına* gider. Hiçbir seviye silinmez.

Neden (canlı ölçüm, 8900 firma / 464 eşsiz kod):

| Canlı `nace_code` şekli | Firma | % |
|---|---|---|
| 4 hane (`NN.NN`) | 7642 | 85.9 |
| 6 hane (`NN.NN.NN`) | 678 | 7.6 |
| noktasız sayı (çöp) | 555 | 6.2 |
| 2 hane | 25 | 0.3 |

Resmi xlsx ise **tamamen 6 haneli**. Türetme yapılmazsa %85.9 hiç eşleşmez.
Ölçülen: **sadece türetme sayesinde eşleşen 3595 firma (%40.4)**.

**2. Referans birleşiktir — dört kaynak, biri diğerinin yerine geçmez.**

`data/nace/` altındaki **dördü birden** okunur:

| Kaynak | İçerik | Ölçülen |
|---|---|---|
| `sektor_meslek_nace_*_resmi.xlsx` | esnaf/sanatkâr meslek kolları | 1531 × 6 hane |
| `turkiye_nace.json` | TR NACE, `code_6digit` + `code` yan yana | 2142 kayıt |
| `nace-rev-2-1.json` | AB Rev 2.1 | 1047 kayıt / 738 kod |
| `nace-rev-2.json` | AB Rev 2 | 996 kayıt / 703 kod |

Kapsam kanıtı:

| Referans | Eşleşen firma | % |
|---|---|---|
| yalnız xlsx (+türetme) | 4242 | **47.7** |
| **dört kaynak (+türetme)** | 8271 | **92.9** |

Tek kaynakla eşleşmeyenler çöp değil, gerçek NACE'ler: `29.10` (1882 firma),
`62.09` (655), `62.01` (634), `41.10` (600) — xlsx'te yok, json'larda var.
"Yeni liste geldi, eskiyi silelim" **%45 kapsam kaybı** demek. Yasak.

Not: `turkiye_nace.json` zaten `code_6digit` + `code` ikilisini birlikte
taşıyor — istenen yapı elimizde var, sıfırdan kurmayın, örnek alın.

## 4. Yapılacak

Yeni dosya: `src/company_master/etl/nace_sozluk_yukle.py`

**Dört kaynak da yerelde** — indirme kodu yazmadan işe başlayın (D-234 madde 2).

1. **Dördünü de oku** (`openpyxl` kurulu, ölçtüm — ek paket gerekmez):
   - `sektor_meslek_nace_2026-05_resmi.xlsx` → sektör/meslek köprüsü **buradan**
   - `turkiye_nace.json` → `code_6digit` + `code` (istenen yapının örneği)
   - `nace-rev-2-1.json`, `nace-rev-2.json` → AB gövdesi, xlsx'in kapsamadığı
     `29.10`/`62.01`/`41.10` gibi kodlar buradan geliyor
2. `nace_codes` tablosuna **upsert**. Kolonlar:
   `nace_code, version, level, parent_code, title, sector_group, is_manufacturing`
   - 6 haneli satır: `nace_code='47.79.04'`, `level=6`, `title` ← resmi tanım,
     `sector_group` ← `AĞAÇ İŞLERİ`, `parent_code='47.79'`
   - 4 haneli satır **ayrıca**: `nace_code='47.79'`, `level=4`, `parent_code='47'`
   - 2 haneli satır **ayrıca**: `level=2`
   - **Hiçbiri diğerinin yerine yazılmaz** (D-234 madde 1). Aynı kod iki
     kaynaktan gelirse `version` ile ayrışsın, üzerine yazıp kaybetmeyin.
3. Sektör↔meslek↔NACE üçlüsünü kaybetmeyin. `nace_codes` bunu taşımıyorsa
   yanına düz bir eşleme tablosu gerekir — **önce mevcut şemayı okuyun**, yeni
   tablo açmadan `nace_to_ostim_sektor.json` (zaten var) ile kıyaslayın.
4. `sources` tablosuna **kaynak başına** kayıt: `ticaret.gov.tr` (tip `official`,
   sürüm `2026.01.01 / Mayıs 2026`) + üç json. Hangi kodun nereden geldiği
   kaybolmasın.
5. **Sonraki sürümler için** indirme desteği ikinci adım: sayfadan `.xlsx`
   linkini desenden bulun (dosya adı her güncellemede değişiyor, URL gömmeyin).
   Bugünün işi değil — dosya elimizde.

## 5. Kabul ölçütü (test)

- `select count(*) from nace_codes` > 0; üç seviye de dolu:
  `select level, count(*) from nace_codes group by level` → 6, 4, 2 satırları var
- `47.79.04` (`level=6`) `title`'ı dönüyor ve "kullanılmış" içeriyor
- `47.79` (`level=4`) **ayrı satır** olarak var — türetme çalıştı, asıl silinmedi
- Yalnız xlsx'te olmayan `29.10`, `62.01`, `41.10` **tabloda** — birleştirme
  çalıştı (yoksa 3116 firma referanssız kalır)
- İkinci kez çalıştırma satır sayısını **ikiye katlamıyor** (upsert çalışıyor)
- `companies.nace_code` eşleşme oranı raporlanır. **Ölçülmüş hedef: %92.9**
  (8271/8900). Bunun altı kalırsa bir kaynak atlanmış demektir.

## 6. Bu görev neyin önkoşulu

Bu tablo dolmadan şu üç iş yapılamaz — hepsi referans listeye bağlı:

- `VERI-NACE-COKLU-01` — çoklu NACE (`company_industries`, şu an 0 satır).
  Ürün sahibi: *"bir işletmenin birden fazla NACE kodu olabilir, bu kanuni bir
  durum; ana NACE kodu esas alınarak varsa ek NACE kodları da toplanabilir ve
  tabloda belirtilir."* Şema bunu zaten destekliyor: `is_primary` kolonu var.
- `VERI-NACE-TEMIZ-01` — sektör sayacı kirlenmesi (`'1163'`, `'794'` vb.).
  Referans liste olmadan "bu geçerli bir NACE mi" sorusu cevaplanamaz.
- `VERI-NACE-KOLON-01` — `nace_validity` kolonuna NACE kodu yazılmış (86 satır:
  `'41.00.02'`, `'35.12.00'`). Kolon karışması; `nace_validity` geçerlilik
  etiketi taşımalı (`unknown`/`medium`/`fallback`), kod taşımamalı.

## 7. Uyarı — yazma öncesi

Canlı DB'de 14003 firma var. Ölçümlerimin tamamı salt-okunur yapıldı.
Yazma adımında **önce yedek**, sonra sınırlı parti (örn. 100 satır) deneyin.

---

*ponytail: xlsx doğrudan indirme + upsert. Skipped: NACE sürüm geçmişi tablosu
(kod değişiklik izleme), eklenmesi gereken an — bir kod resmi listeden düşüp
elimizdeki firmada kalırsa.*
