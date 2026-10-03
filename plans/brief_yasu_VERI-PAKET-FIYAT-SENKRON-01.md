# VERI-PAKET-FIYAT-SENKRON-01 — Brief (yasu)

**Başlık:** [VERI] Paket fiyat senkronunu denetle -> sync_paket_fiyatlari.py ile paketler.py tek kaynak, fark raporu (1s)
**Öncelik:** P2 · **Kit:** ADMIN-KİT (D-196)
**Kilitli dosya:** `scripts/sync_paket_fiyatlari.py`, `tests/test_paket_fiyat_senkron.py` (yeni)
**Bağımlılık:** yok
**Hub:** hubs/PLAN_STRATEGY_HUB.md — ZORUNLU (B-14)

## Neden

| Kanıt | Yer |
|---|---|
| Fiyatlar kodda sabit | `src/company_master/paketler.py:207` (`_ORJINAL_FIYATLAR`), `fiyat_katalogu` :250 |
| Senkron betiği var, hangi yöne yazdığı/ne zaman koştuğu belgesiz | `scripts/sync_paket_fiyatlari.py` |
| Tasarım belgesi "mevcut ölçüldü" diyor ama fiyat farkı tablosu yok | `docs/PAKET_KOTA_TASARIMI.md:5` (§1) |

İki kaynak (kod sabiti + DB) farklıysa müşteri paneli yanlış fiyat gösterir; Mimir katalog bloğu da buradan besleniyor.

## Doğrulanacak varsayım (D-66)

- DB `packages` tablosundaki fiyatlar ile `_ORJINAL_FIYATLAR` **aynı mı**? `--kuru` ile fark tablosu çıkar. Fark 0 ise görev test + belge satırına iner; chat'e yaz.

## Adımlar

1. `sync_paket_fiyatlari.py --kuru` → `paket | kod | DB | fark` tablosu stdout.
2. Tek yön kuralı: **kod → DB** (SSOT = `paketler.py`). Betikte başka yön varsa kaldır.
3. Test: sahte DB satırları ile fark hesabı (DB'ye bağlanmadan, fonksiyon seviyesinde).
4. `docs/PAKET_KOTA_TASARIMI.md` §1'e 1 satır: "fiyat SSOT = paketler.py; senkron komutu: ...".

## Kabul kriteri

- `--kuru` çıktısı raporda.
- pytest yeşil; `paketler.py` değişmez (yalnız okunur).

## Ajan chat zorunlu (D-210 · D-217)

Varsayım tutmuyorsa / faz tıkandıysa sorun aç, uydurma, durma:

```bash
python scripts/ajan_chat.py ac yasu VERI-PAKET-FIYAT-SENKRON-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-PAKET-FIYAT-SENKRON-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id VERI-PAKET-FIYAT-SENKRON-01 --ozet "<özet>"
```

Bulgu defteri kaydı zorunlu (D-318). Teslimden sonra durma (D-312): `gorev_kutusu.py bak --ajan yasu` + `ajan_chat.py oku --son 10`.

## Ilgili Nodlar

- [[docs/PAKET_KOTA_TASARIMI]]
- [[prompts/mimir_sistem_promptu]]
