# ANKARA B2B INTELLIGENCE — MASTER CONTEXT V9
## Birleşik Tasarım: V6 Prensipleri + V7 Somut Altyapı + V8 Simülasyon Dersleri

Bağlantılar: [[README]] · [[01_sirket_master_ana_belgesi]] · [[01_v9_ile_karsilastirma]] · [[01_versiyon_6_baglam_dokumani]] · [[01_versiyon_7_baglam_dokumani]] · [[01_versiyon_8_baglam_dokumani]]

**Date:** 2026-08-28
**Status:** Birleşik Master Doküman — V6 Formatı + V7 İçeriği + V8 Öğrenmeleri
**Core Principle:**
> Do not pretend to know what the data cannot prove. Preserve uncertainty and make the strongest evidence-backed commercial inference possible.

---

## 1. PROJECT DEFINITION & IDENTITY

### 1.1 Platform Identity
**Platform Name:** Ankara B2B Commercial Intelligence & Smart Matching Terminal
**Target Audience:**
- OSTİM, Sincan ASO, İvedik OSB manufacturing SMEs
- Defense Industry Prime Contractors (Tier-1/2/3)
- B2B Service Providers (tooling, logistics, raw materials)

**Core Intelligence Pillars:**
1. **Production Reliability Score (B2B Findeks):** Manufacturing reputation coefficient derived from GİB e-invoice data, TOPSIS historical delivery performance, and Neo4j chained risk graphs. Range: 0-100, with evidence layers exposed.
2. **HS Code Import Substitution Engine:** Cross-references HS Code import data with ChromaDB capability vectors to identify local manufacturers before tender publication.
3. **Predictive Commercial Intent Engine:** Autonomously predicts company purchasing needs within 14 days using job postings, EKAP tender data, and raw material movement signals.
4. **Reputation-Based Non-Circumvention:** Freezes A+ Certified Supplier status, lowers B2B Findeks score, and revokes high-intent tender signals for companies attempting to bypass the platform.

### 1.2 Core Architecture: 6+1 Katman
```
Market Brain (Katman 1)
    ↓
Customer Brain (Katman 2)
    ↓
Opportunity Engine (Katman 3)
    ↓
Decision Engine (Katman 4)
    ↓
Portfolio Engine (Katman 5)
    ↓
Learning Engine (Katman 6)
    ↑
Evidence & Data Quality Layer (Katman 0) — Tüm katmanları saran
```

### 1.3 V6 ↔ V7 ↔ V9 Entegrasyon Prensibi [SSOT]
- **V6** = Beyin. Kavramsal mimari, adversarial testler, belirsizlik yönetimi.
- **V7** = Gövde. PostgreSQL + ChromaDB + Neo4j + Redis, TOPSIS, monetizasyon, saha köprüleri.
- **V8** = Dersler. 100×100×100 simülasyon, 5 kritik bulgu, 8 tutarlılık düzeltmesi.
- **V9** = Birleşik. V6'nın prensipleri + V7'nin teknolojisi + V8'in öğrenmeleri, tek tutarlı dokümanda.

**SSOT Kuralı:** PostgreSQL 16+ relational database is the Single Source of Truth. ChromaDB (vectors), Neo4j (graphs), and Redis (cache) are read-optimized projections of the SSOT. Malformed payloads are isolated within the `quarantine_firms` table.

---

## 2. DATA STRATEGY & SOURCES

### 2.1 Data Philosophy (V6 Prensibi Korunur)
> Do not make the product dependent on private CRM/ERP data. Prefer legally accessible external/public signals.

**Phase Strategy:**
| Phase | Timeline | Data Sources | ERP Dependency |
|-------|----------|--------------|----------------|
| **MVP (Faz 1)** | Ay 1-3 | Public tenders (EKAP), job postings, company registries, news | None. Opt-in only. |
| **Scale (Faz 2)** | Ay 4-9 | + Field verification, TOBB reports, GİB e-invoice (anonymized) | Light (read-only API) |
| **Enterprise (Faz 3)** | Ay 10+ | + Live ERP telemetry (Logo, CANIAS, SAP, MES) | Full bidirectional sync |

### 2.2 Data Sources (MVP → Scale)
| Priority | Source | VKN/Domain Bridge | Signal Type | Technology | Phase |
|----------|--------|-------------------|-------------|------------|-------|
| P0 | EKAP Public Tenders | KİKİK No → VKN | Procurement Intent | Web Scraper + API | MVP |
| P0 | Job Postings (LinkedIn, Kariyer.net) | Company name → VKN | Hiring/Expansion Signal | NLP + NER | MVP |
| P1 | GİB E-Invoice (anonymized) | VKN → Revenue trend | Financial Health | API Gateway | Scale |
| P1 | TOBB Capacity Reports | VKN → Machine list | Production Capability | OCR Parser | Scale |
| P2 | Enterprise ERP (Logo, CANIAS, SAP) | ERP ID → VKN | Real-time Capacity | mTLS + OAuth2 API | Enterprise |
| P2 | OSB Infrastructure Monitoring | Location → Grid status | Operational Availability | IoT Sensors | Enterprise |

### 2.3 Customer Input Minimization (V6 Prensibi)
- Customer input: **minimal, high value, optional where possible, privacy-conscious**
- WhatsApp Voice-to-Intent: Shop-floor managers send voice messages → STT → ChromaDB vector query → TOPSIS search
- No manual data entry for signal ingestion

