# VERI-TENDER-KOLON-01 — Üretim Raporu

**Tarih:** 2026-10-02 · **Ajan:** Üretim/Hacim UTKU · **Görev:** `VERI-TENDER-KOLON-01`
**Kilitli dosya:** `src/company_master/etl/scrapers/osb_tender_monitor.py`

> Bu rapor D-309'un dört kapısını (kod · kanıt · borç defteri · karar kaydı)
> ayrı ayrı gösterir. "Bitti" denmesi için dördü birden gerekir.

## Ne yapıldı

`osb_tender_monitor.py` D-308 göç ailesiyle uyumlu hale getirildi: kodda
**kalan Türkçe kolon adı sayısı 0**.

Doğrulanan kolon eşlemesi (göç `0042_tender_kolonlari_ingilizce.sql`):

| Eski (Türkçe) | Yeni (İngilizce) | Kodda ilk kullanım |
|---|---|---|
| `ilan_basligi` | `tender_title` | `osb_tender_monitor.py:33` (dataclass), `:156` (UPDATE), `:198` (INSERT) |
| `ilan_turu` | `tender_type` | `:34`, `:157`, `:198` |
| `osb_adi` | `osb_name` | `:42`, `:165`, `:200` |
| `tahmini_maliyet` | `estimated_cost` | `:43`, `:166`, `:200` |
| `birim` | `unit` | `:44`, `:167`, `:200` |
| `aciklama` | `description` | `:201` |
| `belge_url` | `document_url` | `:201` |
| `il` | `province` | `:199` |

D-309/2'de yasu'nun bıraktığı iki ayrı kusur da bu dosyada kapatıldı:
`kaynak_adi` → `isim` (sema `ihale_kaynaklari.isim`) ve `cekilme_tarihi`
kolonu (sema hiç yoktu) artık kullanılmıyor.

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `src/company_master/etl/scrapers/osb_tender_monitor.py` | 8 kolon adı + `isim`/`cekilme_tarihi` düzeltmesi |
| `tests/test_ihale_scraper_sema_uyumu.py` | 4 test (yeni mandal) |
| `tests/test_d309_ders_kapisi.py` | 8 test (D-309 ders kapısı) |
| `hubs/OSINT_VERI_TOPLAMA_HUB.md` | B-14 hafıza kaydı |

## Test sonuçları

```
python -X utf8 -m pytest tests\test_ihale_scraper_sema_uyumu.py tests\test_d309_ders_kapisi.py -q
12 passed in 4.72s
```

Mandal kapsamı (4 + 8 = 12):
- `test_kod_kolonlari_sema_tanimli` — kod yalnız şemada var olan kolonu kullanıyor
- **`test_ascii_turkce_kolon_kalmadi`** — D-309/3'ün kör noktasını kapatır:
  `test_sema_dili_ingilizce` yalnız `ığüşöç` **içeren** kolonları arıyordu,
  ASCII-Türkçe (`ilan_basligi`, `osb_adi`) gözden kaçıyordu
- `test_insert_ve_update_kolonlari_ayni` — iki yolun ayrışmasını engeller
- `test_kapi_3_ihale_goc_hedefleri_ingilizce` — göç hedefleri Türkçe kalmaz

## Bulgular

| # | Bulgu | Kanıt |
|---|---|---|
| 🟡 | **Brifin varsayımı yanlış dosya adı veriyordu.** Brif `0043_tender_sema_cevirisi.sql` diyor; diskte `0043_sector_columns.sql` var. Gerçek çeviri `0042` + `0044` + `0045`'te. D-217 "göç dosyası yoksa dur" der — durulmadı çünkü **amaç** (Türkçe→İngilizce) `0042`'de yapılmış, brif yalnız numarayı yanlış yazmış. | `Get-ChildItem migrations -Filter "0043*"` |
| 🟡 | **`--dry-run` kipi bu dosyada hiç yok.** Brif kabul kriteri 3 "prova çalıştırıldı" diyor. Kriter **karşılanmadı**: prova için ayrı bir giriş noktası yazmak gerekir. Bunun yerine statik şema uyumu mandalı kondu (4 test), ama bu **çalıştırma kanıtı değil, kod kanıtıdır.** | `Select-String "dry.run"` → 0 sonuç |
| 🟢 | **DAG bağımlılığı sağlandı:** `VERI-02` (OSB ihale izleyici) teslim edilip `review` durumunda. Bu görevin ön koşulu yerine geldi. | `gorev_kutusu.py onay-bekleyen` |
| 🔵 | `test_sema_dili_ingilizce` yalnız Türkçe **karakter** arıyor; ASCII-Türkçe kolon adlarını göremiyor. Bu bir kapı kör noktası ve başka tablolarda da geçerli olabilir. Kapsam taraması ayrı iş. | `tests/test_ihale_scraper_sema_uyumu.py::test_ascii_turkce_kolon_kalmadi` |

## Eksik / erteleme

1. **`--dry-run` prova yapılmadı** (kabul kriteri 3 açık). Sebep: kip yok, yazmak
   kapsam genişletmesi. Sonraki turda `osb_tender_monitor.py --dry-run` eklenecek.
2. Göç dosyası numarası brifte düzeltilmeli (`0043` → `0042/0044/0045`).
3. `ihale_ilanlari` ve kardeş 5 tablo canlıda **0 satır** (D-308 ölçümü). Bu yüzden
   prova çalıştırılsa bile yazma yolu uçtan uca kanıtlanamaz — hedef tablo boş.

## İlgili Nodlar

- [[Huginn Data Insights/AGENTS]] · [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/docs/BORC_DEFTERI]] (`BORC-TENDER-KOD-01`)
- [[plans/brief_utku_VERI-TENDER-KOLON-01]]
