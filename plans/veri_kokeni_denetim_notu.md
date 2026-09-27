# Veri Kökeni Denetimi — "X firmanın NACE kodu gerçekten bu mu?"

> **Durum:** ölçüm tamamlandı, düzeltme bekliyor
> **Tarih:** 2026-09-27
> **Soru (ürün sahibi):** *"Mevcut veritabanımızdaki tüm listeler — NACE kodu, firma adı vs — gerçek veriye dayanıyor değil mi? Bunu nasıl ölçeriz? 'X firmanın NACE kodu gerçekten bu mu?' sorusuna cevap ne?"*
> **Kural:** Her satır ölçümle doğrulandı. Varsayımlar ayrı işaretli.

---

## 0. ÖLÇÜMÜN SINIRI — önce bunu okuyun

Ölçüm `backups/company_master_pre_dedup_20260908_090326.db` (**SQLite yedeği**) üzerinde yapıldı.
Kod ise **PostgreSQL** kullanıyor (`ILIKE`, `::float`, `NOW()`, `raw_payload->>` ifadeleri).

Ölçüm sırasında bu iki şemanın **uyuşmadığı** ortaya çıktı:

| Kodun sorduğu | SQLite yedeğinde |
|---|---|
| `companies.nace_code` | **YOK** — 18 dosyada, 65 kez sorulan kolon |
| `companies.search_text` | **YOK** |
| `companies.source_record_id` | **YOK** |
| `source_records` tablosu | **YOK** — tablolar yalnızca `companies`, `osbs`, `quarantine_firms` |

**Yani:** Ya bu yedek eski bir şemadan, ya da canlı Postgres bambaşka. Her iki halde de
aşağıdaki doluluk sayıları **bu yedek için kesin**, canlı Postgres için **doğrulanmamış**.

⚠️ **İlk yapılacak iş budur:** canlı Postgres'te aynı ölçümü koşup bu notu teyit etmek.
Onaylanmadan bu nottaki sayılarla karar verilmemeli.

---

## 0.1 Kısa cevap

**Firma adı, telefon, adres, web sitesi: EVET gerçek.** OSTİM'den kazındı, tarihi ve kaynağı JSONL'de kayıtlı.

**NACE kodu: HAYIR — öyle bir veri yok.** Sektör var, NACE kodu yok. Sektör de OSTİM'in kendi beyanı, doğrulanmamış.

**En ciddi bulgu:** Veritabanına **hangi satırın nereden geldiğini soramıyoruz** — köken alanları ETL sırasında düşmüş. Yani bugün *"bu bilgi gerçek mi?"* sorusuna **veritabanından cevap verilemiyor**; sadece yedek JSONL dosyalarına elle bakarak cevaplanabiliyor.

---

## 1. Ölçülen Gerçekler

### 1.1 Zincirin tamamı

```
OSTİM web sitesi (ostim.org.tr)
   ↓ kazıma — 2026-09-03, tek gün
data/ostim/firmalar_detayli_filtered.jsonl   5483 kayıt, 17 alan
   ↓ ETL / ice aktarim — 2026-09-01 19:40-19:41  ⚠️ JSONL'DEN ÖNCE
companies tablosu                            8313 satır, 29 kolon
```

⚠️ **Tarih çelişkisi:** DB kaydı (09-01) kazımadan (09-03) **önce**. Yani DB'deki veri bu JSONL'den gelmiyor — **başka, daha eski bir kazımadan**. Hangisinden geldiği **izlenemiyor** (köken kolonu yok).

### 1.2 JSONL tarafı — burada köken VAR ve iyi

| Alan | Doluluk | Not |
|---|---|---|
| `unvan` | 5483 / %100 | |
| `web_sitesi` | 5483 / %100 | |
| `adres` | 5483 / %100 | |
| `sektor` | 5483 / %100 | ⚠️ kirli, aşağıda |
| **`kaynak`** | 5483 / %100 | `ostim.org.tr` — **köken kaydı var** ✅ |
| **`cekilme_tarihi`** | 5483 / %100 | `2026-09-03`, tek gün — **tarih var** ✅ |
| `telefonlar` | 5083 / %93 | |
| `emailler` | 2701 / %49 | |
| **`vergi_no`** | **3 / %0** | 5483 firmanın **3'ünde** var |
| `vergi_no_kaynagi` | 3 | `source_records` — 3 kayıt için köken var ✅ |
| `osb_parsel` | 5 / %0 | |

