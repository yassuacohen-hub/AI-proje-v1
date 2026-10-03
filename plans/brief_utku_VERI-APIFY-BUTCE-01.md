# VERI-APIFY-BUTCE-01 — Brief (utku)

**Başlık:** [VERI] Apify kullanimini olc ve 10 USD tavan koy -> docs/APIFY_BUTCE.md + tavan kontrolu (1s)
**Öncelik:** P3 · **Kit:** SCRAPE-KİT
**Kilitli dosya:** `docs/APIFY_BUTCE.md` (yeni), `scripts/apify_butce_olc.py` (yeni)
**Bağımlılık:** yok
**Hub:** hubs/PLAN_STRATEGY_HUB.md — ZORUNLU (B-14)

## Neden

| Kanıt | Yer |
|---|---|
| Apify webhook akışı tanımlı, bütçe sınırı yazılı değil | `.agents/skills/osint-web-scraping-toolkit/SKILL.md:57` (Apify Webhook) |
| Belge diskte yok (2026-10-03 ölçümü) | `docs/APIFY_BUTCE.md` → YOK |

Ücretli kaynak sınırsız çalışırsa fatura sürprizi; ürün sahibi tavanı 10 USD/ay dedi.

## Doğrulanacak varsayım (D-66)

- `.env` içinde `APIFY_TOKEN` (veya benzeri) var mı? `findstr /i apify .env` → yoksa görev **yalnız belge** olur, betik yazılmaz; chat'e yaz.
- Apify hesabı gerçekten kullanılıyor mu? `/v2/users/me/usage/monthly` çağrısı 200 dönüyor mu? Dönmüyorsa dur.

## Adımlar

1. `scripts/apify_butce_olc.py`: aylık kullanım USD'yi çek, stdout'a yaz (token yazılmaz), `--tavan 10` üstündeyse rc=2.
2. `docs/APIFY_BUTCE.md`: ölçülen rakam, tavan, kim/nasıl kapatır (Apify konsolunda "Max monthly usage" ayarı — ekran yolu yaz), betik komutu.
3. Apify konsolunda tavanı 10 USD'ye ayarla; ekran görüntüsü yerine ayar sonrası API'den okunan değeri belgeye yaz (D-260).

## Kabul kriteri

- `python scripts\apify_butce_olc.py --tavan 10` → rc=0 ve rakam.
- Belgede ölçülen sayı + tarih var.
- Kod/log'da token yok.

## Ajan chat zorunlu (D-210 · D-217)

Varsayım tutmuyorsa / faz tıkandıysa sorun aç, uydurma, durma:

```bash
python scripts/ajan_chat.py ac utku VERI-APIFY-BUTCE-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-APIFY-BUTCE-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-APIFY-BUTCE-01 --ozet "<özet>"
```

Bulgu defteri kaydı zorunlu (D-318). Teslimden sonra durma (D-312): `gorev_kutusu.py bak --ajan utku` + `ajan_chat.py oku --son 10`.

## Ilgili Nodlar

- [[docs/BORC_DEFTERI]]
- [[.agents/skills/osint-web-scraping-toolkit/SKILL]]
