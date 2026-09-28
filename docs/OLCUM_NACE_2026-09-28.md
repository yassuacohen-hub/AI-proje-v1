# NACE Anatomisi Ölçümü — 2026-09-28

**İş:** OLCUM-NACE-01 · **Tetikleyen:** ürün sahibi — "NACE kodu yanında açılımı olsun,
firma birden fazla kod alabilir" · **Yöntem:** canlı veritabanı, 9412 firma, 3319 sözlük kodu

---

## 0. Tek cümlelik sonuç

**NACE kodlarımızın %100'ü tahmindir. Tek bir firmanın bile resmî NACE kodu elimizde
yoktur.** Bu yüzden "bu firma şu işleri resmî olarak yapabilir" cümlesi bugün
kurulamaz — kurulursa yalan olur.

---

## 1. Ürün sahibinin cümlesi neden doğru bir gereksinim

> "x firmanın nace kodu ve yanında nace koduna bağlı işler — bu şu demek oluyor:
> bu firma bu işleri **resmî olarak yapabilir**. Fakat firma tek bir konuda
> uzmanlaşmış da olabilir."

Bu cümle üç ayrı kavramı doğru ayırıyor:

| Kavram | Anlamı | Kaynağı |
|---|---|---|
| **Yapabilir** (yetki) | Sicilde kayıtlı faaliyet konusu | MERSİS / Ticaret Sicil Gazetesi |
| **Yapıyor** (fiil) | Fiilen ürettiği/sattığı | Web sitesi, ihale, katalog, iş ilanı |
| **Uzman** (odak) | Asıl kazandığı iş | Çıkarım — yukarıdaki ikisinden |

Bunlar **aynı kolonda tutulamaz**. Bugün tek kolonda tutuluyor: `companies.nace_code`.

---

## 2. Ölçüm: kod nereden geliyor?

`companies.nace_code` dolu olan **8289** firma (%88). Kaynak dağılımı:

| `nace_source` | Firma | Ne demek |
|---|---:|---|
| `sector_default` | 5679 | **Tahmin** — kayıt hangi kaynaktan geldiyse o kaynağın varsayılanı |
| `unknown` | 1935 | **Bilinmiyor** — nereden geldiği bile kayıtlı değil |
| `fallback` | 654 | **Tahmin** — hiçbir şey tutmayınca atanan yedek |
| `title_default` | 21 | **Tahmin** — ünvandaki kelimeden çıkarım |
| **gerçek kaynak** | **0** | **MERSİS/TSG'den gelen kod sayısı: SIFIR** |

`nace_validity` de aynı hikâyeyi anlatıyor: `medium` (5711), `unknown` (2942),
`fallback` (738), `title_default` (21). **Hiçbiri `verified` değil.**

### 2.1 Somut zarar: 29.10 kodu

En sık kod **29.10**, tam **1880 firmaya** atanmış. Sözlükteki açılımı:

> *"Kamyonet, Kamyon, Yarı Römorklar İçin Çekiciler, Tankerler vb. Karayolu
> Taşıtlarının İmalatı"*

Ankara'da 1880 kamyon fabrikası yok. Bu, bir OSB kaynağının varsayılan kodunun
tüm firmalara kopyalanmasıdır — **D-245'in "tekrar eden değer = kaynak sızıntısı"
kalıbının en büyük örneği.**

Bugün paneldeki her sektör grafiği, her filtre, her sayım bu 1880 sahte kodu
gerçek sanıyor.

---

## 3. Ölçüm: açılım (title) kullanılabilir mi?

`nace_codes` tablosu — 3319 kod. Kodlama bozukluğu **yok** (0 mojibake). Ama:

| Seviye | Kod | Boş başlık | Oran |
|---|---:|---:|---:|
| level 1 (harf) | 22 | 0 | %0 |
| level 2 (2 hane) | 88 | 52 | **%59** |
| level 4 (XX.XX) | 957 | 483 | **%50** |
| level 6 (XX.XX.XX) | 2252 | 0 | **%0** |

**Biz level 4 kullanıyoruz** (tüm 8289 firma 5 haneli = `XX.XX`), ve level 4'ün
**yarısının başlığı boş**. Yani "kodun yanına açılımını yaz" dendiğinde
firmaların yarısında yazacak bir şey yok.

**Asıl değer level 6'da:** 2252 kodun tamamının Türkçe, ayrıntılı başlığı var.
Örnek — 29.10'un altındaki 7 alt kod:

