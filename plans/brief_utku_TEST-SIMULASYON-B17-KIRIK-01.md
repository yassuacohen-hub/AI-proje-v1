# TEST-SIMULASYON-B17-KIRIK-01 — Brief (utku)

**Başlık:** [TEST] Kirik testleri ve B-14/B-17 uyarilarini duzelt -> test_cmd_teslim_basarili yesil + simulasyon temiz (2s)
**Öncelik:** P1 · **Kit:** ADMIN-KİT (D-196)
**Kilitli dosya:** `tests/test_gorev_kutusu_cli.py`, `tests/test_gorev_kutusu_simulasyon.py`
**Bağımlılık:** yok
**Hub:** hubs/PLAN_STRATEGY_HUB.md — ZORUNLU (B-14)

## Neden

| Kanıt | Yer |
|---|---|
| 2026-10-03 pytest: 33 passed, 1 failed `test_cmd_teslim_basarili` | `tests/test_gorev_kutusu_cli.py` |
| Kök neden: D-318 bulgu kapısı — defterde kayıt yoksa rc 1; test defter yazmıyor | `scripts/gorev_kutusu.py:160` (`cmd_teslim`) |
| Simülasyon B-14/B-17 uyarı basıyor | `scripts/gorev_kutusu.py:585` (`cmd_simulasyon`) |

Kırık test = pre-commit kapısı yalancı; herkes `--no-verify`'a kayar.

## Doğrulanacak varsayım (D-66)

- Tam takımda kaç test kırık? `python -m pytest -q -p no:cacheprovider --no-header -rf tests > data\tmp_kirik.txt 2>&1` → listeyi brife yaz. "3 kırık" beyanını **sayıyla doğrula**.
- B-14/B-17 uyarıları gerçek ihlal mi, eski kayıt mı? `gorev_kutusu.py simulasyon` çıktısındaki görev kimliklerini panoda kontrol et.

## Adımlar

1. `test_cmd_teslim_basarili`: fixture'da bulgu defterine T-01 kaydı yaz (D-318 kapısı **gevşetilmez**, kaçış kapısı açılmaz).
2. Diğer kırık testler: her biri için kök neden 1 satır; test mi yanlış, kod mu? Kod yanlışsa kodu düzelt, test gevşetme.
3. B-14 (hub eksik) / B-17 uyarıları: eksik hub satırını ilgili brife ekle ya da kaydı arşivle; uyarı 0'a insin.
4. Koş: pre-commit tam takım yeşil.

## Kabul kriteri

- `pytest tests` → 0 failed (sayı raporda, önce/sonra).
- `gorev_kutusu.py simulasyon` → B-14/B-17 uyarısı 0, rc=0.
- Hiçbir testte `skip`/`xfail` eklenmedi.

## Ajan chat zorunlu (D-210 · D-217)

Varsayım tutmuyorsa / faz tıkandıysa sorun aç, uydurma, durma:

```bash
python scripts/ajan_chat.py ac utku TEST-SIMULASYON-B17-KIRIK-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id TEST-SIMULASYON-B17-KIRIK-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id TEST-SIMULASYON-B17-KIRIK-01 --ozet "<özet>"
```

Bulgu defteri kaydı zorunlu (D-318). Teslimden sonra durma (D-312): `gorev_kutusu.py bak --ajan utku` + `ajan_chat.py oku --son 10`.

## Ilgili Nodlar

- [[scripts/gorev_kutusu.py]]
- [[docs/BORC_DEFTERI]]
