# Ajan İşbirliği (ORCH-12) Kılavuzu

> Kaynak: `src/company_master/orchestrator/isbirligi.py`
> Denetim izi: `data/orchestrator/isbirligi_raporu.jsonl`
> Test: `tests/test_isbirligi.py`
> Önemli: `scripts/gorev_kutusu.py` → `yardim` / `destek-al` komutları

## 1. Amaç

Ajanlar panoda boştaken baska ajanların plan/blocked görevlerine
**güvenli destek** sunabilir. Destek ajan sadece `tests/`, `docs/`,
`plans/` altina yazdirir — hedef dosya kilitlere cakismaz.

## 2. Komutlar

### 2.1 `yardim` — Bosta ajani gösterir

```
python scripts/gorev_kutusu.py yardim
```

Posta kutusu bos + aktif/review gorevi olmayan ajanlari listeler.
Her ajan icin ilk oneriyi gosterir:

```
BOSTA: kilo, cline | ONERI: kilo->COP-15(test); cline->yok
```

### 2.2 `destek-al` — Destek iste

```
python scripts/gorev_kutusu.py destek-al --ajan kilo --hedef COP-15 --rol test
```

| Parametre | Zorunlu | Aciklama |
|-----------|---------|----------|
| `--ajan` | Evet | Destek veren ajan id |
| `--hedef` | Evet | Desteklenecek gorev ID |
| `--rol` | Evet | `"test"` veya `"arastirma"` |

Akis:
1. Hedef gorev kontrol edilir (var, plan/blocked, kendi gorev degil)
2. `<hedef>-DESTEK-<AJAN>` ID ile yeni gorev panoya eklenir
3. `otomatik_onay=True` isaretlenir
4. Ajan postasına tetik düşer
5. Hedefin `destek` listesine guncellenir

### 2.3 Otomatik onay (tetik icin)

Destek gorevi `otomatik_onay=True` ile olusturulur.
Destekci teslim ettiğinde (`gorev_kutusu.py teslim`):

1. `trigger.teslim_et()` otomatik olarak `onayla()` cagirir → görev `done`
2. `isbirligi_raporu.jsonl` goruntulenir (denetim izi)
3. Hedef gorevin not'a islenir

## 3. Denetim Iz Formatı

`data/orchestrator/isbirligi_raporu.jsonl` — her satır bir JSON nesnesi:

```json
{
  "tarih": "2026-09-13T16:56:52",
  "destek_task": "COP-15-DESTEK-KILO",
  "ajan": "kilo",
  "hedef": "COP-15",
  "rol": "test",
  "ozet": "[DESTEK:test] test yaz",
  "onaylayan": "oto:nobetci"
}
```

| Alan | Aciklama |
|------|----------|
| `tarih` | Onay/an zaman damgası |
| `destek_task` | Destek gorev ID |
| `ajan` | Destek veren ajan |
| `hedef` | Orjinal hedef gorev ID |
| `rol` | `"test"` veya `"arastirma"` |
| `ozet` | Destek gorev basligi/Notu (150 karakter) |
| `onaylayan` | Onaylayan (oto:NOBETCIsI kalitim) |

## 4. Güvenlik Kurallari

- Destek dosyalari YALNIZCA `tests/`, `docs/`, `plans/` altinda olabilir
- Aktif/review durumundaki gorevlere destek onerilmez
- Kendi gorevine destek verilemez
- Tamamlanmış (done) gorevlere destek verilemez
- Tekrar destek istenirse `ValueError` (idempotency)

## 5. API Kullanimi

```python
from src.company_master.orchestrator import isbirligi

# Bosta ajani bul
bosta = isbirligi.bos_ajanlar()  # -> ["kilo", "cline"]

# Aday gorevleri listele
oneriler = isbirligi.yardim_edilebilir("kilo")  # -> [{task_id, sahip, rol, ...}, ...]

# Destek olustur
sonuc = isbirligi.destek_al("kilo", "COP-15", "test")
# sonuc["gorev"] -> destek gorev dict
# sonuc["hedef"] -> "COP-15"

# Denetim izini oku
import json
with open("data/orchestrator/isbirligi_raporu.jsonl") as f:
    for satir in f:
        rapor = json.loads(satir)
```