- `29.10.01` Kamyonet, kamyon, çekici, tanker imalatı
- `29.10.02` Otomobil ve benzeri araçların imalatı
- `29.10.03` Motorlu kara taşıtlarının motorlarının imalatı
- `29.10.04` Minibüs, midibüs, otobüs, troleybüs imalatı
- `29.10.05` Kar motosikleti, golf arabası, ATV, go-kart imalatı
- `29.10.07` Özel amaçlı araçlar (itfaiye, ambulans, mikser, vinçli kamyon…)

Ürün sahibinin istediği "koda bağlı işler listesi" **tam olarak budur** ve
sözlükte hazır duruyor — ama kullanılmıyor.

### 3.1 Sözlükte iki dil karışık

572 başlık Türkçe, gerisi İngilizce. Aynı tabloda:
`'Hunting, trapping and related service activities'` ile
`'Tahıl Yetiştiriciliği'` yan yana. Panelde karışık dil çıkar.

### 3.2 `sector_group` yarı dolu

3319 kodun **1532**'sinde dolu (%46), 12 farklı grup. `is_manufacturing`
**tek değerli** (3319 satırın hepsi aynı) → D-249'a göre **ölü kolon**, sıfır
bilgi taşıyor.

---

## 4. Ölçüm: çoklu NACE bugün tutuluyor mu?

**Yapı var, veri yok.** `company_industries` tablosu tam da doğru tasarlanmış:

```
company_id · nace_code · nace_version · nace_level · is_primary ·
source_id · confidence · verified_at
```

Bu tablo ürün sahibinin istediği her şeyi karşılıyor: çoklu kod, ana/yan ayrımı
(`is_primary`), kaynak izi (`source_id`), güven (`confidence`), doğrulama
zamanı (`verified_at`).

Ama içinde **21 satır** var. 9412 firmadan **21'i**. Ve o 21 firmanın da
hepsi tek kodlu, hepsi `is_primary=True`. Yani **çoklu NACE hiç kullanılmamış**.

Gerçek kod `companies.nace_code`'a yazılmış — yani **tek kodluk düz kolona**.
Çoklu kod oraya sığmaz.

### 4.1 `companies.nace_name` bir başka kaçak

52 firmada dolu, 8 farklı değer: `'Metalurji ve Makina Sanayi'`, `'GIDA'`,
`'KİMYA-LABARATUVAR'`, `'Savunma'`… Bunlar **NACE adı değil**, kaynak sitenin
kendi sektör etiketleri. Yanlış kolona yazılmış serbest metin.

---

## 5. Göç defteri yalan söylüyor (GOC-DEFTER-01)

NACE ölçümü sırasında çıktı, ayrı ama bağlı bir sorun.

`schema_migrations` tablosunda 12 kayıt var. Diskte 25 göç dosyası var.
Her göçün şemadaki izini tek tek kontrol ettim:

| Göç | Şemadaki iz | Durum |
|---|---|---|
| 0012_users_and_catalog | `users` tablosu | **uygulanmış, defterde yok** |
| 0014_packages_marketing | `packages` tablosu | **uygulanmış, defterde yok** |
| 0017_user_activity_log | `user_activity_log` | **uygulanmış, defterde yok** |
| 0018_visibility_layer | görünürlük tabloları | **uygulanmış, defterde yok** |
| 0021_missing_tables | `schema_migrations` | **uygulanmış, defterde yok** |
| 0023_source_records_company_id | `source_records.company_id` | **uygulanmış, defterde yok** |
| 0015_data_log | `data_log` | uygulanmamış (tutarlı) |
| 0016_users_last_login | `users.last_login_at` | uygulanmamış (tutarlı) |
| 0019_admin_mfa | `users.mfa_secret` | uygulanmamış (tutarlı) |
| 0025_kimlik_dosyasi_alanlari | `companies.kimlik_tamligi` | **uygulanmamış** |

**6 göç uygulanmış ama deftere yazılmamış.** Ayrıca 0024 (bugün biz uyguladık,
sonucunu gördük) da defterde yok.

Sonuç: **"hangi göç uygulandı?" sorusunun cevabı bugün yoktur.** Her seferinde
şemayı okumak zorundayız. Ve daha kötüsü — `migrate.py` bir daha çalıştırılırsa
uygulanmış göçleri **tekrar uygulamaya kalkar**.

### 5.1 D-250 buna takılı

`0025` uygulanmamış. Yani `kimlik_tamligi`, `puan_surumu`, `vergi_dairesi`,
`mersis_no`, `ticaret_sicil_no`, `sicil_dairesi` kolonlarının **hiçbiri yok**.
D-250 uygulaması bu göç geçmeden başlayamaz.

