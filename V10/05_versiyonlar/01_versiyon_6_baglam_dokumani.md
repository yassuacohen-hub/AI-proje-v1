# Ankara B2B Intelligence — MASTER CONTEXT
## V6 — Current Architecture, Algorithms, Principles & Testing Context
Date: 2026-08-27

Bağlantılar: [[README]] · [[01_sirket_master_ana_belgesi]] · [[01_v9_ile_karsilastirma]]

## 1. Project Definition
A B2B Commercial Intelligence SaaS that observes legally accessible public/commercial signals, detects company state changes, infers evidence-backed needs and timing, matches those needs to a customer's products, recommends actions under limited sales capacity, and learns from real outcomes.

Core principle:
> Do not pretend to know what the data cannot prove. Preserve uncertainty and make the strongest evidence-backed commercial inference possible.

Initial beachhead: OSTİM / Ankara. The product is not permanently limited to industry.

## 2. Core Architecture

Market Brain
→ Customer Brain
→ Opportunity Engine
→ Decision Engine
→ Portfolio Engine
→ Learning Engine

Across all layers:
Evidence & Data Quality Layer

### Market Brain
“What is happening in companies and the market?”
Observes investments, hiring, expansion, contraction, exports, projects, procurement signals, financing, restructuring, contracts, public announcements and other commercial events.

### Customer Brain
“For this customer, which companies and products represent genuinely sellable opportunities?”
Evaluates product fit, addressable need, timing, evidence, commercial compatibility and sales context.

The two converge into opportunity and decision intelligence.

## 3. Commercial Change Engine
Tracks:
- positive events
- negative events
- mixed states
- stable states

Negative events are not automatically penalties. Example: cost pressure may create demand for automation.

Core chain:
Commercial Event → State Change → Causality → Need → Timing → Product/Supplier Opportunity

Need, Purchase Probability and Timing Probability remain separate concepts.

## 4. Signal & Momentum System
Important concepts:
- Signal Cluster
- Signal Velocity
- Signal Acceleration
- Signal Independence
- Common Cause Detection
- Signal Contradiction
- Missing Signal
- Expected Signal Not Observed
- Company Baseline
- Sector Baseline

Copied articles do not count as independent evidence.

Missing ≠ negative.
Unknown ≠ Lost.

Momentum is not signal count; it uses velocity, acceleration, recency, independence, baselines, contradictions and causal relevance.

## 5. Company / Sector Baselines
Compare:
1. company against its own historical behavior
2. company against its sector
3. company against peers/company type

Example: hiring from 2/month to 18/month is a major company change even if sector average is 20.

## 6. Opportunity Engine
A company-product match is not automatically an opportunity.

Required conceptual gates:
Need → Product Fit → Commercial Opportunity → Evidence/Confidence → Timing

Rules:
- growth ≠ automatic need
- need ≠ automatic product fit
- total company budget ≠ addressable budget
- white space ≠ demand
- unknown competitor ≠ no competitor

## 7. Customer-Facing Scores
Keep the UI understandable. Core scores:
- Need Probability
- Timing
- Fit
- Momentum
- Evidence Strength

Do not expose false precision. If price, budget, decision-maker or win probability is not evidenced, show Unknown / not estimated.

## 8. Opportunity Card
Should answer:
- Why this company?
- What changed?
- What need is inferred?
- Why this product?
- Why now?
- Evidence
- Evidence strength
- What is unknown?
- Recommended next action
- contradictions/risks where useful

Never invent budget, price, decision-maker, decision location, competitor absence or purchase status.

## 9. Need Publishing
Two modes:
- Private Need
- Supplier Network Need

This reduces fear of exposing sensitive commercial intent and reduces required manual entry.

## 10. Decision Engine
Question:
“What should the team do next?”

Actions can include:
- contact now
- monitor
- investigate
- clarify
- wait
- revisit later
- account-level validation
- deprioritize

If the buyer/decision-maker cannot be found, do not invent one. Use company-level validation.

## 11. Portfolio Engine
Major differentiator.

Problem:
10,000 company-product matches may exist while the sales team can work only 20.

