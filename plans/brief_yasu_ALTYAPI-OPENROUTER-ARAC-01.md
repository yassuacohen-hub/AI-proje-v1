# ALTYAPI-OPENROUTER-ARAC-01 — Brief (yasu)

**Başlık:** [ALTYAPI] OpenRouter araclarini kalici yap -> scripts/or_*.py + continue_haftalik_bildir.py takipli, haftalik schtasks (2s)
**Öncelik:** P2 · **Kit:** ADMIN-KİT (D-196)
**Kilitli dosya:** `scripts/continue_haftalik_bildir.py`, `scripts/or_batch_cikar.py`, `scripts/or_fiyat_ara.py`, `scripts/or_kod_liste.py`, `scripts/or_sablon_ekle.py`, `scripts/or_seckin.py`
**Bağımlılık:** yok
**Hub:** hubs/PLAN_STRATEGY_HUB.md — ZORUNLU (B-14)

## Neden

| Kanıt | Yer |
|---|---|
| 6 betik git'te takipsiz (`??`), 2026-10-03 `git status` ölçümü | `scripts/or_*.py`, `scripts/continue_haftalik_bildir.py` |
| Haftalık bildirim betiği var ama zamanlayıcı yok | `scripts/continue_haftalik_bildir.py:97` (`main`), `bildir` :73 |

Takipsiz betik = bir `git clean` ile kaybolur. Haftalık koşu elle yapılıyor.

## Doğrulanacak varsayım (D-66)

- 6 betiğin her biri `python <betik> -h` ile hatasız açılıyor mu? Açılmayanı sil ya da düzelt; **yeni betik yazma** (R1).
- İçlerinde anahtar/`.env` değeri sabit yazılı mı? `findstr /i "sk-or" scripts\or_*.py` → bulunursa dur, chat'e yaz.

## Adımlar

1. Her betiğe 3 satırlık modül docstring (ne yapar, nasıl çağrılır, çıktı nereye).
2. `git add -f` gerekmez; yol sınırlı commit (`git add -- scripts/or_*.py scripts/continue_haftalik_bildir.py`).
3. `schtasks /create /tn HuginnORHaftalik /sc weekly /d MON /st 09:00 /tr "python <tam yol>\continue_haftalik_bildir.py"` — komutu `docs/OPENROUTER_ARACLAR.md`'ye yaz, kendin bir kez `schtasks /run` ile dene.
4. Bir duman testi: `tests/test_or_araclar_import.py` → 6 modül import edilebilir.

## Kabul kriteri

- `git status` → 6 betik takipli.
- `schtasks /query /tn HuginnORHaftalik` → kayıt var.
- pytest duman testi yeşil.

## Ajan chat zorunlu (D-210 · D-217)

Varsayım tutmuyorsa / faz tıkandıysa sorun aç, uydurma, durma:

```bash
python scripts/ajan_chat.py ac yasu ALTYAPI-OPENROUTER-ARAC-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id ALTYAPI-OPENROUTER-ARAC-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id ALTYAPI-OPENROUTER-ARAC-01 --ozet "<özet>"
```

Bulgu defteri kaydı zorunlu (D-318). Teslimden sonra durma (D-312): `gorev_kutusu.py bak --ajan yasu` + `ajan_chat.py oku --son 10`.

## Ilgili Nodlar

- [[scripts/api_anahtar_testi.py]]
- [[docs/BORC_DEFTERI]]
