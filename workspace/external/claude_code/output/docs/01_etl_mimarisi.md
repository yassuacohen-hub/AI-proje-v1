# ETL Mimarisi (V9 ile uyumlu, guncel)

**Kaynak:** `AI proje v1/V10/03_mimari/01_etl_mimarisi.md` (Claude Code tarafindan guncellendi, 2026-09-03)  
**Referans:** [[00-Home]] - [[01_sirket_master_ana_belgesi]] - [[01_mvp_gereksinimleri]] - [[01_veri_toplama_modeli]] - [[01_versiyon_9_baglam_dokumani]]

Bu belge, [[01_sirket_master_ana_belgesi]] (Company Master V1.0) SSOT ana baglam dokumanidir. Tum ETL kararlari V9 ile uyumlu olmalidir.

## 1. Veri akisi

```text
SOURCE
  |
  v
RAW INGESTION (scraper + API, KVKK filtreli)
  |
  v
Pydantic VALIDATION GATE (quarantine_firms fallback)
  |
  v
NORMALIZATION (source_records -> companies)
  |
  v
ENTITY RESOLUTION (VKN/domain fuzzy match)
  |
  v
COMPANY MASTER (PostgreSQL SSOT)
  |
  +---> ChromaDB (1536-dim capability vectors)
  +---> Neo4j (firm/product/risk graph)
  +---> Redis (<300ms warm cache)
  |
  v
ENRICHMENT (TOPSIS, NACE, OSB)
  |
  v
DATA QUALITY SCORE (0-100)
  |
  v
SEARCH INDEX (PostgreSQL trigram + ChromaDB cosine)
  |
  v
INTELLIGENCE LAYER (Market Brain + Customer Brain)
```

Ham veri ile temizlenmis veri ayridir. SSOT kurali: PostgreSQL tek dogruluk kaynagidir; ChromaDB/Neo4j/Redis read-optimized projection'dir.

## 2. Migration sira numarasi (0001-0005)

| No | Baslik | Kapsam |
|----|--------|--------|
| 0001 | Initial schema | `companies`, `osbs`, `sources`, `source_records` |
| 0002 | Quarantine layer | `quarantine_firms`, error_reason, raw_payload jsonb |
| 0003 | Quality + Verification | `data_quality_score`, `entity_confidence`, `nace_validity` |
| 0004 | Intelligence staging | `job_signals`, `signal_type`, `is_active` |
| 0005 | Indexes | `idx_companies_legal_name_trgm` (GIN pg_trgm), `idx_companies_tax_number`, `idx_companies_is_ankara_osb` |

Migration dosyalari `src/company_master/db/migrations/NNNN_*.sql` formatinda uretilir ve `python -m company_master.etl.migrate` ile sirayla uygulanir.

## 3. Quality score formulu (V9 + V8 Bulgu #3 duzeltmesi)

`data_quality_score` araligi 0-100; kritik alan agirliklari:

| Alan | Agirlik |
|------|---------|
| adres | 20 |
| vergi_no | 20 |
| web_sitesi | 15 |
| osb_parsel | 15 |
| sektor | 10 |
| telefon | 10 |
| nace_code | 5 |
| email | 5 |
| **Toplam** | **100** |

Bos kritik alan cezalari:

| Alan | Ceza |
|------|------|
| vergi_no yok | -15 |
| adres yok | -10 |
| web_sitesi yok | -5 |
| telefon+email+vergi_no hepsi bos | -5 (ekstra) |

Son skor `clamp(0, 100)` ile sinirlanir. Hesaplama: `src/company_master/etl/normalize.py:_data_quality_score()`.

## 4. Detay scrape durumu

| Kaynak | Liste scrape | Detay scrape | Detay alanlari |
|--------|--------------|--------------|-----------------|
| OSTIM (`ostim.org.tr`) | TAMAM (`scrape_tum_osb`, sektorler bazinda) | TAMAM (`fetch_firma_detay`, slug bazli) | web_sitesi, adres, vergi_no, osb_parsel, sosyal_medya |
| ASO (`aso.org.tr`) | TAMAM (`run_full_scrape`) | KISMEN (yalnizca listeleme sayfasi bilgileri) | telefon, email, unvan |
| EKAP | BACKLOG (Faz 2) | - | ihale_no, kurum, son_teklif_tarihi |
| LinkedIn / Kariyer.net | BACKLOG | - | pozisyon, lokasyon |
| GIB e-Fatura | BACKLOG (Faz 2) | - | anonim satis trendi |
| TOBB kapasite raporu | BACKLOG (Faz 2, OCR) | - | makine listesi, guc, tonaj |