---

## 3. TECHNOLOGY STACK & DATA ARCHITECTURE

### 3.1 Unified Hybrid Database Architecture
```
[Raw Data Sources] ──► [Pydantic Validation Gate]
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              [Valid Data]        [quarantine_firms]
                    │              (Analyst Review)
        ┌───────────┼───────────┐
        ▼           ▼           ▼
  [PostgreSQL]  [ChromaDB]   [Neo4j]
  (Relational)  (Vector)     (Graph)
  + PostGIS     1536-dim     Risk/Symbiosis
        │           │           │
        └───────────┼───────────┘
                    ▼
            [Redis Cache]
            (<300ms SLA)
```

### 3.2 PostgreSQL 16 + PostGIS Schema
```sql
-- Master Firm Model
CREATE TABLE firms (
    firm_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    tax_id VARCHAR(20) UNIQUE,
    osb_region VARCHAR(100) NOT NULL,
    location GEOMETRY(Point, 4326), -- PostGIS: Logistics distance calc
    nace_code VARCHAR(10) NOT NULL,
    employee_count INT DEFAULT 0,
    digital_score FLOAT DEFAULT 0.0,
    topsis_score FLOAT DEFAULT 0.0,
    b2b_findeks_score INT DEFAULT 50, -- Range: 0-100, evidence-backed
    is_verified_a_plus BOOLEAN DEFAULT FALSE,
    is_field_verified BOOLEAN DEFAULT FALSE, -- +0.05 TOPSIS bonus (V8: sınırlı)
    credit_balance INT DEFAULT 100, -- V7 Hybrid Credit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- V6 Quarantine Layer
CREATE TABLE quarantine_firms (
    quarantine_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_payload JSONB NOT NULL,
    error_reason TEXT NOT NULL,
    source_url VARCHAR(500),
    resolved_status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- V7 Business & Growth Signals
CREATE TABLE job_signals (
    signal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firm_id UUID REFERENCES firms(firm_id) ON DELETE CASCADE,
    position_title VARCHAR(255) NOT NULL,
    signal_type VARCHAR(50) NOT NULL, -- ERP_BUYING_INTENT, TOOLING_NEED, LOGISTICS
    posted_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 3.3 ChromaDB Vector Architecture
- **Dimension:** 1536-dim embeddings (OpenAI/text-embedding-3-large or equivalent)
- **Collections:** `capabilities`, `products`, `tender_specs`, `hs_code_mappings`
- **Metadata:** firm_id, nace_code, osb_region, verification_status, last_updated
- **Search:** Cosine similarity with metadata filters

### 3.4 Neo4j Graph Schema
- **Nodes:** Firm, Product, Tender, Machine, Location
- **Relationships:**
  - `(Firm)-[:SUPPLIES]->(Product)`
  - `(Firm)-[:RISKY_LINK {risk_score}]->(Firm)` — Supply chain risk propagation
  - `(Firm)-[:SYMBIOSIS {waste_type}]->(Firm)` — Industrial symbiosis (scrap, heat, chemicals)
  - `(Firm)-[:LOCATED_AT]->(Location)` — PostGIS distance queries

---

## 4. SIGNAL & MOMENTUM SYSTEM

### 4.1 V6 Signal Concepts (Korunur)
| Concept | Definition | V9 Implementation |
|---------|------------|-------------------|
| Signal Cluster | Co-occurring signals | ChromaDB metadata aggregation |
| Signal Velocity | Rate of signal generation | Time-series in PostgreSQL |
| Signal Acceleration | Change in velocity | Derivative calculation |
| Signal Independence | Unique evidence sources | Source deduplication + URL hash |
| Common Cause Detection | Single root, multiple signals | Graph pattern matching in Neo4j |
| Signal Contradiction | Conflicting signals | Contradiction flag + manual review queue |
| Missing Signal | Expected but not observed | Scheduled expectation checks |
| Expected Signal Not Observed | Failed prediction | Prediction Ledger entry |
| Company Baseline | Firm's own historical behavior | PostgreSQL time-series |
| Sector Baseline | Industry average | Aggregated PostgreSQL views |

### 4.2 Key Rules (V6 Prensibi)
- **Copied articles do not count as independent evidence.**
- **Missing ≠ negative.**
- **Unknown ≠ Lost.**
- **Momentum is not signal count;** it uses velocity, acceleration, recency, independence, baselines, contradictions, and causal relevance.

---

## 5. COMMERCIAL CHANGE ENGINE

### 5.1 Core Chain
```
Commercial Event → State Change → Causality → Need → Timing → Product/Supplier Opportunity
```

### 5.2 Event Taxonomy
| Event Type | Example | Signal Source |
|------------|---------|---------------|
| Positive | New factory, hiring surge, export growth | News, job postings, trade data |
| Negative | Layoffs, contract cancellation, cost pressure | News, financial signals |
| Mixed | Restructuring (cuts + invests) | Multiple sources |
| Stable | No significant change | Baseline comparison |

**Rule:** Negative events are not automatically penalties. Cost pressure may create demand for automation.

### 5.3 Need, Purchase Probability, Timing Probability
**These remain SEPARATE concepts in V9.**
- `Need Probability`: Evidence-backed likelihood of a genuine need
- `Purchase Probability`: Likelihood of purchase given need (requires more evidence)
- `Timing Probability`: Likelihood that now is the right time

---

## 6. OPPORTUNITY ENGINE

### 6.1 Opportunity Gates (V6 Prensibi Korunur + V8 Bulgu #5 Düzeltmesi)
```
Need → Product Fit → Commercial Opportunity → Evidence/Confidence → Timing
```

| Gate | Threshold | Action if Failed |
|------|-----------|------------------|
| Need Gate | need_prob ≥ 0.25 | max INVESTIGATE (V8 hard gate) |
| Fit Gate | fit_score ≥ 0.30 | MONITOR or DEPRIORITIZE |
| Evidence Gate | evidence_strength ≥ 0.20 | INVESTIGATE (gather more data) |
| Timing Gate | timing_score ≥ 0.30 | WAIT or REVISIT |

**V8 Dersi:** Need < 0.25 → max INVESTIGATE. CONTACT_NOW yasak.

### 6.2 Three-Score System (V6 Prensibi Geri Getirildi)
**V8'in tek skorlu Ensemble yaklaşımı V9'da ayrıştırıldı:**

| Score | Range | UI Label | Evidence Required |
|-------|-------|----------|-------------------|
| **Need Score** | 0.0 - 1.0 | "İhtiyaç Olasılığı" | Signal cluster, historical pattern |
| **Fit Score** | 0.0 - 1.0 | "Ürün Uyumu" | Capability match, certification, capacity |
| **Timing Score** | 0.0 - 1.0 | "Zamanlama" | Recency, seasonality, budget cycle |
| **Ensemble Score** | 0.0 - 1.0 | "Birleşik Skor" | Weighted combination (UI'da gösterilir) |

**V8 Dersi:** Fit skoru ayrı gösterilmelidir. Tek skor, fit'i gizleyerek yanıltıcı olabilir.

### 6.3 Ensemble Skorlama (V8 Yeniliği, V9'da Düzeltilmiş)
```python
def compute_ensemble_score(need, fit, timing, evidence, weights=None):
    # Default weights (V8 kalibrasyon sonrası)
    if weights is None:
        weights = {
            'need': 0.30,
            'fit': 0.35,   # V8: %20→%35 (Bulgu #3)
            'timing': 0.20,
            'evidence': 0.15
        }

    # Safety Net: Clamp + Normalize (Düzeltme D4)
    raw = (need * weights['need'] + 
           fit * weights['fit'] + 
           timing * weights['timing'] + 
           evidence * weights['evidence'])

    # Bonuslar sınırlı (V8 Bulgu #3)
    field_bonus = 0.05 if is_field_verified else 0.0  # V7: +0.20 → V9: +0.05
    signal_bonus = 0.03 if active_intent_10d else 0.0  # V7: +0.15 → V9: +0.03

    clamped = max(0.0, min(1.0, raw + field_bonus + signal_bonus))
    return clamped
