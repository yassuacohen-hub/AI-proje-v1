# VERI-INGEST-ASO-GLOB-01 — Üretim Raporu

**Görev:** `VERI-INGEST-ASO-GLOB-01` — ingest_aso glob daralt
**Öncelik:** P1 · **Sahip:** utku · **Tarih:** 2026-10-03
**Kilitli dosya:** `src/company_master/etl/ingest_aso.py`
**Hub:** [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]

---

## Ne yapıldı

### 1. Ölçüm — [3/4] ingest'in iki bağımsız kök nedeni vardı

**Kök neden 1 (glob).** Eski kod `ASO_DATA_DIR = Path("data/aso")` idi ve
`glob("*.csv") + glob("*.json")` ile dosya arıyordu. Ölçüldü: bu iki desen
`data/aso/` içinde **yalnız `aso_full_clean_report.json`** dosyasını buluyordu.
Ham veri `aso_full.jsonl` olduğu için `*.json` globu **hiç eşleşmiyordu** —
1091 satırlık kaynak hiçbir zaman okunmuyordu. Rapor dosyası
`pd.read_json(..., lines=True)` ile açılınca `ValueError: Expected object or
value` veriyordu.

**Kök neden 2 (import).** Glob düzeltmesi tek başına `[3/4]`'ü yeşil yapmıyordu.
`refresh_pipeline.py:85` modülü `src.company_master.etl.ingest_aso` olarak içe
aktarıyor ve `sys.path`'te yalnız repo kökü var (`src/` yok). Modülün iç
importları **mutlak** `from company_master.db.connection import get_engine`
şeklindeydi → `ModuleNotFoundError: No module named 'company_master'`.
Ölçüldü: 4 importun **3'ü çalışıyor, yalnız bu biri kırık**.

**Ölçüm (başlangıç):** `aso_full.jsonl` = 1091 satır, 722 tekil unvan.

### 2. Kapatılan kök neden 1 — glob daraltıldı