Portfolio Engine allocates scarce resources using:
- Expected Commercial Value
- evidence confidence
- win probability when sufficiently evidenced
- timing
- time-to-cash
- strategic value
- sales effort
- deal complexity
- resource conflicts
- opportunity cannibalization
- evidence-backed expansion value

Highest score is not automatically the best opportunity.

Account Opportunity Map prevents multiple product opportunities in one company from causing excessive contact pressure.

Human Override is allowed, but human preference is not objective evidence.

## 12. Learning Engine
Purpose:
Learn which signals, combinations, contexts, products, sectors and timing patterns actually lead to outcomes.

Components:
- Prediction Ledger
- Outcome Ledger
- Feedback Engine
- Signal Quality
- Prediction Error
- Pattern Discovery
- Pattern Memory
- Shadow Model
- Validation
- Model Drift Detection

Loop:
Signal → Prediction → Opportunity → Action → Reaction → Outcome → Learning → Validation → Model improvement

## 13. Prediction Ledger
Store each material prediction with timestamp, evidence and unknowns.

Later compare prediction with reality.

Errors must be classified:
- wrong company
- wrong need
- wrong timing
- wrong product
- wrong budget assumption
- wrong purchase probability
- stale data
- signal interpretation error
- common-cause error
- missing information

## 14. Outcome Ledger
Outcome states:
- Verified Won
- Reported Won
- Verified Lost
- Reported Lost
- Delayed
- Unknown

Human feedback is not a verified commercial outcome.

Possible verification evidence:
invoice, PO, contract, delivery, payment, customer confirmation, reliable public evidence.

Unknown never becomes Lost automatically.

## 15. Feedback Engine
Minimize customer data entry.

Example:
“Is this opportunity correct?”
👍 Yes / 👎 No

If No:
- need wrong
- timing wrong
- product wrong
- company wrong
- budget unsuitable
- other

Implicit feedback may include opened, saved, contacted, ignored, revisited and dismissed.

Real outcomes have the strongest learning weight.

## 16. Learning Safety Rules
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

Learning scopes:
Global / Sector / Subsector / Company Type / Customer-Specific

## 17. Minimum Sample Threshold
A pattern with 8 successes out of 8 is not automatically a production rule.

Lifecycle:
Candidate → Shadow → Validated → Production

Promotion requires sufficient examples, evidence, stability and validation.

## 18. Common Cause Detection
If:
new factory + hiring + machine investment
all originate from one government incentive, they are not three independent signals.

Common causes prevent artificial momentum.

## 19. Counterfactual Engine
Ask:
“If this signal were removed, would the opportunity still exist?”

Example:
Factory + Hiring + Investment + RFQ = 91
Remove RFQ = 54
Remove Hiring = 73
Remove Investment = 80

This measures signal contribution/robustness. It is not by itself proof of causality.

## 20. Negative Evidence
Learn not only what happened, but what was expected and not observed.

Example:
Factory expansion predicts machinery procurement; months pass with no relevant signal.

Record:
Expected Signal Not Observed.

Do not claim the company definitely did not buy machinery.

## 21. Evidence & Data Quality Layer
Dimensions:
- source reliability
- freshness
- independence
- entity resolution confidence
- completeness
- contradiction
- evidence type
- evidence age
- direct vs inferred information

Poor evidence reduces confidence.

## 22. Model Drift
A pattern can change over time.

Monitor:
- prediction error over time
- pattern stability
- sector changes
- source changes
- outcome distribution

Recent evidence can matter more, but history is not blindly deleted.

## 23. Shadow Model
Significant algorithm changes first run beside the production model.

Compare:
Old Model vs New Model

Metrics:
- prediction quality
- false positives
- false negatives
- timing accuracy
- ranking quality
- decision impact
- robustness

Promote only if the new model provides meaningful improvement.

## 24. Decision Impact
Not every error has equal business risk.

Severity:
1 = trivial
2 = low
3 = medium
4 = high
5 = critical

Error types:
- False Positive
- False Negative
- Timing Error
- Causality Error
- Evidence Error
- Data Quality Error
- Ranking Error
- Resource Allocation Error

Catastrophic failures:
- invented budget
- invented price
- invented decision-maker
- invented purchase decision
- invented competitor absence