```

### 6.4 Counterfactual Engine (V6 Prensibi + V8 Implementasyonu)
```python
def counterfactual_robustness(opportunity):
    signals = opportunity.signals
    base_score = opportunity.ensemble_score

    contributions = {}
    for signal in signals:
        score_without = compute_ensemble_without(signal)
        contribution = base_score - score_without
        contributions[signal.id] = contribution

    # Fragile detection (V8)
    max_contribution = max(contributions.values())
    if max_contribution > 0.40:  # Single signal dominates >40 points
        opportunity.is_fragile = True
        opportunity.max_action = "INVESTIGATE"  # CONTACT_NOW yasak

    return contributions
```

---

## 7. CUSTOMER BRAIN & FIT CALCULATION

### 7.1 Fit Calculation (V6 + V7 + V8 Birleşimi)
**V6 Prensibi:** `need ≠ automatic product fit`, `growth ≠ automatic need`

**V7 Implementasyonu:**
```
Final Score = C_i* + Field Verification Bonus + Signal Bonus
C_i* = S_i^- / (S_i^+ + S_i^-)
```

**V8 Düzeltmesi:** Bonuslar sınırlı, Fit ağırlığı artırıldı.

**V9 Yaklaşımı:**
| Component | Weight | Source |
|-----------|--------|--------|
| TOPSIS C_i* | 0.60 | AHP-weighted capability distance |
| Field Verification | 0.05 | On-site audit (V7: 0.20 → V9: 0.05) |
| Active Intent Signal | 0.03 | 10-day window (V7: 0.15 → V9: 0.03) |
| Evidence Strength | 0.32 | Independent source count, freshness |

### 7.2 Dynamic AHP Weight Matrix (V7 Özelliği, V9'da Korunur)
| Tender Type | w_cert | w_delivery | w_findeks | w_price | w_idle |
|-------------|--------|------------|-----------|---------|--------|
| Defense/Aerospace | 0.40 | 0.30 | 0.20 | 0.10 | — |
| Emergency Subcontract | — | 0.20 | — | 0.10 | 0.45 |
| Standard Procurement | 0.20 | 0.25 | 0.25 | 0.20 | 0.10 |

### 7.3 Rules
- `total company budget ≠ addressable budget`
- `white space ≠ demand`
- `unknown competitor ≠ no competitor`

---

## 8. DECISION ENGINE

### 8.1 Decision Matrix (V6 Esnekliği + V8 Hard Gate'leri)

| Need | Fit | Evidence | Timing | Recommended Action | Confidence |
|------|-----|----------|--------|-------------------|------------|
| < 0.25 | any | any | any | **INVESTIGATE** (hard gate) | Low |
| 0.25-0.50 | < 0.30 | any | any | MONITOR or DEPRIORITIZE | Low |
| 0.25-0.50 | ≥ 0.30 | < 0.20 | any | INVESTIGATE | Medium |
| 0.25-0.50 | ≥ 0.30 | ≥ 0.20 | < 0.30 | WAIT / REVISIT | Medium |
| 0.50-0.75 | ≥ 0.30 | ≥ 0.20 | ≥ 0.30 | CONTACT_NOW or INVESTIGATE | High |
| ≥ 0.75 | ≥ 0.50 | ≥ 0.40 | ≥ 0.50 | **CONTACT_NOW** | Very High |
| any | any | any | any + Contradiction | CLARIFY | Variable |
| any | any | any | any + Fragile | max INVESTIGATE | Low |

### 8.2 DEPRIORITIZE Levels (V8 Düzeltme D3)

**Level 1: Silent Deprioritize (System Only)**
- Trigger: evidence < 0.15 OR stale data > 90 days
- Action: Score drops, no user notification

**Level 2: User Warning (Visible)**
- Trigger: evidence 0.20-0.30 + contradiction detected, OR contraction signal + fit < 0.50
- Action: Red flag on opportunity card, user sees warning

### 8.3 Global Deduplication (V8 Bulgu #4 Düzeltmesi)
```sql
-- Same firm-product pair cannot be shown to multiple users simultaneously
SELECT firm_id, product_id, COUNT(DISTINCT user_id) AS dup_count
FROM opportunities
WHERE status = 'ACTIVE'
  AND created_at > NOW() - INTERVAL '7 days'
