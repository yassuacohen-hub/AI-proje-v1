[[Huginn Data Insights/data/orchestrator/VEC-TEST-01_rapor_2026-09-17_kilo.md]]

# VEC-TEST-01 Raporu

**Tarih:** 2026-09-17  
**Ajan:** kilo  
**Paket:** `src/company_master/vector/` (embedder.py, service.py, store.py)

## Yapılanlar

1. Embedder: `to_dict()`, `embed_texts()` fonksiyonu, `client` property (get_client cache) testleri
2. Store: `VectorDoc`/`SearchHit` to_dict, `_cosine` kenar durumları (boş liste, farklı uzunluk, sıfır norm, aynı vektör), boş upsert, count fallback (ChromaDB hata), ChromaDB mock ile upsert/query/delete_all, collection property ChromaDB yoksa geri dönüş
3. Service: `firma_metni` liste değeri, `DuplicateGroup.to_dict`, boş embed sonucu (index_firmalar, find_similar, deduplicate_by_vkn), embed_document, tracer=None else branch tam kapsam, id_key değişken index_firmalar
4. OTEL paketleri (opentelemetry-sdk, jaeger-thrift, instrumentation) bağımlılık çözüldü
5. BOM ve mojibake düzeltildi

## Test Sonuçları

- **tests/vector:** 73 passed, 0 failed
- **Tam süit:** 3595 passed, 4 skipped, 0 failed
- **Kodlama denetimi:** temiz (BOM yok, mojibake yok)

## Kapsam

| Dosya | Stmts | Miss | Cover | Missing |
|-------|-------|------|-------|---------|
| __init__.py | 4 | 0 | 100% | — |
| embedder.py | 71 | 1 | 99% | 79 |
| service.py | 161 | 11 | 93% | 28-29, 45, 105, 112-113, 159-161, 199, 248, 259 |
| store.py | 162 | 26 | 84% | 27, 40-41, 57, 117-118, 121, 126-130, 151, 166-191 |
| **TOPLAM** | **398** | **38** | **90%** | — |

## Riskler

- embedder.py satır 79 (`self._client = get_client()`) OTEL/9Router bağlantı noktası — runtime'da gerçek istemci mevcutsa tetiklenir
- service.py OTEL hata yolları (28-29, 45) ve tracer yok fallback'ler kısıtlı test edilebilir
- store.py ChromaDB gerçek bağlantı satırları (166-191) mock ile kapsandı, üretimdeki ChromaDB hata davranışı doğrulunmamış