## 25. Adversarial Test Framework V2
Every test attacks:
1. data correctness
2. data completeness
3. signal independence
4. causality
5. timing
6. generalization
7. decision impact

Results:
- 🟢 GEÇTİ
- 🔴 KALDI
- 🟠 ALGORİTMA DEĞİŞMELİ
- 🔵 ASK / BİLGİ EKSİK

When a rule changes, regression-test previous scenarios.

## 26. Major Tests Already Considered
- copied news masquerading as multiple signals
- growth without relevant product need
- strong need but company contraction
- total budget mistaken for addressable budget
- unavailable price benchmark
- stale price benchmark
- wrong product mapping
- unknown competitor
- unknown decision-maker
- unknown decision location
- large nominal opportunity with low win probability
- small opportunity with high evidence and fast time-to-cash
- same company with multiple product opportunities
- same product across hundreds of companies
- scarce sales/technical resources
- account contact pressure
- cannibalizing opportunities
- poisoned CRM data
- false Won/Lost records
- misleading human feedback
- small-sample overfitting
- sector pattern transfer errors
- common-cause signals
- model drift
- white-space traps
- missing signals
- contradictory commercial states

## 27. 100×100 Portfolio Concept
Target benchmark:
100 companies × 100 products = 10,000 potential matches.

The system must distinguish:
10,000 matches
from
actual opportunities
from
priority opportunities.

Portfolio Engine should choose where scarce sales resources produce the greatest expected commercial result.

## 28. Startup Category
The project has evolved beyond:
- lead database
- news monitoring
- generic CRM
- generic AI sales assistant

Intended category:
B2B Commercial Intelligence / Opportunity Intelligence / Decision Intelligence

Core differentiation:
Convert fragmented external commercial signals into evidence-backed company state changes, needs, timing, product opportunities and resource-aware actions, then learn from actual outcomes.

## 29. Initial Go-To-Market
Initial beachhead:
OSTİM / Ankara

Reason:
dense B2B ecosystem, SMEs, manufacturing/supplier relationships, manageable geographic scope and potential network effects.

Expansion:
OSTİM → Ankara OSBs → Ankara → Türkiye → international.

The product should remain multi-sector even though OSTİM is the first proving ground.

## 30. Data Strategy
Do not make the product dependent on private CRM/ERP data.

Prefer legally accessible external/public signals.

Customer input should be:
- minimal
- high value
- optional where possible
- privacy-conscious

## 31. Key Open Problems
Continue research/design on:
- final event taxonomy
- graph + relational data model
- signal weighting
- counterfactual implementation
- common-cause detection
- Momentum mathematical formulation
- Timing model
- confidence calibration
- portfolio optimization
- outcome verification
- entity resolution
- source reliability
- pricing/value estimation without hallucination
- privacy/legal boundaries
- MVP scope
- minimum data required for useful predictions
- benchmark methodology
- go-to-market and onboarding

## 32. Current Next Phase
Build “Algorithm V6 Benchmark” conceptually around:
- 100 companies
- 100 products
- realistic outcomes
- limited sales capacity
- clean and poisoned data
- sector variation
- missing information
- timing variation
- counterfactual scenarios
- common-cause scenarios
- model drift

Benchmark metrics should include:
prediction quality, false positives, false negatives, timing accuracy, evidence calibration, ranking quality, resource allocation quality, catastrophic hallucination rate, robustness and recovery after bad data.

## 33. Handoff Rules for Another AI
Treat this document as the current design state, not a finished specification.

When improving it:
1. Preserve accepted principles unless strong evidence shows a flaw.
2. Criticize assumptions.
3. Propose alternatives before changing core architecture.
4. Stress-test every major algorithmic change.
5. Never invent data availability.
6. Label assumptions, unknowns and evidence.
7. Prefer useful simplicity over unnecessary complexity.
8. For every score, explain what decision it changes.
9. For every data field, explain how it can realistically be collected.
10. For every learning rule, explain how it can fail and how it will be tested.
11. Regression-test old scenarios after changes.
12. Keep the customer-facing product simpler than the internal intelligence layer.

## 34. Core Principle
> The goal is not to find more data. The goal is to make better commercial inferences from fragmented data while being explicit about uncertainty.

END — MASTER CONTEXT V6
