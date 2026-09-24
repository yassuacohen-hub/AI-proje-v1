---
agent: harici_ajan
source: workspace\external\harici_ajan\output\etl_pipeline_analysis.md
ingested: 2026-09-12T07:24:44.858430+00:00
type: task_output
task_id: unknown
updated_at: unknown
sahip: unknown
durum: unknown
---
# ETL Pipeline Analizi

## Kapsam
- Modul: src/company_master/etl/pipeline.py (5991 bayt)
- Amac: OSTIM jsonl -> source_records (RAW INGESTION)
- Adimlar: 1) Kaynak olusturma, 2) content_hash ile dedup, 3) Batch insert

## Onemli Noktalar
1. **Kaynak Yonetimi:** ensure_source() ile sources tablosunda ostim.org.tr kaydi
2. **Idempotent:** content_hash devre disi birakir, tekrar calistirma guvenli
3. **Veri Kalitesi:** data_quality_score (phone varsa 70, yoksa 40)
4. **Performans:** Psycopg executemany ile tek ag turu batch insert

## Eksiklikler ve Oneriler
- NACE validator eklenebilir (nace_code dogrulugu kontrol edilmelidir)
- Retry/backoff mekanizmasi: transient DB hatalari icin
- Structured JSON log formati onerilir (log parsing kolaylasir)

*Bu içerik harici_ajan tarafından 2026-09-12 07:24:44 UTC'de ingest edildi.*
