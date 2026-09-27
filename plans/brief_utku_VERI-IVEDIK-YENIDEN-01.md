# Brif — VERI-IVEDIK-YENIDEN-01 (P1)

**Başlık:** [VERI] İvedik kaynağını yeniden kazı (sektör alanı boş) (2s)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `data/ivedik/firmalar.jsonl`
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

**Sahip:** utku · **Mod:** code · **Süre:** 2s · **Bağımlılık:** VERI-HAYALET-TEMIZ-01 bitmeden başlamaz

## Neden
Hayalet temizliği bittiğinde İvedik OSB'den elimizde **sadece 14 firma** kalacak. Bu sayı gerçek olamaz — İvedik Ankara'nın en büyük sanayi bölgelerinden biri.

```
ivedik.org.tr : 3134 satir / 14 tekil firma  (%0.4)
```

Eski kazıyıcı döngüye girdiği için sayfa 1'den öteye hiç geçmemiş; elimizdeki 14 firma **sadece ilk sayfanın içeriği**.

## Adımlar
1. [`ivedik_scraper.py`](../src/company_master/etl/scrapers/ivedik_scraper.py) zaten korumalı [`sayfa_dongusu()`](../src/company_master/etl/scrapers/base_osfb_scraper.py:101) kullanıyor — **doğrula**, kullanmıyorsa geçir.
2. Siteden **gerçek firma sayısını** bul: liste sayfasındaki toplam sayaç ya da son sayfa numarası. Bu sayı hedefimiz.
3. Yeniden çek, `data/ivedik/firmalar.jsonl` üret.
4. Çekilen tekil ünvan sayısını adım 2'deki hedefle karşılaştır — **sapma varsa yükleme yapma, raporla**.
5. Uygunsa ETL ile `companies`'e yükle.

## Ek keşif — sektör alanı boş

İvedik kayıtlarında sektör verisi **sıfır**. Yeniden çekerken şunu da yanıtla:

- Sitede firma kartında/detay sayfasında sektör bilgisi **var mı**?
- Varsa kazıyıcı neden almıyor — seçici mi yanlış, detay sayfası mı atlanıyor?

Cevabı brifin altına ekle. Varsa alanı da çek.

## Kabul kriteri
- Çekilen tekil ünvan sayısı ≈ sitedeki toplam firma sayısı (±%2)
- `jsonl` içinde yinelenen ünvan **yok**
- Sektör sorusu yanıtlanmış (var/yok + neden)
- Yükleme sonrası `ivedik.org.tr` için satır sayısı = tekil ünvan sayısı

## Uyarı

Temizlik öncesi yükleme yapılırsa 3134 hayalet satırın üstüne yenileri eklenir, sorun büyür. **Sıra: önce TEMIZ-01, sonra bu.**

## Doğrulanacak varsayım

> D-66 brif sözleşmesi. Her madde bu brifin gövdesinde **ölçülmüş** bir değere dayanır.
> Kodda tutmayan madde varsa **dur**, panoya sorun aç, uydurma.

- Bağımlılık: `VERI-HAYALET-TEMIZ-01` **bitmeden başlamaz** varsayıldı. Hayalet kayıt dururken yeniden kazıma mükerrer üretir.
- `data/ivedik/firmalar.jsonl` çıktısında sektör alanı **boş** varsayıldı (3134 kayıt). Doluysa yeniden kazıma gereksiz — ölç, raporla.
- Mevcut `ivedik_scraper.py` betiğinin çalışır durumda olduğu varsayıldı. Kaynak site yapısı değiştiyse **dur**, panoya sorun aç.

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Varsayım tutmuyorsa, bir faz tıkandıysa veya @mention aldıysan
chat'e yazmak **zorunludur** — brifi yeniden okuyup beklemek değil.

```bash
python scripts/ajan_chat.py ac utku VERI-IVEDIK-YENIDEN-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-IVEDIK-YENIDEN-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-IVEDIK-YENIDEN-01 --ozet "<ozet>"
```

Teslimden önce `hubs/OSINT_VERI_TOPLAMA_HUB.md` dosyasının "Kapanan işler" bölümüne `VERI-IVEDIK-YENIDEN-01`
satırını yaz (B-14 kapısı) — yazılmazsa teslim reddedilir.

## Ilgili Nodlar

- [[hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
