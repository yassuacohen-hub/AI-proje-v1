# ETL Mimarisi Review

**Tarih:** 2026-09-02  
**Reviewer:** Claude Code (external agent)  
**Kaynak:** V10/03_mimari/01_etl_mimarisi.md  
**Baglam:** V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md

## V9 Baglam ile Tutarlilik

### Tutarli Olan Bolumler
- ETL adimlari (SOURCE -> RAW INGESTION -> NORMALIZATION -> VALIDATION -> ENTITY RESOLUTION -> COMPANY MASTER) V9 ile uyumlu.
- 22 tablo referansi (V9 ile uyumlu).
- pg_trgm extension kullanimi V9 da belirtilmis.

### Tespit Edilen Tutarsizliklar
1. **Migration sira numarasi:** V9 0001-0004 olarak gosteriyor, guncel durum 0001-0005 (normalize eklendi). Bu bir duzeltme degil ama update edilmeli.
2. **OSTIM detay scraper durumu:** V9 da 8.313 firma icin detay scrape tamamlandi yaziyor, ancak data/ostim/firmalar_detayli.jsonl dosyasi mevcut degil.
3. **Quality score formulu:** V9 da 70/40 olan eski formula, normalize.py icinde guncellenmis (vergi 20 + adres 20 + web 15 + parsel 15 + sektor 10 + tel 10 + email 5 + nace 5). Update edilmeli.

## Eksik Bolumler (Onerilen Eklentiler)

### Olceklendirilebilirlik
- 8.313 firma icin batch insert performansi: 1000-2000 kayit/batch onerilir.
- Idempotentlik: content_hash ile mevcut.
- Connection pooling: SQLAlchemy engine pool size ayarlanmali.

### Hata Yonetimi
- Retry mekanizmasi: transient DB hatalari icin (3 deneme, exponential backoff).
- Dead letter queue: basarisiz normalize islemleri icin.
- Logging: structured JSON log formati.

### Observability
- Metrics: ETL sureleri, basari/hata oranlari.
- Tracing: OpenTelemetry entegrasyonu.
- Alerting: Slack/PagerDuty uyarilari.

## Diyagram Onerileri

### Veri Akis Diyagrami (Mermaid)

graph LR
    A[OSTIM JSONL] --> B[pipeline.py]
    B --> C[source_records]
    C --> D[normalize.py]
    D --> E[companies]
    E --> F[entity_resolution.py]
    F --> G[entity_resolution tablosu]
    E --> H[search/engine.py]
    H --> I[Streamlit UI]


## API Kontrat Aciklamalari

| API | Base URL | Auth | Kullanim |
|-----|----------|------|---------|
| Supabase | https://xxx.supabase.co | API Key | PostgreSQL connection |
| OSTIM Scraper | ostim.org.tr | None | Web scrape |
| Telegram Bot | api.telegram.org | Bot Token | Bildirim |

## Sonuc

Genel olarak V9 baglam dokumani ile uyumlu. Migration sira numarasi ve quality score formulu guncellemeleri dokumana yansitilmali. Detay scrape ve observability eksikleri P1 oncelikli olarak ele alinmali.
