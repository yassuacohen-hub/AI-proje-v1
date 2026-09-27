# Brif — VERI-IVEDIK-YENIDEN-01 (P1)

**Sahip:** utku · **Mod:** code · **Süre:** 2s · **Bağımlılık:** VERI-HAYALET-TEMIZ-01 bitmeden başlamaz

## Sorun

Hayalet temizliği bittiğinde İvedik OSB'den elimizde **sadece 14 firma** kalacak. Bu sayı gerçek olamaz — İvedik Ankara'nın en büyük sanayi bölgelerinden biri.

```
ivedik.org.tr : 3134 satir / 14 tekil firma  (%0.4)
```

Eski kazıyıcı döngüye girdiği için sayfa 1'den öteye hiç geçmemiş; elimizdeki 14 firma **sadece ilk sayfanın içeriği**.

## Yapılacak

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

## Kabul ölçütleri

- Çekilen tekil ünvan sayısı ≈ sitedeki toplam firma sayısı (±%2)
- `jsonl` içinde yinelenen ünvan **yok**
- Sektör sorusu yanıtlanmış (var/yok + neden)
- Yükleme sonrası `ivedik.org.tr` için satır sayısı = tekil ünvan sayısı

## Uyarı

Temizlik öncesi yükleme yapılırsa 3134 hayalet satırın üstüne yenileri eklenir, sorun büyür. **Sıra: önce TEMIZ-01, sonra bu.**