Ve `0025` içinde **yeni bir ikiz doğuyor**: `mersis_no` ekliyor, oysa şemada
`mersis_number` kolonu zaten var (0 dolu). Göç uygulanmadan yakalandı.

---

## 6. SEMA-IKIZ-01 ölçümü (tamamlandı)

515 kolonun 511'i İngilizce (%99.2). Türkçe 4 kolon, hepsi `companies`'te,
hepsi sonradan eklenmiş yama:

| Hedef (İngilizce) | Kaynak (Türkçe) | Taşınacak | Çelişen |
|---|---|---:|---:|
| `tax_number` (40 dolu) | `vergi_no` (761) | 730 | 1 |
| `website_domain` (5397) | `web_sitesi` (5049) | 49 | 1 |
| *(yok)* → `address` | `adres` | tümü | 0 |
| *(yok)* → `osb_parcel` | `osb_parsel` (19) | tümü | 0 |

Çelişen tek web kaydı da aslında hata: KAL-MET'in `website_domain` alanına
üyesi olduğu derneğin sitesi (`isim.org.tr`) yazılmış; doğrusu `web_sitesi`
alanında. Yine kaynak sızıntısı.

---

## 7. Öneri — NACE üç katmana ayrılır

Ürün sahibinin ayırdığı üç kavram, üç ayrı yere yazılır:

### Katman 1 — YETKİ (resmî, sicilden)
`company_industries` tablosu (zaten var, kullanılmıyor):
- Firma başına **birden çok satır** — çoklu NACE burada çözülür
- `is_primary` → ana faaliyet / yan faaliyet ayrımı
- `source_id` + `verified_at` → hangi sicil belgesinden, ne zaman
- Kaynak: MERSİS / TSG. **Bugün erişimimiz yok** (TSG-KAYNAK-01: captcha)

### Katman 2 — FİİL (gözlemlenen)
Ayrı alan: firma ne yaptığını **kendi söylüyor** (web sitesi, katalog, ihale).
Bu bir NACE kodu değil, **kanıttır**. Koda çevrilirse `confidence` düşük yazılır.

### Katman 3 — TAHMİN (bizim çıkarımımız)
Bugün `companies.nace_code`'da olan her şey budur. Adı dürüst olmalı:
**tahmin edilmiş koda "kod" denmez.**

### 7.1 Hemen yapılabilecek dört şey (kaynak gerektirmez)

1. **`nace_code` sahteliği itiraf edilir.** Panelde `verified` olmayan kod
   "tahmini sektör" etiketiyle gösterilir, asla "NACE kodu" denmez.
   D-245/D-249'un doğal devamı.
2. **1880 firmalık 29.10 kütlesi işaretlenir.** Tek kaynaktan kopyalanmış
   varsayılan kod → sızıntı. Sektör sayaçlarından çıkarılır.
3. **Açılım level 6'dan gelir.** Ürün sahibinin istediği "koda bağlı işler
   listesi" = o kodun altındaki level-6 başlıkları. Sözlükte hazır, Türkçe,
   %100 dolu. Level 4'ün boş %50'si level 6'dan doldurulabilir.
4. **Çoklu NACE `company_industries`'e taşınır.** Düz kolon çoklu kodu
   taşıyamaz. Tablo zaten doğru tasarlanmış.

### 7.2 Kaynak gerektirenler (bloke)

- Gerçek NACE kodu → MERSİS/TSG (MERSIS-KAYNAK-01)
- Sözlüğün Türkçeleştirilmesi → TÜİK NACE Rev.2 Türkçe listesi (bedava, indirilir)

---

## 8. Açık kararlar

| Kod | Karar | Kimde |
|---|---|---|
| **NACE-KATMAN-01** | Üç katman ayrımı onaylanıyor mu? | ÜRÜN SAHİBİ |
| **NACE-SAHTE-01** | Tahmini kod panelde nasıl etiketlenir? | ÜRÜN SAHİBİ |
| **GOC-DEFTER-01** | Defter şemadan yeniden inşa + elle DDL yasağı | ÜRÜN SAHİBİ |
| **SEMA-IKIZ-01** | Tüm alan adları İngilizce, 4 kolon taşınır | ÜRÜN SAHİBİ |

---

## İlgili Nodlar

- [[AGENTS]]
- [[docs/VERI_KALITE_SOZLESMESI]]
- [[docs/KAPSAM_KIYASI_2026-09-28]]