GROUP BY firm_id, product_id
HAVING COUNT(DISTINCT user_id) > 1;
```

**Reservation System:**
- User A sees Opportunity X → 24-hour reservation
- User B cannot see same opportunity until reservation expires or User A dismisses

### 8.4 Contact Limits (V8 B2 Seçeneği Riski Giderme)
- Max 1 contact/hour/firm (not 3/day — hourly is less intrusive)
- Max 3 contacts/day/firm (hard ceiling)
- Account Opportunity Map prevents multiple product pressure

### 8.5 Buyer/Decision-Maker Rule (V6 Prensibi Korunur)
> If the buyer/decision-maker cannot be found, do not invent one. Use company-level validation.

**V9 Enhancement:** Neo4j graph query for decision-maker detection:
```cypher
MATCH (f:Firm {firm_id: $id})-[:HAS_CONTACT]->(c:Contact)
WHERE c.role CONTAINS 'Satın Alma' OR c.role CONTAINS 'Genel Müdür'
RETURN c.name, c.role, c.verified
ORDER BY c.verified DESC, c.last_contact DESC
LIMIT 3;
```

---

## 9. PORTFOLIO ENGINE

### 9.1 Portfolio Optimization (V6 Farklılaştırıcısı + V8 Düzeltmeleri)

**Problem:** 10,000 company-product matches exist while sales team can work only 20.

**V9 Formula (Düzeltme D6 Uygulandı — Fit tekrarı giderildi):**
```python
def portfolio_score(opp, sales_capacity, strategic_value=1.0):
    # V8 Dersi: Portfolio'da FIT_SCORE ayrı hesaplanmaz,
    # Ensemble skor zaten fit'i içerir. Ayrı fit ekleme = double counting.

    ecv = opp.expected_value * opp.win_probability
    time_to_cash = opp.estimated_close_days / 30  # months
    effort = opp.sales_effort_hours
    complexity = opp.deal_complexity  # 1-5

    # Resource conflict penalty
    conflict_penalty = 0.0
    if opp.firm_id in currently_pursued_firms:
        conflict_penalty = 0.15

    # Cannibalization penalty
    cannibal_penalty = 0.0
    if opp.product_category in recently_sold_categories:
        cannibal_penalty = 0.10

    score = (ecv * 0.40 + 
             (1/time_to_cash) * 0.20 + 
             opp.evidence_strength * 0.20 + 
             strategic_value * 0.10 + 
             (1/complexity) * 0.10 - 
             conflict_penalty - 
             cannibal_penalty)

    return max(0.0, score)
```

### 9.2 Account Opportunity Map
```sql
-- Prevent multiple product opportunities causing excessive contact pressure
SELECT firm_id, 
       COUNT(*) AS opp_count,
       MAX(timing_score) AS max_timing,
       SUM(expected_value) AS total_ev
FROM opportunities
WHERE status IN ('ACTIVE', 'CONTACT_NOW')
GROUP BY firm_id
HAVING COUNT(*) > 1;
```

### 9.3 Human Override
> Human Override is allowed, but human preference is not objective evidence.

**V9 Enhancement:** Override logged with reason, outcome tracked separately for learning.

---

## 10. LEARNING ENGINE

### 10.1 Learning Loop
```
Signal → Prediction → Opportunity → Action → Reaction → Outcome → Learning → Validation → Model Improvement
```

### 10.2 Components
| Component | V6 Definition | V9 Implementation |
|-----------|---------------|-------------------|
| Prediction Ledger | Store each prediction with timestamp, evidence, unknowns | PostgreSQL table + JSONB evidence blob |
| Outcome Ledger | Verified Won, Reported Won, Verified Lost, etc. | PostgreSQL with verification evidence links |
| Feedback Engine | Minimize data entry (👍/👎) | WhatsApp quick-reply + implicit feedback (opened, saved, contacted) |
| Signal Quality | Track source reliability over time | Per-source accuracy score in PostgreSQL |
| Prediction Error | Classify errors (wrong company, need, timing, etc.) | Automated error classification + analyst review queue |
| Pattern Discovery | Find signal combinations that predict outcomes | Neo4j graph pattern mining |
| Pattern Memory | Store validated patterns | PostgreSQL + Redis cache |
| Shadow Model | Run new models beside production | A/B test framework (Düzeltme D1) |
| Validation | Statistical significance checks | Minimum sample thresholds per pattern |
| Model Drift Detection | Monitor prediction error over time | Monthly drift reports |

### 10.3 Shadow Model — Security Valve + A/B Test Motoru (Düzeltme D1)

**Architecture:**
```
[Production Model] ←── 100% traffic (decisions)
       ↑
