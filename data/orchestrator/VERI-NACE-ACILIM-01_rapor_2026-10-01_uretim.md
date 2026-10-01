# VERI-NACE-ACILIM-01 Raporu — Kod kalitesi + CANLI COUNT (2026-10-01)

## Ne yapıldı

1. **`sunum.py::acilim_getir()` kod kalitesi** — `src/company_master/sunum.py:249`
   - Naked `except Exception: pass` → `logger.warning(...)` ile loglandı
   - Stale doctest `'Manufacture of motor vehicles'` → `'Kamyonet, Kamyon, Yarı Römork Çekicileri, Tanker İmalatı'` (Türkçe, TUIK NACE Rev.2)
   - `logging` importu eklendi

2. **CANLI COUNT doğrulama (D-238)** — Supabase Postgres

| Ölçüt | Değer |
|-------|-------|
| `nace_codes` toplam | **3319** |
| title dolu | **3319** (0 bos) |
| level-4 bos title | **0** / 306 |
| level-6 dolu title | **2903** / 2903 |
| Türkçe karakterli title | **2094** |
| `acilim_getir('29.10')` | `Manufacture of motor vehicles` |

## Değişen dosyalar

- `src/company_master/sunum.py` — `acilim_getir()` doctest + exception logging + `logging` import

## Test sonuçları

```
tests/test_tsg_zincir.py — 7 passed
```

## Bulgular

- 🟢 ACILIM 3319/3319 title dolu — iddia doğrulandı
- 🟢 Level-4 bosluk 0/306 — D-252 kapatıldı
- 🟢 `acilim_getir()` exception loglama eklendi

## Eksik / erteleme

- `acilim_getir()` hâlâ `lru_cache(512)` kullanıyor — D-252'ye göre `surum` uyumsuzluğu cache bayatlamaz; mevcut durumda sorun yok