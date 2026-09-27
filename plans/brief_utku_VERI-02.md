# VERI-02 — Brief (utku)

**Başlık:** [VERI] OSB ihale ilanlarını izleyip yeni ilanı tespit et (3s)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/scrapers/osb_tender_monitor.py`
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.
**Eski kimlik:** WK-02 (D-222'de devredildi; `WK-` öneki D-57 kanonik alan listesinde yok)

> **Tek brif kuralı (D-217):** Bir görev = bir brif. Toplu iş birden çok brife bölünmez;
> tek brifte `## Faz A/B/C...` başlıklarıyla anlatılır. Faz başına ayrı dosya açmak yasak.

## Neden

D-222 denetimi panodaki 65 kaydı tek tek ölçtü ([`AGENTS.md`](../AGENTS.md:1) D-222 Kural 4). Bu iş **hiç başlanmamış**: adı 42 dosyada geçiyor ama tek satır kod yok. `archive` durumunda gömülü kaldığı için backlog'da görünmüyordu. Gerçek backlog'a alındı ki tekrar unutulmasın.

## Doğrulanacak varsayım

- `src/scrapers/` altında yeniden kullanılabilir bir tarayıcı taban sınıfı olduğu varsayıldı. Yoksa **dur**, panoya sorun aç — sıfırdan altyapı yazma kararı ürün sahibinindir.
- İzlenecek OSB kaynak listesinin **tanımlı olmadığı** varsayıldı. Listeyi ajan uyduramaz; `ac` ile sor.
- Kaynakların HTML sunduğu varsayıldı. RSS veya API varsa **dur** — en ucuz yol o, HTML ayrıştırma yazma.
- "Yeni ilan" için kalıcı durumun veritabanında tutulacağı varsayıldı. Şemada karşılık yoksa **dur**, panoya sorun aç.

## Adımlar

1. Yukarıdaki dört varsayımı ölç. Tutmayanı `ac` ile panoya yaz, uydurma.
2. Kaynak listesi ve erişim biçimi netleştikten sonra tek kaynak için izleyiciyi yaz.
3. Yeni ilan tespitini kalıcı duruma bağla (aynı ilan iki kez "yeni" sayılmasın).
4. Erişim hatasını görünür kıl — sessiz başarı yasak.
5. Tek çalıştırılabilir kontrol bırak.

## Kabul kriteri

- [ ] Yeni ilan tespiti tekrarlanabilir: aynı ilan iki kez "yeni" sayılmaz.
- [ ] Kaynak erişilemezse görev sessizce başarılı olmaz — hata görünür.
- [ ] `src/scrapers/osb_tender_monitor.py` için en az bir çalıştırılabilir kontrol var.
- [ ] Dört varsayımın her biri ya doğrulandı ya panoda sorun olarak açıldı.

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Brifteki bir varsayım kodda tutmuyorsa `ac` ile sorun aç, **uydurma, durma**.

```bash
python scripts/ajan_chat.py ac utku VERI-02 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-02
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-02 --ozet "<özet>"
```

## Bilinçli sınır

ponytail: tavan = tek kaynak + zamanlanmış tetik yok. Yükseltme yolu = kaynak
sayısı 1'i geçtiğinde kaynak listesini yapılandırmaya taşı; izleme sıklığı
konuşulunca tetiğe bağla.

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/plans/_brief_sablon]]
- [[Huginn Data Insights/plans/brief_utku_VERI-03]]