[Shadow Model] ←── 20% traffic (read-only predictions)
       ↓
[Comparison Engine] ←── Weekly: prediction quality, false pos/neg, timing accuracy
       ↓
[Promotion Gate] ←── Shadow > Production + 5% AND stable for 4 weeks
```

**Promotion Criteria:**
- Shadow performance > Current performance × 1.05
- Stable for minimum 4 weeks
- No catastrophic hallucinations in shadow period
- Analyst approval

### 10.4 Calibration Engine (V8 Bulgu #1 Düzeltmesi + Düzeltme D5)

**Problem:** High-scored opportunities were not more successful (WON avg: 0.598 vs Error avg: 0.610)

**V9 Solution — 3-Phase Calibration:**

| Phase | Period | Learning Weight | Method |
|-------|--------|-----------------|--------|
| **Cold Start** | Month 1-3 | 0% (static) | Pre-calibrated weights from V8 simulation |
| **Shadow Learning** | Month 4-6 | 20% | Shadow model tests new weights on 20% traffic |
| **Auto-Calibration** | Month 7+ | 100% | Monthly Spearman correlation → weight update |

```python
def monthly_calibration():
    outcomes = fetch_last_month_outcomes()

    correlations = {
        'fit': spearman(outcomes.fit, outcomes.won),
        'need_prob': spearman(outcomes.need_prob, outcomes.won),
        'evidence': spearman(outcomes.evidence, outcomes.won),
        'timing': spearman(outcomes.timing, outcomes.won)
    }

    total_corr = sum(abs(c) for c in correlations.values())
    new_weights = {k: abs(v)/total_corr for k, v in correlations.items()}

    # Shadow test
    shadow_perf = test_shadow_model(new_weights)
    current_perf = test_current_model()

    if shadow_perf > current_perf * 1.05:
        promote_to_production(new_weights)
        log_calibration_event(old_weights, new_weights, shadow_perf)
    else:
        keep_current_weights()
        alert_data_science_team(shadow_perf, current_perf)
```

### 10.5 Learning Safety Rules (V6'nın 10 Kuralı Korunur)
1. Unknown is allowed.
2. Never invent missing commercial facts.
3. Feedback ≠ verified outcome.
4. Correlation ≠ causality.
5. Copied sources ≠ independent evidence.
6. Missing ≠ negative.
7. One customer must not define a global pattern.
8. Old patterns must be monitored for drift.
9. Production weights do not change simply because a new pattern was discovered.
10. New models must pass shadow validation.

### 10.6 Minimum Sample Threshold
| Stage | Min Samples | Min Success Rate | Stability Period |
|-------|-------------|------------------|------------------|
| Candidate | N ≥ 5 | > 0.60 | 2 weeks |
| Shadow | N ≥ 20 | > 0.65 | 4 weeks |
| Validated | N ≥ 50 | > 0.70 | 8 weeks |
| Production | N ≥ 100 | > 0.75 | Ongoing monitoring |

---

## 11. EVIDENCE & DATA QUALITY LAYER

### 11.1 Dimensions (V6'nın 9 Boyutu + V7 Pydantic Gate)
| Dimension | V6 Definition | V9 Implementation | Failure Handling |
|-----------|---------------|-------------------|------------------|
| Source Reliability | Per-source track record | PostgreSQL accuracy score | Weight reduction |
| Freshness | Age of evidence | Timestamp + half-life decay | Stale flag |
| Independence | Unique evidence sources | URL hash + source dedup | Merge/penalty |
| Entity Resolution | Confidence in firm match | VKN/Domain bridge + fuzzy | Quarantine |
| Completeness | Missing fields | Pydantic validation | Quarantine |
| Contradiction | Conflicting signals | Neo4j contradiction graph | Manual review |
| Evidence Type | Direct vs inferred | Tagging system | Confidence adjustment |
| Evidence Age | Time since observation | Auto-stale after 90 days | Deprioritize |
| Direct vs Inferred | Primary vs secondary | Source classification | Weight adjustment |

### 11.2 Quarantine Pipeline
```
[Raw Data] → [Pydantic Validation Gate] → [Valid] → PostgreSQL/ChromaDB/Neo4j
                                    ↓
                              [quarantine_firms]
                                    ↓
                              [Analyst Review]
                                    ↓
                              [Resolved/Rejected]
