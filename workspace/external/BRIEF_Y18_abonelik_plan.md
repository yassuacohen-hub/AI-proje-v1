# Y18 — ABONELIK / RATE PLAN TASARIMI (sahip: arastirmaci)

## Gorev
Dashboard (port 8000) + Telegram bot'u kullanan musteri icin **pilot abonelik tier'leri** tasarla. Cikti: tier tablosu + kotalar + isimlendirme onerisi.

## Mevcut altyapi (sistem V2)
- API key auth zaten var: `DASH_API_KEY` env, `X-API-Key` header
- Rate limit: 120 istek/dk sliding window (`web_app.py`)
- KVKK maskeleme: `?mask=1` (deneme) / `DASH_MASK_PII=1` (korumali mod) — tier'larla baglanabilir
- Telegram bot: 10+ komut, gunluk rapor, degisiklik bildirimi

## Arastirilacak sorular
1. Deneme / baslangic / profesyonel tier'larin kota ve veri erisim farklari ne olmali?
2. Rekabet referansi: Kompass TR, Euromonitor TR segmenti — fiyat/kapsam?
3. VKN ve tam iletişim verisi hangi tier'da acilir? (KVKK politika baglantisi)
4. Telegram hatti: hangi tier'da bildirim frekansi farkli olur?

## Cikti
`workspace/external/<ajan>/output/Y18_abonelik_plan.md` — tier tablosu (isim | kota | veri erisimi | fiyat onerisi | KVKK seviyesi).