**Yorum:** Kazıyıcı doğru tasarlanmış — `kaynak` + `cekilme_tarihi` + `vergi_no_kaynagi` alanları tam da bu sorunun cevabı için konulmuş. Sorun kazımada değil, **ETL'de**.

### 1.3 EN CİDDİ BULGU — köken ETL'de kayboluyor

| Alan | JSONL | companies tablosu |
|---|---|---|
| `kaynak` | 5483 dolu | **kolon YOK** ❌ |
| `cekilme_tarihi` | 5483 dolu | **kolon YOK** ❌ |
| `sektor` | 5483 dolu | **kolon YOK** ❌ |
| `vergi_no_kaynagi` | 3 dolu | **kolon YOK** ❌ |
| `slug` | 5483 dolu | **kolon YOK** ❌ |
| `web_sitesi` | 5483 dolu | kolon var, **dolu 0** ❌ |
| `adres` | 5483 dolu | kolon var, **dolu 0** ❌ |
| `vergi_no` | 3 dolu | kolon var, **dolu 0** ❌ |

**Elde veri var, veritabanında yok.** `web_sitesi` ve `adres` 5483 kayıtta dolu ama DB kolonu boş — ETL bu alanları **yazmıyor**.

`source_url` kolonu sistemde yalnızca `quarantine_firms` tablosunda var — o da **0 satır**. Yani köken izi **sadece hatalı kayıtlar için** tasarlanmış, doğru kayıtlar için değil. Ters kurgu.

### 1.4 NACE / sektör — "gerçekten bu mu?" sorusunun cevabı

| Ölçüt | Sonuç |
|---|---|
| `nace_code` kolonu | **hiçbir tabloda yok** |
| `nace_validity` | 8313/8313 → **tamamı `'unknown'`** |
| JSONL `sektor` | 5483/%100 dolu — **ama 17 tekil değer** |
| Sektör değeri temiz mi? | **HAYIR — 5483/5483'ünde (%100) sayı yapışık** |

Ölçülen gerçek değerler:

```
'Otomotiv1163'                      -> ad='Otomotiv'  yapışık=1163  (942 firma)
'Yapı ve İnşaat794'                 -> ad='Yapı ve İnşaat'  yapışık=794
'Makine ve Makine Ekipmanları757'   -> yapışık=757
```

Yapışık sayı = OSTİM'in filtre menüsündeki firma sayacı (`Yapı ve İnşaat (794)`). Kazıyıcı menü etiketini **olduğu gibi** almış, sayıyı ayıklamamış. `nace_to_ostim_sektor.json` içindeki `sektor_sirket_sayisi` alanı **aynı sayı** — yani bu hata sözlüğe de taşınmış.

**Cevap:** *"X firmanın sektörü gerçekten bu mu?"* → **OSTİM sitesinde hangi menüde listelendiği**. Bu bir **beyan**, resmî NACE tescili değil. NACE kodu ise **hiç yok**.

### 1.4.1 Test verisi karışmış olabilir — 108 satır

`seed/seed_ankara_osb.py:231` **rastgele** kalite skoru üretiyor:
`"data_quality_score": round(40 + random.random() * 30, 2)` — ünvanı `Test Firma {i}`.

Ölçüm:

| Ölçüt | Sonuç |
|---|---|
| `legal_name like 'Test Firma%'` | **0** ✅ seed adları DB'de yok |
| `company_id` UUID biçimli (36 karakter) | **108** ⚠️ seed `uuid.uuid4()` kullanıyor |
| `company_id` slug biçimli (gerçek kazıma) | 8205 |

**Yorum:** Seed'in ürettiği ünvanlar yok, ama 108 satır seed'in kimlik biçimini taşıyor.
Bunlar ASO/birleştirme kaynaklı da olabilir — **ölçülmedi**. 108 satır denetlenmeli.
(`%test%` eşleşen 29 kayıt gerçek firma: `ADİL TESTERE MAKİNE`, `Aren Test Laboratuvarı` — yanlış alarm.)

### 1.5 Kalite skorları anlamsız