```

---

## 12. MONETIZATION & BUSINESS MODEL

### 12.1 Revenue Streams (V7 Modeli, V9'da Açıkça Entegre)

| Revenue Item | Price | Credits/Access | Included Features |
|--------------|-------|----------------|-------------------|
| **B2B Industrial Terminal** | 85,000 TRY/year | 100 Contact Credits | Core Search, TOPSIS Hot Radar, B2B Findeks Scorecard |
| **Strategic Intelligence** | 220,000 TRY/year | 500 Contact Credits | + Idle Capacity Radar, HS Code Import Substitution, Incentive Engine |
| **Enterprise (Prime Contractor)** | 650,000 TRY+/year | Unlimited API + C-Level Access | + Neo4j Graph Risk, Bi-directional ERP/MES API Gateway |
| **Credit Pack (Pay-per-Match)** | 750 TRY / 50 Credits | Additional usage | Unlocks extended contact details |
| **Emergency RFQ Fee** | 2,500 TRY / RFQ | 1 Emergency Tender | Direct push to A+ suppliers |
| **Verified Supplier Badge** | 35,000 TRY/year | Field expertise audit | A+ status, +0.05 TOPSIS bonus (V8: sınırlı) |
| **Hot Sales Lead Sale** | 12,500 TRY / Lead | Verified signal | Qualified leads for vendors |
| **Success Fee (Commission)** | 2% - 4% of volume | Contractual | Commission on closed subcontracting volume |

### 12.2 PLG Findeks Hook (V7 Özelliği)
- Self-service tool: Any firm can query their own B2B Findeks score for free
- Viral growth mechanism: "Check your manufacturing reputation"
- Limited to self-score; competitor scores require subscription

### 12.3 Freemium Alignment with V6 "Minimal Input"
- **Free tier:** Hot Radar (anonim), B2B Findeks self-query, basic search
- **Paid tier:** Contact credits, API access, verified badge
- **Enterprise:** Full ERP integration, unlimited API, dedicated support

---

## 13. AI AGENT & FIELD BRIDGES

### 13.1 AI Agent System Prompt (V7'den Geri Getirildi)

```
YOU ARE: The Senior Field & Commercial Intelligence Agent of the 
Ankara B2B Commercial Intelligence Terminal.

CORE DUTIES:
1. Instantly analyze user B2B search queries and technical RFQs to deliver 
   concise, actionable matching results.
2. Address concerns and handle objections from traditional industrial business 
   owners hesitating to adopt the platform.

TONE: Never use abstract AI terminology (RAG, LLM, Vector Embeddings). 
Speak standard industrial language: "Hot Sales Radar", "Idle Capacity", 
"B2B Findeks", "RFQ Fee".

OUTPUT STRUCTURE: Jump straight to structured tables, code, or bulleted 
actions without meta-introductions or conversational filler.
```

### 13.2 Objection Handling Protocol (V7'den Geri Getirildi)

| Objection | Response |
|-----------|----------|
| **Price** | "We don't sell software; we fill your idle machine hours. A single subcontracting job secured through the platform completely covers the annual subscription cost." |
| **Privacy / Data Leak** | "Your company identity remains hidden without explicit consent. Listings are fully anonymized (e.g., 'AS9100 Certified Workshop in Sincan OSB')." |
| **Complexity** | "No training required. Simply message via WhatsApp as if texting your shop manager: 'Need a 5-axis CNC with open capacity in OSTİM'." |
| **Data Freshness** | "This is not a static directory. We operate as an active intelligence terminal processing real-time public tenders, hiring signals, and live ERP data streams." |

### 13.3 Field Bridges

| Bridge | Input | Output | Technology |
|--------|-------|--------|------------|
| **WhatsApp Voice-to-Intent** | Voice message from shop floor | Structured ChromaDB query + TOPSIS results | Speech-to-Text + NLP |
| **TOBB Capacity Report OCR** | Official TOBB PDF | Machine counts, power, tonnage | OCR + Pydantic validation |
| **Digital Dispute & Arbitration** | Quality/tolerance dispute | Findeks score held in escrow until resolution | Workflow engine |
| **OSB Grid Monitoring** | Regional power maintenance | Factory status = "Under Maintenance", RFQs rerouted | IoT sensors + Redis Pub/Sub |

---

## 14. SECURITY & COMPLIANCE

### 14.1 Security Matrix
| Feature | Implementation | Standard |
|---------|---------------|----------|
| Zero-Knowledge STEP/CAD Encryption | Encrypt at rest; dynamic watermarks on download | ISO 27001 |
| mTLS + OAuth2 API Gateway | All ERP connections encrypted + authenticated | OAuth2 RFC 6749 |
| Data Protection & Consent Shield | İYS (Communication Management System) permission check | KVKK compliant |
| Latency SLA | <300ms via Redis Warm Cache | Internal SLA |

### 14.2 Anonymity Architecture (V6 + V7 + V8 D2 Birleşimi)
```
Phase 1: Anonymous Discovery
  User sees: "AS9100 Certified Workshop in Sincan OSB"
  Data: Capability vectors, B2B Findeks range (not exact score)

Phase 2: Identity Reveal (upon explicit consent or credit spend)
  User sees: Full company name, contact details, exact Findeks
  Data: Complete profile, historical performance
