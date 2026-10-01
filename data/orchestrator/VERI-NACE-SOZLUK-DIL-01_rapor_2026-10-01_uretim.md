# VERI-NACE-SOZLUK-DIL-01 Raporu — CANLI COUNT + ACILIM koordinasyonu (2026-10-01)

## Ne yapıldı

1. **CANLI COUNT doğrulama (D-238)** — Supabase Postgres, ACILIM ile aynı sorgu kümesi

| Ölçüt | Değer |
|-------|-------|
| `nace_codes` toplam | **3319** |
| title dolu | **3319** (0 bos) |
| Türkçe karakterli title | **2094** |
| level-4 bos title | **0** / 306 |
| level-6 dolu title | **2903** / 2903 |
| `companies.nace_code` dolu | **8289** / 9412 |

2. **ACILIM koordinasyonu** — her iki görev aynı COUNT'u ölçtü:
   - ACILIM: `nace_codes` 3319/3319 title dolu → GEÇTi
   - SOZLUK-DIL: 0 bos title → GEÇTi
   - Ortak: level-4 bosluk 0/306, level-6 2903/2903

## Değişen dosyalar

- Yok (sadece ölçüm)

## Test sonuçları

```
tests/test_tsg_zincir.py — 7 passed
```

## Bulgular

- 🟢 SOZLUK-DIL 0 bos title — iddia doğrulandı
- 🟢 ACILIM + SOZLUK-DIL aynı COUNT'u ölçtü, çelişki yok
- 🟢 Level-4 bosluk 0/306 — D-252 kapatıldı

## Eksik / erteleme

- TUIK NACE Rev.2 Türkçe listesi indirilmedi — 2094 Türkçe karakterli title hâlâ yarım ASCII (D-252/6)