# Brief — ALTYAPI-DURUM-SOZLUK-01 (P1)

## Kök Neden
Görev durum sözlüğü üç yerde farklı tanımlı; sahte uyarı ve sessiz mantık
çatışması üretiyor.

| Yer | Tanım |
|---|---|
| `src/company_master/orchestrator/task_board.py:31` | `GOREV_DURUMLARI = ("plan","aktif","review","done","blocked","archive")` — **`iptal` yok** |
| `scripts/pano_denetim.py:42` | `KAPALI_DURUMLAR = ("done","archive","iptal")` |
| `scripts/orkestrator_kontrol.py:21` | `KAPALI_DURUMLAR = ("done","iptal","cancelled")` |

Sonuç: `durum=iptal` şema doğrulamasından geçemez ama iki script onu bekliyor;
`cancelled` hiçbir yerde üretilmiyor, ölü değer.

## Yapılacaklar
1. `task_board.py` tek kaynak olsun:
   - `GOREV_DURUMLARI` içine `"iptal"` eklensin.
   - `KAPALI_DURUMLAR = ("done", "archive", "iptal")` **task_board'da** tanımlansın.
2. `pano_denetim.py` ve `orkestrator_kontrol.py` kendi kopyalarını silip
   `task_board`'dan alsın (`orkestrator_kontrol` için import yolu eklenecek).
3. Ölü `cancelled` değeri kaldırılsın.
4. Test: üç modülün aynı tuple nesnesini gördüğünü ve `iptal` durumunun
   `sema_dogrula`'dan geçtiğini kanıtla.

## Dosyalar
- `src/company_master/orchestrator/task_board.py`
- `scripts/pano_denetim.py`
- `scripts/orkestrator_kontrol.py`
- `tests/test_durum_sozlugu.py`

## Kabul
- Tek tanım, üç tüketici. Yeni testler yeşil.

## Sahibi
ihsan — mod: code
