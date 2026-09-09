# Company Master V1.0 — Python Altyapısı

Ankara B2B şirket evreni için Company Master V1.0 implementasyonu. V10 belgelerinde tanımlanan şema, ETL ve arama altyapısının Python kod karşılığıdır.

## Mimari

`
company_master/
├── schema/            # PostgreSQL şema
│   ├── migrations/    # Numaralı migration seti (0001–0004) — esas kaynak
│   └── companies.sql  # Eski tek-dosya şema (legacy; SQLite test fallback'i ile kullanılır)
├── etl/               # Ham veri → master akışı
│   └── pipeline.py    # ingest_source / normalize / entity_resolution
├── entity_resolution/ # Eşleştirme motoru
│   └── matcher.py     # VKN + unvan fuzzy matching
├── search/            # PostgreSQL Full Text Search
│   └── fulltext.py
└── services/          # Dış servis istemcileri
    ├── test_nvidia_requests.py
    ├── test_nvidia_langchain.py
    └── test_nvidia.js
`

## Yol Haritası

Bkz. V10/TODO.md (P0) ve V10/project_state.md (Karar Bekleyenler).

## İlgili Belgeler

- V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md
- V10/03_mimari/01_etl_mimarisi.md
- V10/01_gereksinimler/01_mvp_gereksinimleri.md
- V10/07_referanslar/01_veri_kaynagi_envanteri.md
