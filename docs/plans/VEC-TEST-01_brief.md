# VEC-TEST-01 — Vektör katmanı test kapsamı ≥ %90 (kilo, P2)

> Ortak kurallar: `docs/plans/GECE-ZINCIR-01_ortak_kurallar.md`. Zincir halkası 2/6.

## Kapsam
- Paket: `src/company_master/vector/` (`embedder.py`, `service.py`, `store.py`).
- Testler: `tests/vector/` (mevcut: test_embedder, test_service, test_store, test_matcher, test_ninerouter_client, conftest).

## İş
1. `python -X utf8 -m pytest tests/vector -q --cov=src/company_master/vector --cov-report=term-missing` → başlangıç kapsamını rapora yaz.
2. Kapsanmayan dallara test ekle. Öncelik:
   - `store.py`: chromadb **yokken** in-memory fallback (`HAS_CHROMA` monkeypatch), boş `query`, `where` filtresi, `_cosine` sıfır vektör, `delete_all` sonrası `count`, `upsert` tekrar (aynı id → güncelleme).
   - `embedder.py`: ağ yok senaryosu (mock), boş liste, batch bölme, hata yolu.
   - `service.py`: `deduplicate_by_vkn` kenarları, `index_firmalar` boş girdi, `search` top_k>count.
3. Dış servis çağrısı MOCK'lanır (9router/OpenAI'ye gerçek istek YOK; `_no_real_env_secrets` fixture'ı korunur).
4. `src/` değişikliği yalnız gerçek bug bulunursa (rapora "BUG" başlığıyla).

## Teslim kriteri
- `tests/vector` kapsamı ≥ %90 (`term-missing` çıktısı raporda).
- Tam süit yeşil; kodlama_denetim temiz.
- Rapor: `data/orchestrator/VEC-TEST-01_rapor_<tarih>_kilo.md`.
