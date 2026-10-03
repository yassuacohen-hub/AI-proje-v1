# VERI-OSTIM-HREF-FILTRE-01 — Brief (utku)

**Başlık:** [VERI] OSTIM detay kaziyicida web sitesi href filtresini duzelt -> _is_company_website + 100 firma pilot satir denetimi (2s)
**Öncelik:** P2 · **Kit:** SCRAPE-KİT
**Kilitli dosya:** `src/company_master/etl/scrapers/ostim_detail_scraper.py`, `tests/test_ostim_detail_scraper.py`
**Bağımlılık:** SCRAPE-005 karar belgesi okunmuş olmalı
**Hub:** hubs/PLAN_STRATEGY_HUB.md — ZORUNLU (B-14)

## Neden

| Kanıt | Yer |
|---|---|
| Filtre 9 satır; sosyal/harita/mailto adreslerini web sitesi sayıyor olabilir | `src/company_master/etl/scrapers/ostim_detail_scraper.py:27` (`_is_company_website`) |
| SCRAPE-005 reddedildi: doluluk gösterildi, satır doğruluğu gösterilmedi | `data/orchestrator/SCRAPE-005-KAZIMA-DOCKER-INTEGRATION_karar_2026-10-03.md` |
| Kural: doluluk ≠ kalite | `docs/BORC_DEFTERI.md:1518` (D-292) |

## Doğrulanacak varsayım (D-66)

- Mevcut çıktıda `web_sitesi` alanı dolu kayıtların kaçı `facebook|instagram|linkedin|maps.google|mailto|ostim.org.tr` içeriyor? Say, sayıyı brife yaz. **0 ise görev küçülür**: yalnız test ekle, chat'e yaz.

## Adımlar

1. Ölçüm: mevcut çıktı dosyasında yanlış-pozitif sayısı (yukarıdaki regex), `scripts/ostim_href_olc.py` kalıcı betik.
2. `_is_company_website`: ret listesi (sosyal, harita, mailto, tel:, ostim.org.tr, javascript:) + şema zorunlu `http(s)`.
3. Pilot: 100 firma yeniden çek; **10 tanesini elle aç**, tabloya `slug | href | gerçek site mi (E/H)` yaz (D-292 satır denetimi).
4. Test: 8 örnek href için parametrize (4 doğru, 4 yanlış).

## Kabul kriteri

- Yanlış-pozitif sayısı ölçüm öncesi/sonrası tabloda.
- 10/10 elle denetim tablosu raporda.
- pytest yeşil; `ostim_scraper.py` dokunulmaz (D-290 kaynak kilidi).

## Ajan chat zorunlu (D-210 · D-217)

Varsayım tutmuyorsa / faz tıkandıysa sorun aç, uydurma, durma:

```bash
python scripts/ajan_chat.py ac utku VERI-OSTIM-HREF-FILTRE-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-OSTIM-HREF-FILTRE-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-OSTIM-HREF-FILTRE-01 --ozet "<özet>"
```

Bulgu defteri kaydı zorunlu (D-318). Teslimden sonra durma (D-312): `gorev_kutusu.py bak --ajan utku` + `ajan_chat.py oku --son 10`.

## Ilgili Nodlar

- [[data/orchestrator/SCRAPE-005-KAZIMA-DOCKER-INTEGRATION_karar_2026-10-03]]
- [[docs/BORC_DEFTERI]]