```

---

## 15. TEST FRAMEWORK

### 15.1 Adversarial Test Framework (V6 V2 + V8 Simülasyon Birleşimi)

**Every test attacks:**
1. Data correctness
2. Data completeness
3. Signal independence
4. Causality
5. Timing
6. Generalization
7. Decision impact

**Test Results:**
- 🟢 PASSED
- 🔴 FAILED
- 🟠 ALGORITHM MUST CHANGE
- 🔵 ASK / INFORMATION MISSING

### 15.2 100×100×100 Simulation (V8 Dersleri)

**Scenario:** 100 Firms × 100 Products × 100 Users, 646 signals, 10,000 potential matches

**5 Critical Findings & Fixes:**

| # | Finding | Risk | V9 Fix |
|---|---------|------|--------|
| 1 | High-scored ops not more successful (WON: 0.598 vs Error: 0.610) | TOPSIS doesn't predict sales success | 3-Phase Calibration + Ensemble scoring |
| 2 | Error rate 48.2% (NO_RESPONSE 22%, LOST 22%, WRONG_TIMING 15%) | System doesn't self-calibrate | Outcome Ledger + Feedback Engine + Shadow Model |
| 3 | Fit score misleading (fit: 0.319, score: 0.793) | Fit weight too low, bonuses dominant | Fit weight 20%→35%, bonuses capped, 3-score UI |
| 4 | Same firm-product duplication | Multiple users see same opportunity | Global deduplication + 24h reservation system |
| 5 | Low need → CONTACT_NOW (need: 0.15) | Gates too loose | Need < 0.25 → max INVESTIGATE hard gate |

### 15.3 Regression Testing Rule
> When a rule changes, regression-test previous scenarios.

### 15.4 Major Test Scenarios (V6'nın 26 Senaryosu + V8 Bulguları)
- Copied news masquerading as multiple signals
- Growth without relevant product need
- Strong need but company contraction
- Total budget mistaken for addressable budget
- Unavailable/stale price benchmark
- Wrong product mapping
- Unknown competitor/decision-maker/location
- Large nominal opportunity with low win probability
- Small opportunity with high evidence and fast time-to-cash
- Same company with multiple product opportunities
- Same product across hundreds of companies
- Scarce sales/technical resources
- Account contact pressure
- Cannibalizing opportunities
- Poisoned CRM data
- False Won/Lost records
- Misleading human feedback
- Small-sample overfitting
- Sector pattern transfer errors
- Common-cause signals
- Model drift
- White-space traps
- Missing signals
- Contradictory commercial states
- **NEW (V8):** Fragile opportunity (single signal dominates)
- **NEW (V8):** Global deduplication failure
- **NEW (V8):** Calibration cold-start

---

## 16. UI/UX: HOW HUMANS SEE SCORES

### 16.1 Opportunity Card (Identity Revealed)
```
┌─────────────────────────────────────────────────────────────┐
│  FIRSAT KARTI — Özdemir Lazer Makina San. Tic. Ltd. Şti.  │
├─────────────────────────────────────────────────────────────┤
│  🏭 Firma: Özdemir Lazer (OSTİM, Bölge 3)                 │
│  📊 B2B Findeks: 78/100  [GİB ✅, TOPSIS ✅, Field ⚠️]    │
│                                                             │
│  İHTİYAÇ: 5 Eksen CNC İşleme (Helikopter Parçası)         │
│  ├─ İhtiyaç Olasılığı:    72%  ████████░░                 │
│  ├─ Ürün Uyumu:           65%  ██████▌░░░                 │
│  ├─ Zamanlama:            58%  █████▊░░░░                 │
│  └─ Birleşik Skor:        68%  ██████▊░░░                 │
│                                                             │
│  🔍 Kanıt:                                                │
│  • İş ilanı: "5 Eksen CNC Operatörü" (14 gün önce)       │
│  • EKAP İhale: Helikopter parçası işlenmesi (7 gün önce)  │
│  • İhracat artışı: %23 (son çeyrek)                       │
│                                                             │
│  ⚠️ Bilinmeyenler:                                        │
│  • Bütçe: Belirtilmemiş                                   │
│  • Karar verici: Bilinmiyor (firma düzeyi doğrulama)     │
│  • Rakip sayısı: Bilinmiyor                               │
│                                                             │
│  🎯 Önerilen Aksiyon: CONTACT_NOW                         │
│  📅 Son Güncelleme: 2 saat önce                           │
└─────────────────────────────────────────────────────────────┘
```

### 16.2 Dashboard View
```
┌─────────────────────────────────────────────────────────────┐
│  PORTFÖY DASHBOARD — Bu Hafta (20/20 fırsat)              │
├─────────────────────────────────────────────────────────────┤
│  CONTACT_NOW:  5  │  INVESTIGATE:  8  │  MONITOR:  7     │
├─────────────────────────────────────────────────────────────┤
│  Skor Dağılımı: 0.45 - 0.89 (çeşitlilik: iyi)            │
│  Ortalama Kanıt: 0.62 │ Ortalama İhtiyaç: 0.58            │
│  Kullanıcı Başı: 3.2 fırsat (hedef: <5)                  │
├─────────────────────────────────────────────────────────────┤
│  ⚠️ Uyarılar:                                             │
│  • 2 fırsat FRAGILE (tek sinyal baskın)                   │
│  • 1 firma 3+ contact (limit aşımı riski)                │
│  • Kalibrasyon: Faz 2'de (gölge model aktif)            │
└─────────────────────────────────────────────────────────────┘
```

### 16.3 WhatsApp Agent View
```
📱 WhatsApp Mesajı:

