# MVP Kapsamı — V9 Birleştirme ve Ankara OSB Odak

Bağlantılar: [[00-Home]] · [[01_sirket_master_ana_belgesi]] · [[01_v9_ile_karsilastirma]] · [[project_state]] · [[CHANGELOG]] · [[TODO]]

Bu belge, V9 Master Context (V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md) ile V10 Company Master V1.0 arasındaki MVP kapsamı birleştirmesini sabitler. V9'un tüm katmanları MVP'ye alınmaz; yalnızca Faz 0 (V10 Company Master V1.0) kapsamındaki bileşenler aktive edilir.

## V9 §17.1 — Initial Beachhead

> OSTİM / Ankara — Dense B2B ecosystem, SMEs, manufacturing/supplier relationships. Manageable geographic scope, potential network effects.

**Karar:** MVP kapsamı **yalnızca Ankara** ile sınırlıdır. Tüm şirket kayıtlarında `is_ankara = TRUE` zorunlu olur; aksi kayıtlar `is_ankara = FALSE` olarak veritabanında durur ve MVP sorgularına dahil edilmez.

## V9 §17.2 — Faz 1 MVP Kapsamı (Ay 1-3)

V9 §17.2'de Faz 1 listesi:
- Signal ingestion, basic matching, B2B Findeks
- PostgreSQL + ChromaDB, EKAP + job posting scrapers
- 100 firm pilot

**V10 Uyarlaması:** ChromaDB, EKAP, B2B Findeks MVP dışı. Sadece:
- PostgreSQL şema + ingestion
- OSB üye listesi scraping
- 100 firma pilot

## MVP Kapsamı (Net)

### Coğrafya
- **Yalnız Ankara** (il kodu 06).
- `is_ankara = FALSE` olan kayıtlar `quarantine_firms` mantığıyla ayrı tabloda tutulur (V9 §11.2).

### Sektör
- **Yalnız OSB firmaları** (Organize Sanayi Bölgesi üyesi).
- OSB üyeliği doğrulanmamış firmalar `is_osb_member = FALSE` olarak işaretlenir, MVP dışı.
- NACE C (İmalat) zorunlu koşul değil ama filtreleme seçeneği olarak sunulur (master §9).

### Veri Kaynakları (V10/07_referanslar/01_veri_kaynagi_envanteri.md sırası)
1. OSTİM OSB (öncelik 1)
2. İvedik OSB
3. ASO 1. OSB
4. ASO 2-3 OSB
5. Başkent OSB
6. Diğer Ankara sanayi bölgeleri

### Tablolar
Aktif: `osbs`, `companies`, `company_locations`, `company_industries`, `sources`, `source_records`, `quarantine_firms`.
Pasif (Faz 2+): `evidence`, `company_events`, `commercial_signals`, `momentum_snapshot`, `company_state`, `entity_resolution`, `company_names`, `company_identifiers`, `company_contacts`, `company_products`, `products`, `product_categories`, `nace_codes`.

### Skorlar
- `data_quality_score`: Aktif (master §4).
- `entity_confidence`: Aktif (V9 §11).
- `b2b_findeks_score`, `topsis_score`, `digital_score`: Pasif (Faz 2+).

## V9'dan Alınan Çekirdek Prensipler

- **V9 §11 Evidence & Data Quality:** 9 boyut (Source Reliability, Freshness, Independence, Entity Resolution, Completeness, Contradiction, Evidence Type, Evidence Age, Direct vs Inferred).
- **V9 §15.1 Adversarial Test Framework:** 7 saldırı boyutu (data correctness, completeness, signal independence, causality, timing, generalization, decision impact).
- **V9 §20 Core Principle:** "Better commercial inferences from fragmented data, explicit about uncertainty."
- **V6 Prensibi:** "Unknown is allowed. Never invent missing commercial facts."

## V9'dan MVP Dışı (Faz 2+)

- ChromaDB vektör mimarisi (§3.3)
- Neo4j graf şeması (§3.4)
- Signal & Momentum System (§4)
- Commercial Change Engine (§5)
- Opportunity Engine + Three-Score System (§6)
- Customer Brain + Fit Calculation (§7)
- Decision Engine + Decision Matrix (§8)
- Portfolio Engine (§9)
- Learning Engine + Shadow Model + Calibration (§10)
- Monetization & Business Model (§12)
- AI Agent & Field Bridges (§13)
- Security & Compliance (mTLS, OAuth2, Zero-Knowledge) (§14)
- 100×100×100 Simulation (§15.2)

## Kabul Ölçütleri (V9 §18.2 metriklerinden MVP uyarlaması)

- Coverage: Ankara OSB firmalarının ≥%60'ı yakalanmış olmalı.
- Entity Accuracy: VKN eşleşmesi %95+.
- Duplicate Rate: ≤%3.
- Field Completeness: P0 alanları için ≥%80 doluluk.
- Freshness: OSB listesi ≤90 günlük.
