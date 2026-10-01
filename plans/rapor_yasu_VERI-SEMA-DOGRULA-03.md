# VERI-SEMA-DOGRULA-03 — NACE Dil Kolonları Denetim Raporu

**Ölçen:** ihsan (orkestratör devralma, D-58) · **Ajan:** yasu
**Tarih:** 2026-10-01 · **Kurallar:** D-222 · D-238 · D-260

## Sonuç

**Dil desteği yok — ne şemada ne kodda.** NACE açılımı tek dilde (Türkçe) tutuluyor.
Brifin işaret ettiği dosya da yanlıştı: tablo `0006_nace_details.sql` değil, [`0002_relations.sql:59`](../src/company_master/schema/migrations/0002_relations.sql:59) içinde kuruluyor.

## 1. Şema denetimi — `nace_codes`

Kaynak: [`0002_relations.sql:59-67`](../src/company_master/schema/migrations/0002_relations.sql:59)

| Sütun | Tür | Dil? |
|---|---|---|
| `nace_code` | TEXT PRIMARY KEY | — |
| `version` | TEXT | — |
| `level` | INTEGER | — |
| `parent_code` | TEXT (self FK) | — |
| `title` | TEXT | **Türkçe** (D-252/6: TÜİK NACE Rev.2 Türkçe listesi) |
| `sector_group` | TEXT | — |
| `is_manufacturing` | BOOLEAN | — |

**Toplam 7 sütun. `name_en` / `name_fr` / `name_de` → hiçbiri yok.**
Dil, sütun adında da kodlanmış değil: tek alan `title` ve içeriği Türkçe.

## 2. Kod denetimi — `acilim_getir()`

Kaynak: [`sunum.py:253`](../src/company_master/sunum.py:253)

```python
@lru_cache(maxsize=512)
def acilim_getir(nace_code: str | None) -> str:
    ...
    SELECT title FROM nace_codes WHERE nace_code = :kod LIMIT 1
```

| Soru | Cevap |
|---|---|
| Parametre sayısı | **1** (`nace_code`) |
| `lang` parametresi | **yok** |
| Sorgulanan sütun | `title` (Türkçe) |
| Veri yoksa | `BOS` döner — 0 veya boş string değil (D-250/7 uyumlu ✅) |

## 3. Karar — dil kolonu şimdi eklenmeli mi?

| Seçenek | Artı | Eksi |
|---|---|---|
| **A. Eklenmesin (önerilen)** | Sıfır iş, sıfır risk. Müşteri Türkçe. | İngilizce rapor istenirse gecikir |
| B. `title_en` eklensin | Çoklu dil hazır | Göç + 1500 satır çeviri + `lang` parametresi + çağıran güncellemesi ≈ 2 gün; **tüketicisi yok (D-236)** |

**Seçtiğim: A.** Tüketicisi olmayan çıktı üretilmez (D-236). İhtiyaç doğduğunda yol açık: `title_en` sütunu + `acilim_getir(kod, lang="tr")` imzası — ikisi de geriye dönük uyumlu.

## Kabul kriteri

- [x] `nace_codes` sütun listesi çıkarıldı (7 sütun)
- [x] Dil sütunlarının yokluğu kanıtlandı
- [x] `acilim_getir()` imzası ve SQL'i ölçüldü
- [x] Rapor dosyası oluşturuldu (bu dosya)

## Öz-eleştiri

Brif üç yerde yanlıştı: dosya adı (`0006` değil `0002`), sütun adı (`name` değil `title`), satır aralığı (250-276 ≈ doğru, şans). Brifi ölçmeden yazmışım. **Ders: brif içindeki dosya yolu da bir beyandır, D-260 brife de uygulanır.**

## Ilgili Nodlar

- [[AGENTS]]
- [[hubs/VERI_KALITESI_HUB]]
