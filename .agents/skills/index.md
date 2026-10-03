# Ortak Skill Havuzu — `.agents/skills/`

Bu dizinde bulunan skill’ler, **tüm ajanlar tarafından (Cline, Kilo, Roo, Claude vs.)**
paylaşılır. Ajanlar ilgili `SKILL.md`’yi okur; aynı talimata göre çalışırlar.

| Skill | Link | Kullanım Alanı |
|-------|------|----------------|
| 9router | [SKILL.md](9router/SKILL.md) | AI gateway, web search/fetch için |
| architecture-and-planning | [SKILL.md](architecture-and-planning/SKILL.md) | Mimari karar, plan |
| business-plan-template | [SKILL.md](business-plan-template/SKILL.md) | OSINT pazarlama iş modeli, ROI canvas |
| code-optimization | [SKILL.md](code-optimization/SKILL.md) | Python, SQL, JS performans optimizasyonu |
| code-quality-and-security | [SKILL.md](code-quality-and-security/SKILL.md) | OWASP, tip güvenliği |
| cuopt-numerical-optimization-formulation | [SKILL.md](cuopt-numerical-optimization-formulation/SKILL.md) | Operatör optimizasyonu |
| data-designer | [SKILL.md](data-designer/SKILL.md) | Veri model tasarımı |
| data-designer-synthetic | [SKILL.md](data-designer-synthetic/SKILL.md) | Sentetik veri üretimi |
| data-quality-testing | [SKILL.md](data-quality-testing/SKILL.md) | Veri kalite testleri |
| dbt-testing | [SKILL.md](dbt-testing/SKILL.md) | dbt model test stratejileri |
| enterprise-data-classification | [SKILL.md](enterprise-data-classification/SKILL.md) | PII / DLP tespit |
| huginn-mimir-dis | [SKILL.md](huginn-mimir-dis/SKILL.md) | Mimir-DIŞ müşteri paneli: tenant sandbox, RAG/ingestion (ortak), prompt-injection red-team, GO/NO-GO kapısı |
| huginn-mimir-ic | [SKILL.md](huginn-mimir-ic/SKILL.md) | Mimir-İÇ (ODIN) admin paneli: TEKLİF + kilit sözü kapısı, LoRA eğitim seti, iç red-team |
| elite-product-ux-architect | [SKILL.md](elite-product-ux-architect/SKILL.md) | UX mimarisi, dashboard, karar odaklı tasarım |
| elite-saas-architect | [SKILL.md](elite-saas-architect/SKILL.md) | Sistem mimarisi, SaaS değerlendirme, ölçeklenebilirlik |
| frontend-design | [SKILL.md](frontend-design/SKILL.md) | Web dashboard UI |
| interactive-mentor | [SKILL.md](interactive-mentor/SKILL.md) | Türkçe kodlama mentoru |
| marketing-strategy | [SKILL.md](marketing-strategy/SKILL.md) | Lead skor → CRM pipeline |
| osint-web-scraping-toolkit | [SKILL.md](osint-web-scraping-toolkit/SKILL.md) | Web kazıma + Apify webhook + Ticari/OSINT istihbarat |
| senior-engineer | [SKILL.md](senior-engineer/SKILL.md) | Senior yazılımcı, mimari, debug, performans |
| skill-bekci | [SKILL.md](skill-bekci/SKILL.md) | Skill havuzu nöbetçisi |
| skill-card-generator | [SKILL.md](skill-card-generator/SKILL.md) | Skill kartı üretici |
| streemit-product-intelligence | [SKILL.md](streemit-product-intelligence/SKILL.md) | Streemit ürün stratejisi, ticari istihbarat, müşteri değeri |
| supabase | [SKILL.md](supabase/SKILL.md) | Supabase entegrasyonu |
| supabase-postgres-best-practices | [SKILL.md](supabase-postgres-best-practices/SKILL.md) | PostgreSQL best practices |
| venture-category-architect | [SKILL.md](venture-category-architect/SKILL.md) | Kategori yaratma, konumendirme, marka, Büyüme |

## Eklenenlar (v2 — 2026-09-12)

- `9router` — decolua/9router skills’inden uzaktan çekildi. Apify/webhook destekli.
- `osint-web-scraping-toolkit` — projeye özel, `osint_engine.py` + webhook entegrasyonu.
- `frontend-design`, `dbt-testing` — marketplace’ten uzaktan kopyalandı.

## Marketplace bağlantısı

- `.agents/marketplace/` → **submodule** olarak pin’li (`8254e9d`).
- `.agents/marketplace/SKILLS_INDEX.md` → 189 skill envanteri (otomatik güncel).
