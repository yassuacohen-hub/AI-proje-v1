# Brif — VERI-NACE-TEMIZ-01: Sektör sayacı kirlenmesini düzelt → nace_code temizliği

**Başlık:** [VERI] Sektör sayacı kirlenmesini düzelt, `nace_code` temizliği (2s)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

**Sahip:** utku · **Süre:** 2s · **Veren:** ihsan
**Önkoşul:** `VERI-NACE-SOZLUK-01` (geçerlilik kontrolü referans listeye bağlı)
**Kanıt tabanı:** `plans/brief_utku_VERI-NACE-SOZLUK-01.md` bölüm 1

---

## Neden

Ölçülen kirlilik (canlı Supabase):

`companies.nace_code` içinde NACE kodu **olmayan** değerler var:

| Değer | Firma | Ne olduğu |
|-------|-------|-----------|
| `1163` | 168 | OSTİM sektör sayfasındaki firma sayacı |
| `410` | 68 | aynı |
| `780` | 62 | aynı |
| `794` | 54 | aynı |
| `757` | 53 | aynı |

Bunlar kazıma sırasında sayfadaki **sektör firma sayısı** rakamının NACE kodu
sanılıp yazılmasından geliyor. Tamamı `nace_source='unknown'`.

Ayırt edici işaret: geçerli NACE kodları **noktalı** (`47.79.04`, `10.11`),
bu değerler **noktasız düz sayı**. Ama sadece desene güvenmeyin — `nace_codes`
referansına karşı doğrulamak kesin yol.

## Adımlar
1. `companies.nace_code` değerlerini `nace_codes` tablosuna karşı kontrol et.
2. Eşleşmeyenleri **silmeden önce** dök: kaç satır, hangi değerler, hangi
   `nace_source`. Sayıyı rapora yaz.
3. Eşleşmeyenleri `NULL`'a çek ve `nace_source='invalid_cleared'` işaretle.
   **Kaydı silme** — firma duruyor, sadece yanlış kod gidiyor.
4. `sector_default` / `fallback` kökenli kodlara **dokunmayın** bu görevde;
   onlar yanlış ama "uydurma varsayılan" başka bir problem (bkz. bölüm 5).
   Bu görev sadece **NACE olmayan çöp** değerleri hedefliyor.

## Kabul kriteri
- Temizlik sonrası `nace_code` değerlerinin **tamamı** `nace_codes`'ta var
- Firma sayısı değişmemiş (14003 → 14003) — hiçbir kayıt silinmedi
- Temizlenen satır sayısı raporda yazılı

## 4. Uyarı — yazma öncesi yedek

Canlı DB'de 14003 firma. Toplu `UPDATE` öncesi yedek alın, önce 100 satırlık
parti deneyin. Geri alınamaz bir hata bu görevde en olası risk.

---

## 5. İKİNCİ TUR ÖLÇÜM — kök neden ETL değil, KAYNAK (2026-09-27)

Ürün sahibi haklı çıktı: *"resmi kaynaklardan teyit edilecek, ASO firma
listesi gibi"*. Resmi oda kayıtlarında firma→NACE **var** ve elimizde duruyor:

| Kaynak | Kayıt | raw_nace dolu | Şekli geçerli NACE |
|--------|-------|---------------|--------------------|
| ostim.org.tr | 9513 | 6242 | 6188 |
| aso.org.tr | 592 | 592 (%100) | 592 |
| baskentosb.org.tr | 761 | 761 (%100) | **0** — NACE değil, sektör adı ("Metalurji ve Makina Sanayi") |
| ivedik.org.tr | 3134 | 0 | 0 |

**Ham kaynak ile DB'ye yazılanın karşılaştırması (ünvan köprüsüyle):**

| Kaynak | Eşleşen | Ham ile AYNI | Ham EZİLMİŞ | Ham var, DB boş |
|--------|---------|--------------|-------------|-----------------|
| ostim | 3146 | **3046 (%96.8)** | 15 (%0.5) | 85 (%2.7) |
| aso | 128 | 105 (%82.0) | 0 (%0) | 23 (%18) |

**Bu benim önceki teşhisimi düzeltiyor.** "ETL eşleştirmeyi bozdu" demiştim —
yanlış. ETL kaynağı **sadakatle kopyalamış**. Bozukluk kaynakta:

```
OSTİM raw_nace dağılımı        →  companies.nace_code (sector_default)
   29.10   1897 firma          →     29.10   1881
   10.11    924                →     10.11    911
   62.01    635                →     62.01    629
   41.10    605                →     41.10    600
```

