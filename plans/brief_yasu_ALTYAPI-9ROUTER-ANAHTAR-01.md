# ALTYAPI-9ROUTER-ANAHTAR-01 — Brief (yasu)

**Başlık:** [ALTYAPI] 9Router anahtar guncelleme betigini yaz -> scripts/ninerouter_anahtar_guncelle.py (2s)
**Öncelik:** P2 · **Kit:** ADMIN-KİT (D-196)
**Kilitli dosya:** `scripts/ninerouter_anahtar_guncelle.py` (yeni), `tests/test_ninerouter_anahtar_guncelle.py` (yeni)
**Bağımlılık:** yok
**Hub:** hubs/PLAN_STRATEGY_HUB.md — ZORUNLU (B-14)

## Neden

| Kanıt | Yer |
|---|---|
| Anahtar `.env` içinde `NINEROUTER_KEY`; istemci başlığa koyuyor | `src/company_master/gateway/ninerouter_client.py:147` (`_headers`) |
| Anahtar testi var, güncelleme yolu yok | `scripts/api_anahtar_testi.py:115` (`test_et`), `env_oku` :28 |
| Betik diskte yok (2026-10-03 `dir scripts` ölçümü) | `scripts/ninerouter_anahtar_guncelle.py` → YOK |

Anahtar döndüğünde `.env` elle düzenleniyor; yanlış satır / çift anahtar riski. Tek komutla güvenli değişim istiyoruz.

## Doğrulanacak varsayım (D-66)

- `.env` içinde `NINEROUTER_KEY=` satırı **tek** mi? `findstr /c:"NINEROUTER_KEY" .env` ile say. Birden fazlaysa dur, chat'e yaz.
- `api_anahtar_testi.py` 9Router'ı kapsıyor mu? `SAGLAYICILAR` (:43-90) içinde `NINEROUTER` yoksa önce oraya satır ekle.

## Adımlar

1. `scripts/ninerouter_anahtar_guncelle.py <yeni_anahtar>`: `.env` oku, `NINEROUTER_KEY=` satırını değiştir (yoksa ekle), yedek `.env.bak_<tarih>` al, atomik yaz (tmp + replace).
2. Anahtar **stdout'a/log'a yazılmaz**; yalnız "guncellendi, ilk 4 karakter: xxxx" basılır.
3. Sonunda `api_anahtar_testi.py`'nin 9Router testini çağır; başarısızsa yedeği geri yükle, rc=1.
4. Test: `tmp_path` üstünde sahte `.env` ile değişim + geri yükleme (`monkeypatch` ile test_et sahte).

## Kabul kriteri

- `python scripts\ninerouter_anahtar_guncelle.py --kuru xxxx` → değişiklik yok, plan basar.
- pytest yeni test dosyası yeşil; `tests/vector/test_ninerouter_client.py` bozulmaz.
- Çıktıda ve commit'te anahtar değeri yok (D-288 dersi).

## Ajan chat zorunlu (D-210 · D-217)

Varsayım tutmuyorsa / faz tıkandıysa sorun aç, uydurma, durma:

```bash
python scripts/ajan_chat.py ac yasu ALTYAPI-9ROUTER-ANAHTAR-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id ALTYAPI-9ROUTER-ANAHTAR-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id ALTYAPI-9ROUTER-ANAHTAR-01 --ozet "<özet>"
```

Bulgu defteri kaydı zorunlu (D-318). Teslimden sonra durma (D-312): `gorev_kutusu.py bak --ajan yasu` + `ajan_chat.py oku --son 10`.

## Ilgili Nodlar

- [[scripts/api_anahtar_testi.py]]
- [[docs/BORC_DEFTERI]]