Özdemir Lazer - 5 Eksen CNC
İhtiyaç: 78% | Zamanlama: 64%
Kanıt: İş ilanı + EKAP ihale
Öneri: Şimdi Ara
[Detaylar] [Sonra Hatırlat] [Yoksay]
```

---

## 17. GO-TO-MARKET & MVP ROADMAP

### 17.1 Initial Beachhead
**OSTİM / Ankara**
- Dense B2B ecosystem, SMEs, manufacturing/supplier relationships
- Manageable geographic scope, potential network effects

**Expansion Path:**
```
OSTİM → Ankara OSBs → Ankara → Türkiye → International
```

### 17.2 Three-Phase Roadmap

| Phase | Timeline | Focus | Key Deliverables |
|-------|----------|-------|------------------|
| **Faz 1: MVP** | Ay 1-3 | Signal ingestion, basic matching, B2B Findeks | PostgreSQL + ChromaDB, EKAP + job posting scrapers, 100 firms pilot |
| **Faz 2: Scale** | Ay 4-9 | Learning engine, portfolio optimization, field bridges | Shadow model, WhatsApp agent, TOBB OCR, 1,000 firms |
| **Faz 3: Enterprise** | Ay 10+ | ERP integration, full automation, national expansion | Neo4j graph, bidirectional ERP API, HS Code engine, 10,000 firms |

### 17.3 Startup Category
**Not:** Lead database, news monitoring, generic CRM, or generic AI sales assistant.

**Is:** B2B Commercial Intelligence / Opportunity Intelligence / Decision Intelligence

**Core Differentiation:** Convert fragmented external commercial signals into evidence-backed company state changes, needs, timing, product opportunities, and resource-aware actions — then learn from actual outcomes.

---

## 18. OPEN PROBLEMS & NEXT PHASE

### 18.1 Key Open Problems (V6'nın 21 Maddesi + V8'in 4 Yeni Maddesi)

| # | Problem | Category | Priority |
|---|---------|----------|----------|
| 1 | Final event taxonomy | Signal | High |
| 2 | Graph + relational data model sync | Architecture | High |
| 3 | Signal weighting auto-calibration | Algorithm | High |
| 4 | Counterfactual implementation at scale | Performance | Medium |
| 5 | Common-cause detection automation | Algorithm | High |
| 6 | Momentum mathematical formulation | Algorithm | High |
| 7 | Timing model (seasonal, sectoral, firm-specific) | Algorithm | High |
| 8 | Confidence calibration without sufficient outcomes | Statistics | High |
| 9 | Portfolio optimization with non-linear constraints | Algorithm | Medium |
| 10 | Outcome verification (invoice, PO, contract, delivery) | Operations | High |
| 11 | Entity resolution at scale (VKN matching accuracy) | Data | High |
| 12 | Source reliability cold-start | Algorithm | Medium |
| 13 | Pricing/value estimation without hallucination | AI Safety | Critical |
| 14 | Privacy/legal boundaries (KVKK, e-invoice, scraping) | Legal | Critical |
| 15 | MVP scope — first 90 days features | Product | Critical |
| 16 | Minimum data for useful predictions | Statistics | High |
| 17 | Benchmark methodology standardization | Testing | Medium |
| 18 | Go-to-market and onboarding friction | GTM | High |
| 19 | Churn prediction (V7 monetization + V6 Learning) | Analytics | Medium |
| 20 | Multi-language NLP (Turkish technical terms) | NLP | Medium |
| 21 | Ensemble convergence — when do 3 models agree/diverge? | **NEW (V8)** | Medium |
| 22 | Calibration frequency — weekly? monthly? | **NEW (V8)** | Medium |
| 23 | Deduplication fairness — small users excluded? | **NEW (V8)** | Low |
| 24 | Shadow Model maintenance cost optimization | **NEW (V8)** | Low |
| 25 | Anonymous profile conversion rate | **NEW (V8)** | Medium |

### 18.2 Benchmark Concept
**V9 Benchmark:** 100 companies × 100 products × realistic outcomes × limited sales capacity × clean and poisoned data × sector variation × missing information × timing variation × counterfactual scenarios × common-cause scenarios × model drift

**Metrics:**
- Prediction quality (Precision, Recall, F1)
- False positive rate
- False negative rate
- Timing accuracy (MAE in days)
- Evidence calibration (Brier score)
- Ranking quality (NDCG)
- Resource allocation quality (ECV realization)
- Catastrophic hallucination rate
- Robustness and recovery after bad data

---

## 19. HANDOFF RULES FOR ANOTHER AI

Treat this document as the current design state, not a finished specification.

When improving it:
1. Preserve accepted principles unless strong evidence shows a flaw.
2. Criticize assumptions.
3. Propose alternatives before changing core architecture.
4. Stress-test every major algorithmic change.
5. Never invent data availability.
6. Label assumptions, unknowns, and evidence.
7. Prefer useful simplicity over unnecessary complexity.
8. For every score, explain what decision it changes.
9. For every data field, explain how it can realistically be collected.
10. For every learning rule, explain how it can fail and how it will be tested.
11. Regression-test old scenarios after changes.
12. Keep the customer-facing product simpler than the internal intelligence layer.

---

## 20. CORE PRINCIPLE

> The goal is not to find more data. The goal is to make better commercial inferences from fragmented data while being explicit about uncertainty.

**V9 Fusion:** More data (V7's infrastructure) + better inference (V6's intelligence) + transparent uncertainty (both versions' principle) + **simulation-validated fixes** + **document consistency** = **Evidence-backed, learning, scalable, consistent B2B Commercial Intelligence.**

---

**END — MASTER CONTEXT V9**