Birebir aktarım. Ama OSTİM'in `10.11` (et ürünleri işleme) dediği firmalar:
*"SOLAR GÜNLERİ FHT ENERJİ", "Cebrail Can - Ilgın Market", "APOLET İŞ
SAĞLIĞI VE GÜVENLİĞİ"*. `29.10` (motorlu kara taşıtı) dedikleri: *"Yurtiçi
Kargo", "Kv Elektrik Üretim", "Tava Türk Mutfağı"*.

→ Bunlar **OSTİM sektör sayfasının varsayılan kodu**, firmanın kendi NACE'si
değil. `nace_source='sector_default'` etiketi zaten bunu söylüyordu:
**5705 firma (%40.7) uydurma varsayılan taşıyor.**

### Bundan çıkan iki değişiklik

1. **TEMIZ-01'in kapsamı genişliyor.** Sadece noktasız çöp (~400 satır)
   değil, `sector_default` kökenli 5705 satır da NULL'lanacak — çünkü
   `nace_codes`'a karşı **geçerli görünürler** (29.10 gerçek bir NACE kodu),
   şekil testinden geçerler, ama **yanlıştırlar**. Şekil kontrolü bunları
   yakalayamaz; yakalayan tek işaret `nace_source` kolonudur.

   Silme ölçütü: `nace_source IN ('sector_default','fallback','title_default')`
   → 6381 satır. Kalan güvenilir çekirdek: `unknown` kökenli 2519 satır
   (bunların %96.8'i resmi kaynakla birebir uyuşuyor).

2. **Güven katmanı ayrışıyor.** Üç ayrı kalite seviyesi var, tek kolonda
   toplanmamalı:

   | Seviye | Kaynak | Firma | Güven |
   |--------|--------|-------|-------|
   | A — resmi oda kaydı | aso + ostim gerçek NACE | ~2500 | yüksek |
   | B — ünvan kesişimi | sözlük + kesişim (D-234) | hedef | orta |
   | C — sektör varsayılanı | OSTİM sayfa kodu | 5705 | **sıfır, atılacak** |

   A seviyesi **altın örneklemdir**: B'nin (ünvan kesişimi) doğruluğunu
   ölçmek için hazır cevap anahtarı. Kesişim motoru yazılınca önce bu 2500
   firmada denenecek, isabet oranı raporlanacak.

### Ek iş: baskentosb sektör adı köprüsü

761 firma NACE değil **sektör adı** taşıyor ("Metalurji ve Makina Sanayi",
"KİMYA-LABARATUVAR", "GIDA"). Bunlar atılmamalı — 12 farklı sektör adı,
resmi xlsx'teki sektör sütunuyla eşlenebilir. Elle 12 satırlık eşleme
tablosu yazmak, 761 firmayı kaybetmekten ucuz.

---

*ponytail: geçersiz + uydurma kodu NULL'lama, güven seviyesini nace_source'ta
tutma. Skipped: doğru kodu yeniden bulma (eşleştirme) — o COKLU-01 ve ünvan
kesişimi işi. A seviyesi 2500 firma onun cevap anahtarı olacak.*

## Doğrulanacak varsayım

> D-66 brif sözleşmesi. Her madde bu brifin gövdesinde **ölçülmüş** bir değere dayanır.
> Kodda tutmayan madde varsa **dur**, panoya sorun aç, uydurma.

- Önkoşul `VERI-NACE-SOZLUK-01` bitmiş varsayıldı — geçerlilik kontrolü `nace_codes` referans listesine bağlı. Sözlük boşsa **dur**.
- 2. tur ölçüm: 5705 firma (%40.7) **uydurma varsayılan** `nace_code` taşıyor varsayıldı. Sayı farklıysa yeniden ölç.
- Kök neden ETL değil **KAYNAK** olarak düzeltildi (önceki teşhisim yanlıştı). Ham kaynak ile DB karşılaştırması ünvan köprüsüyle yapılacak.
- Sayaç biçimli değer (`'1163'` gibi) temizlendi, **0** kaldı varsayıldı; NN.NN biçimli yanlış kod BAG-01 kapsamında. Çakışma varsa KAHİN'e sor.

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Varsayım tutmuyorsa, bir faz tıkandıysa veya @mention aldıysan
chat'e yazmak **zorunludur** — brifi yeniden okuyup beklemek değil.

```bash
python scripts/ajan_chat.py ac utku VERI-NACE-TEMIZ-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-NACE-TEMIZ-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-NACE-TEMIZ-01 --ozet "<ozet>"
```

Teslimden önce `hubs/VERI_KALITESI_HUB.md` dosyasının "Kapanan işler" bölümüne `VERI-NACE-TEMIZ-01`
satırını yaz (B-14 kapısı) — yazılmazsa teslim reddedilir.

## Ilgili Nodlar

- [[hubs/VERI_KALITESI_HUB]]
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