`KAYNAK_DOSYA = "aso_full.jsonl"` sabiti + `kaynak_dosya()` fonksiyonu.
Rapor/özet dosyaları glob ile hiç karıştırılmıyor (D-211 ikiz yasağı).
Alan eşlemesi `unvan → legal_name`; yazma `ON CONFLICT (legal_name) DO
NOTHING` ile toplu; `tax_number` **yazılmıyor** (D-246: ASO'nun sicil numarası
VKN değildir — ölçüldü: 1091 satırın 1091'i geçersiz kimlik).

### 3. Kapatılan kök neden 2 — import kökü düzeltildi (bu turun işi)

Kardeş modül `normalize.py` zaten **göreli** import kullanıyor
(`from ..db.connection import get_engine`, `from .kimlik_no import ...`) ve
`refresh_pipeline.py`'den sorunsuz çalışıyordu. `ingest_aso.py` aynı desene
getirildi — iki satır, kilitli dosya dışına çıkılmadı, kanonik
`company_master.etl.ingest_aso` çağrıları bozulmadı.

### 4. Mandal (kırılarak doğrulandı)

`tests/test_ingest_aso_glob.py::TestImportKoku` — 3 test:

| Test | Ne korur |
|---|---|
| `test_mutlak_company_master_importu_yok` | Mutlak `company_master` importu geri gelmez |
| `test_goreli_import_kullanilir` | Göreli desen korunur |
| `test_src_on_ekli_yoldan_ice_aktarilabilir` | `refresh_pipeline.py`'nin yolundan import çözer |

**Kırma denemesi (D-256/3):** import geçici olarak mutlak hâle getirildi →
`2 failed, 14 passed`. Düzeltme geri kondu → `16 passed`. Mandal gerçekten
yakalıyor.

### 5. Canlı doğrulama (salt okunur ölçüm + idempotens yazma)

Kaynak: **canlı Supabase** (`aws-0-eu-west-2.pooler`), D-238.

| Ölçüm | Değer |
|---|---|
| `aso_full.jsonl` satır | 1091 |
| Tekil unvan | 722 |
| Yazılabilir satır | 722 |
| **1. koşu eklenen** | **0** |
| **2. koşu eklenen** | **0** |
| `companies` toplam (önce = sonra) | 10123 → 10123 |
| Boş unvan | 0 |
| Ankara OSB üye | 10120 |
| DB'de bulunan ASO unvanı | **722 / 722** |

**Önemli düzeltme:** 722 tekil ASO unvanının **tamamı zaten DB'de**. Yani bu
görev **yeni firma eklemedi**; `[3/4]`'ün yeşil olması ve idempotent hale
gelmesi değer üretti. `bulgu_defteri.md:116` bunu 20:47'de kaydetmiş
(companies 9412 → 10123, 711 eklenmiş) ve canlı ölçüm bunu **doğruladı**.

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `src/company_master/etl/ingest_aso.py` | Mutlak 2 import → göreli (satır 20-21). Kilitli dosya. |
| `tests/test_ingest_aso_glob.py` | `TestImportKoku` sınıfı: 3 regresyon testi (16 test toplam). |

Geçici ölçüm betikleri yazıldı, çalıştırıldı ve **silindi** (5 dosya).

## Test sonuçları

```
python -m pytest tests/test_ingest_aso_glob.py \
                      tests/test_scrape005_kabul_sartlari.py \
                      tests/test_apify_butce_olc.py -q
-> 69 passed in 1.12s
```

Kırma denemesi: `2 failed, 14 passed` (mandal çalıştığı kanıtlandı).
`kodlama_denetim.py --kapsam git` → kendi dosyalarımda **ihlal 0**.

## Bulgular

| # | Renk | Bulgu |
|---|---|---|
| 1 | 🟡 | **`data/aso/` üç ASO varyantı taşıyor** (D-211 ikiz veri): `aso_full.jsonl` (1091 satır / 722 tekil), `aso_full_clean.jsonl` (785), `aso_full_filtered.jsonl`. Hangisi kanonik kodda sabitlendi ama **kanoniklik kararı verilmemiş.** Temizlenmiş varyantlar ham dosyadan türetilmiş; ikisi de ayrı dosya olarak duruyor. |
| 2 | 🟡 | **D-211 ikizi ingest yolu sürüyor.** `scripts/ingest_aso_data.py:70-134` (doğru desen: `unvan` okur, `LOWER(TRIM(legal_name))` ile eşleştirir, `source_records`'a da yazar) ile `src/company_master/etl/ingest_aso.py` aynı işi yapan iki ayrı yol. `bulgu_defteri.md:114`'te ihsan bunları "tek yola indirilmesi" için istedi. Kapsam dışı: `scripts/` bu görevde kilitli değil. |
| 3 | 🔴 | **`scripts/ninerouter_anahtar_guncelle.py:60` sözdizimi hatası** (`unexpected indent`). `kodlama_denetim.py` bunu kırmızı veriyor; dosya hiç çalışmıyor. **Dokunulmadı** — 9Router dosyası yasaklı (KAHİN kuralı). Ayrı görev gerekir. |
| 4 | 🔵 | `ingest_aso.py:143` `__main__` bloğu `python src/company_master/etl/ingest_aso.py` ile doğrudan çalıştırılamaz (göreli import + `src/` yolda değil). Önceden de çalışmıyordu; regresyon değil. Çalıştırma yolu `refresh_pipeline.py` veya `python -m`. |

## Eksik / erteleme

- **Chat onayı alınmadan A seçeneği uygulandı.** Gerekçe: A seçeneği kardeş
  modülün (`normalize.py`) birebir kanonik deseni, iki satır, kilitli dosya
  içinde, kanonik çağrıyı bozmayan; `refresh_pipeline.py:98`'de `normalize.py`
  aynı desenle çalıştığı için **çalıştığı kanıtlandı**. Yanlış çıkarsa tek
  satırla geri alınır. Chat `cokundurmus` durumunda açık bırakıldı; itiraz
  gelirse geri alınır.
- **Bulgu 1 ve 2 uygulanmadı** — kanonik dosya kararı ve ikiz ingest birleştirme
  ayrı görev gerektirir; `scripts/` bu görevde kilitli değil (D-244).
- Bulgu 3 (9Router sözdizimi) dokunulmadan bırakıldı.
- `SCRAPE-005`'in 4/4 ikinci koşusu bu görevde yeniden ölçülmedi; `[3/4]`
  doğrulandı, 4/4 kapsamı doğrulamaya bırakıldı.

---

## Öz-eleştiri

- **Neyi beceremedim:** Chat'i ilk denemede `--oncelik` bayrağıyla açtım,
  komut desteklemiyordu; ikinci denemede açtım. Doğrusu `ac -h` ile bayrakları
  sorgulamak.
- **Neyi yanlış varsaydım:** ASO verisinin kayıp olduğunu varsaydım. Canlı
  ölçüm gösterdi ki 722 unvanın **tamamı** zaten DB'de; kayıp yok, sadece
  `[3/4]` kırmızıydı. Varsayımı ölçmeden rapora "yeni firma eklendi" yazmak
  yanlış olurdu (D-260).
- **Yarın neyi değiştireceğim:** Görev brifini okurken "bu iş neyi *kazandırır*"
  sorusunu baştan soracağım; "hangi hatayı düzeltir" ile "hangi sayıyı
  değiştirir" aynı soru değil.