| Kolon | Değer | Yorum |
|---|---|---|
| `data_quality_score` | **0.0** (8313/8313) | sistem kendi verisine "kalite 0" demiş |
| `entity_confidence` | 1.0 (8313/8313) | sabit — hesaplanmamış |
| `status_confidence` | 1.0 (8313/8313) | sabit |
| `status` | `active` (tekil=1) | herkes aktif — **doğrulanmamış** |
| `is_ankara`, `is_osb_member`, `osb_id` | tekil=1 | tek değer → ayırt etmiyor |

JSONL'de ise `_quality_score=54.0`, `_db_quality_score=45.0`, `_dqt_pass_rate=74.99` gibi **gerçekten hesaplanmış** skorlar var. Bunlar da DB'ye taşınmamış.

✅ **Panoya yansımıyor — ölçüldü.** Sunum katmanında (`api/`, `dashboard/`, `ui/`, `rapor/`)
`quality_score` döndüren/etiketleyen **0 satır** bulundu. Yani `0.0` değeri şu an
müşteri ekranına çıkmıyor. Risk **potansiyel**, aktif değil.

⚠️ Ama `search/engine.py:182` bu kolonla **filtreliyor**
(`COALESCE(c.data_quality_score,0) >= :kalite_min`). Hepsi `0.0` olduğundan
`kalite_min > 0` seçilen her aramada **sonuç boş döner**. Bu aktif bir hata.

### 1.6 Kazıma kalitesi — küçük ama gerçek hatalar

| Hata | Ölçüm | Örnek |
|---|---|---|
| slug ünvanla uyuşmuyor | **35 / 5483 (%1)** | ünvan `OTO PARÇACIM YEDEK PARÇA`, slug `osman-korkmaz` |
| İki firma tek satırda | 1 / 5483 | `YANAR KAZAN MAKİNA LTD. ŞTİ. \| KUBUŞ KAZAN` |

%1 düşük ama sıfır değil. `ASDEM ASANSÖR KUMANDA PANOLARI` → slug `emre-zer` gibi durumlar **firma adı yerine kişi adı** alındığını gösteriyor.

### 1.7 NACE doldurma script'leri — 12 script, sonuç sıfır

| Script | Satır | Kaynağı |
|---|---|---|
| `nace_eksik_doldur.py` | 144 | yerel dosya + **tahmin mantığı** |
| `nace_enrich_phase2.py` | 130 | yerel dosya + **tahmin mantığı** |
| `nace_enrich_phase3.py` | 98 | *"1266 firma için fallback strategy"* |
| `fill_nace_from_aso.py` | 66 | ASO verisi |
| `sektor_doldur.py` | 70 | yerel + tahmin |
| + 7 script daha | | |

Hiçbiri **canlı resmî kaynağa** (MERSİS, Ticaret Sicil Gazetesi, TÜİK) sormuyor. Hepsi ünvandan/sektörden **çıkarım** yapıyor. Üç fazlı iş yapılmış, **veritabanına yazılmamış**.

> **Kritik ayrım:** Çıkarılmış NACE ile tescilli NACE aynı şey değil. Panoda "NACE kodu" diye gösterilirse müşteriye **doğrulanmış bilgi** izlenimi verir. Bu bir **güven riski**.

---

## 2. "Gerçekten bu mu?" sorusunu ölçülebilir kılmak — öneri

Tek bir kolon bu sorunu çözer: **her alanın yanında kökeni**.

```
company_source (yeni tablo)
  company_id     -> hangi firma
  field_name     -> hangi alan (nace_code, sektor, primary_phone...)
  value          -> o anki değer
  source         -> 'ostim.org.tr' | 'MERSIS' | 'cikarim:unvan' | 'elle'
  source_url     -> tam adres
  fetched_at     -> çekilme tarihi
  confidence     -> 1.0 resmî tescil | 0.6 site beyanı | 0.3 çıkarım
```

Bu yapıyla ürün sahibinin sorusu **tek sorguyla** cevaplanır:

```sql
select field_name, value, source, fetched_at, confidence
from company_source where company_id = ?
```

**Pano tarafı için asıl kazanç — güven etiketi:**

| Kaynak | Etiket | Pano gösterimi |
|---|---|---|
| MERSİS / Ticaret Sicil | **Tescilli** | yeşil |
| OSTİM site beyanı | **Beyan** | sarı |
| Ünvandan çıkarım | **Tahmin** | gri + "doğrulanmadı" |

