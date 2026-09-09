# Y16 — SEKTOR ZEKASI / MVP MARKET BRAIN (sahip: arastirmaci)

> Ana referans: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md` (V9 Market Brain)

## Gorev
Dashboard'a "sektor sagligi" katmani icin MVP tasarimini arastir ve **islenebilir ozellik listesi + veri yeterlilik analizi** cikari.

## Mevcut veri (baseline)
- 14.000 firma, NACE %100 dolu, web %60, telefon %92
- Kalite skoru dagilimi: 60-79: 4.866 | 40-59: 1.465 | 20-39: 2.438 | 0-19: 4.669
- NACE dagilimi: 29.10 Otomotiv (1.897), 10.11 Gida (924), 62.09 Yazilim (661)...
- Bos tablolar: company_products, company_capabilities, company_events, evidence, commercial_signals (Market Brain icin cok degerli ama simdilik bos)

## Arastirilacak sorular
1. NACE grup bazinda "sektor sagligi kartinin" hangi metrikleri MEVCUT veriyle hesaplanabilir? (firma sayisi, kalite ort., web varligi, kaynak cesitligi, guncellik)
2. Hangi metrikler DISARIDAN gelmeli? (fiyat/haber/sentiment — MVP'de kapsam disi mi?)
3. Dashboard'da gosterim formu: sektor kartinin sutunlari/badge'leri ne olmali?
4. V9 Market Brain'in MVP kupelerinden hangisi bu veriyle simule edilebilir, hangisi Scale asamasina kalmali?

## Cikti
`workspace/external/<ajan>/output/Y16_sektor_zekasi_mvp.md` — ozellik listesi + veri yeterlilik tablosu + MVP kapsam onerisi.

## Orta baglami (sistem V2)
Yerel DB'de calis: `DATABASE_URL=postgresql+psycopg://huginn:huginn_local_dev@localhost:5433/huginn` (14k firma, ~30x hizli sorgu).