Detay scrape pipeline'i:
1. `scripts/ingest_ostim_detail.py` `data/ostim/firmalar_detayli.jsonl` dosyasini satir satir okur.
2. `legal_name` (case-insensitive trim) uzerinden `companies` tablosunda eslestirir.
3. `companies.website_domain / primary_phone / primary_email / tax_number / vergi_no / web_sitesi / osb_parsel` alanlarini `COALESCE` ile gunceller (mevcut veri ezilmez).
4. `source_records.raw_payload` uzerine detay metadata (`adres`, `sektor`, `sosyal_medya`, `yetkili`, `vergi_no_extracted`, `osb_parsel_extracted`, `slug`, `cekilme_tarihi`, `detay_kaynagi`) jsonb merge ile ekler.
5. Batch sonlarinda commit; hata durumunda rollback + log.

Bilinen kisiltlar:
- OSTIM robots.txt her zaman erisilebilir degil; operator manuel onayi gerekir (`scraping_permission_router.py`).
- VKN fallback yalnizca unvan icindeki 11-haneli regex ile calisir.
- 80 karakterden uzun osb_parsel degerleri None yapilir (`is_parsel_payload`).

## 5. Entity Resolution esikleri (V9)

```text
95-100 -> otomatik eslestir
85-94  -> guclu aday
70-84  -> ikinci kontrol
<70    -> eslestirme yapma
```

Esikler gercek veri benchmark'i ile yeniden ayarlanir. V8 simulasyonu (100x100x100) ile yapilan kalibrasyon sonucu `src/company_master/entity_resolution/matcher.py` icinde tutulur.

## 6. Ana kimlik karari

```text
company_id = UUID (Primary Key)
VKN = benzersiz kimlik/dogrulama alani
MERSIS = yardimci kimlik alani
domain = VKN yoksa fallback entity resolver girdisi
```

## 7. Arama (Search) mimarisi

Ilk MVP icin **PostgreSQL + Full Text Search (trigram) + LIKE** yeterlidir. Meilisearch/Elasticsearch ilk gunden zorunlu degildir.

- `idx_companies_legal_name_trgm` (GIN pg_trgm) ile benzerlik aramasi.
- `search_companies(query, limit)` similarity() DESC sirali doner.
- JSONL fallback (DB aktarim oncesi): `search_jsonl`.
- Dashboard: `fetch_dashboard_companies`, `fetch_filtered_companies` (sector, kalite_min/max, has_phone/email/web).

## 8. Mimari sinir

Company Master tek basina tahmin ve skorlama YAPMAZ (satin alma, butce, firsat skoru vb.). Bunlar Intelligence Engine katmanlarinin (Market Brain + Customer Brain + Opportunity Engine) sorumlulugudur. Tam tablo tanimlari icin master belge SSOT §3'e bakiniz.

## 9. Ensemble ve kalibrasyon notlari (V8 -> V9)

TOPSIS C_i* artik Portfolio Engine'e **ayri bir skor** olarak gitmez (V8 D6 duzeltmesi). Ensemble zaten fit'i icerir; double counting kaldirildi.

Fit agirligi V7'de %20 iken V9'da **%35** olarak guncellendi (V8 Bulgu #3). Bonuslar sinirlandi: field_verification +0.05, active_intent_10d +0.03.

## 10. Degisiklik ozeti (2026-09-03)

- Migration sira numarasi 0001-0005 olarak standardize edildi.
- Quality score formulu tablo olarak eklendi (V9 ile uyumlu).
- Detay scrape durum tablosu eklendi (OSTIM tamam, ASO kismen, digerleri backlog).
- SSOT, Pydantic validation gate ve quarantine katmani acikca diagrama eklendi.
- Bonus sinirlari (field +0.05, intent +0.03) not edildi.
- Mimari sinir maddesi Intelligence Engine'e atifla guncellendi.

## 11. Handoff

Bu belge V9 aktif baglam dokumani ile eszamanli olarak guncel tutulur. Yeni bir tarayici, kalite alani veya migration eklendiginde ilgili tablolar buraya yansitilir.

Referanslar:
- [[01_versiyon_9_baglam_dokumani]] (SSOT)
- [[01_sirket_master_ana_belgesi]]
- [[V10/03_mimari/01_etl_mimarisi]] (orijinal konum)