Böylece hiçbir ekranda tahmin, tescil gibi görünmez.

### Asgari sürüm (lazy — tam tablo gerekmeden)

`companies` tablosuna **3 kolon** eklenmesi sorunun %80'ini çözer:
`source` (metin), `source_fetched_at` (tarih), `nace_confidence` (ondalık).
Tam köken tablosu, alan bazında geçmiş gerektiğinde eklenir.

---

## 3. Bulguların iş etkisi

| Bulgu | Etki | Aciliyet |
|---|---|---|
| **Şema uyuşmazlığı** — kod `nace_code`/`source_records` soruyor, yedekte yok | 18 dosya çalışmaz durumda olabilir | **en yüksek** |
| `data_quality_score=0.0` + arama filtresi | `kalite_min>0` seçen her arama **boş döner** | **yüksek** |
| `web_sitesi`/`adres` JSONL'de dolu, DB'de boş | **5483 firmanın verisi kullanılmıyor** | **yüksek** |
| Köken kolonları yok | "gerçek mi?" sorusu cevaplanamaz | **yüksek** |
| Sektör değerlerinde yapışık sayı | sözlük eşleşmesi bozuk | orta |
| NACE kodu hiç yok | sektör bazlı analiz yapılamaz | orta |
| DB tarihi < kazıma tarihi | DB'deki veri hangi kazımadan bilinmiyor | orta |
| 108 UUID biçimli `company_id` | test verisi karışmış olabilir | orta |
| 35 hatalı slug | eşleştirmede %1 gürültü | düşük |
| ~~`data_quality_score` panoda görünüyor~~ | ✅ ölçüldü — görünmüyor | — |

---

## 4. Önerilen iş kalemleri

| Kod | İş | Neden |
|---|---|---|
| `VERI-SEMA-01` | **Canlı Postgres'te aynı ölçümü koş** — şema tek mi, `nace_code` var mı | bu notun geçerliliği buna bağlı |
| `VERI-ETL-01` | ETL'in `web_sitesi`, `adres`, `vergi_no` yazmamasını düzelt | 5483 kayıt elde duruyor |
| `VERI-KOKEN-01` | `companies`'e `source` / `source_fetched_at` / `nace_confidence` ekle | soru cevaplanabilir olsun |
| `VERI-SEKTOR-01` | Sektör değerlerinden yapışık sayıyı ayıkla (`re.sub(r"\d+$", "")`) | %100 kirli |
| `VERI-NACE-01` | NACE ataması + **"tahmin" etiketiyle** yaz | tescil gibi görünmesin |
| `VERI-SEED-01` | 108 UUID biçimli `company_id` denetle | test verisi karışmış olabilir |

**Sıra önerisi:** `VERI-SEMA-01` **önce** (diğer her şey buna dayanıyor) →
`VERI-ETL-01` (elde duran veri) → `VERI-KOKEN-01` → `VERI-SEKTOR-01` → `VERI-NACE-01` → `VERI-SEED-01`.

⚠️ `VERI-SEMA-01` sonucu bu notun bazı sayılarını **geçersiz kılabilir**. Sıra atlanmamalı.

---

## 5. Ölçülmeyenler (varsayım olarak işaretli)

- **Canlı Postgres şeması** — ölçülmedi. Bu notun en büyük boşluğu (`VERI-SEMA-01`).
- 108 UUID biçimli `company_id` gerçekten seed mi — ölçülmedi.
- Diğer OSB JSONL'leri (`ivedik`, `baskent`, `aso`, `merged`) aynı kirliliği taşıyor mu — ölçülmedi.
- MERSİS/Ticaret Sicil Gazetesi'nden NACE **programla alınabilir mi** — ölçülmedi.
- `merged_companies.jsonl` (4.2MB) DB'nin gerçek kaynağı mı — ölçülmedi.

### Ölçüldü ve temizlendi (yanlış alarmlar)

- ~~`data_quality_score` panoda görünüyor~~ → sunum katmanında 0 satır ✅
- ~~Seed test firmaları DB'de~~ → `Test Firma%` 0 satır ✅
- ~~`%test%` eşleşen 29 kayıt test verisi~~ → gerçek firmalar (`ADİL TESTERE MAKİNE`) ✅

## İlgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/plans/ekap_ihale_yuklenici_kesif_notu]]
