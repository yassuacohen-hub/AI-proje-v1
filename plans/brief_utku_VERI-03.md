# VERI-03 — Brief (utku)

**Başlık:** [VERI] Tarama isteklerinde IP/proxy rotasyonu (2s)
**Öncelik:** P2 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/scrapers/proxy_rotation.py`
**Bağımlılık:** `VERI-02`
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.
**Eski kimlik:** WK-03 (D-222'de devredildi; `WK-` öneki D-57 kanonik alan listesinde yok)

> **Tek brif kuralı (D-217):** Bir görev = bir brif. Toplu iş birden çok brife bölünmez;
> tek brifte `## Faz A/B/C...` başlıklarıyla anlatılır. Faz başına ayrı dosya açmak yasak.

## Neden

D-222 denetiminde **hiç başlanmamış** olarak ölçüldü ([`AGENTS.md`](../AGENTS.md:1) D-222 Kural 4). `archive` durumunda gömülü olduğu için backlog'da görünmüyordu. Proxy rotasyonu kendi başına değer üretmez — bir engellenme ölçümüne cevaptır. Bu yüzden VERI-02'ye bağlı.

## Doğrulanacak varsayım

- **Engellenme olduğu varsayılmadı — ölçülecek.** Hangi kaynak, hangi sıklık, hangi HTTP kodu? Somut ölçüm yoksa bu görev **yazılmaz** (YAGNI), panoya "ölçüm yok" notu düşülür.
- Kaynağa saygılı gecikme + `robots.txt` uyumunun sorunu **çözebileceği** varsayıldı. Çözüyorsa proxy'ye hiç gerek yok — en ucuz çözüm budur, orada dur.
- Proxy havuzunun **mevcut olmadığı** varsayıldı. Ücretli servis kararı ürün sahibinindir, ajanın değil — `ac` ile sor.
- Kimlik bilgilerinin mevcut sır yönetimiyle okunacağı varsayıldı. Karşılığı yoksa **dur**, koda gömme.

## Adımlar

1. VERI-02 tamamlanmadan başlama.
2. Engellenme ölçümünü topla (kaynak · sıklık · hata kodu). Ölçüm yoksa **dur**, panoya yaz, kod yazma.
3. Gecikme + `robots.txt` uyumunu önce dene; sorun kalkıyorsa görevi kapat.
4. Ancak o zaman sıralı proxy rotasyonunu yaz.
5. Tek çalıştırılabilir kontrol bırak.

## Kabul kriteri

- [ ] Yalnızca somut engellenme ölçümü varsa kod yazıldı; yoksa gerekçe panoda.
- [ ] Kimlik bilgileri koda gömülmedi.
- [ ] `src/scrapers/proxy_rotation.py` için en az bir çalıştırılabilir kontrol var.
- [ ] Dört varsayımın her biri ya doğrulandı ya panoda sorun olarak açıldı.

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Brifteki bir varsayım kodda tutmuyorsa `ac` ile sorun aç, **uydurma, durma**.

```bash
python scripts/ajan_chat.py ac utku VERI-03 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-03
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-03 --ozet "<özet>"
```

## Bilinçli sınır

ponytail: tavan = sıralı rotasyon, sağlık kontrolü yok. Yükseltme yolu = ölü
proxy görülünce sağlık kontrolü ekle.

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/plans/_brief_sablon]]
- [[Huginn Data Insights/plans/brief_utku_VERI-02]]
