# Ortak Skill Havuzu — `.agents/skills/`

Bu dizinde bulunan skill’ler, **tüm ajanlar tarafından (Cline, Kilo, Roo, Claude vs.)**
paylaşılır. Ajanlar ilgili `SKILL.md`’yi okur; aynı talimata göre çalışırlar.

| Skill | Link | Kullanım Alanı |
|-------|------|----------------|
| 9router | [SKILL.md](9router/SKILL.md) | AI gateway, web search/fetch için |
| architecture-and-planning | [SKILL.md](architecture-and-planning/SKILL.md) | Mimari karar, plan |
| code-quality-and-security | [SKILL.md](code-quality-and-security/SKILL.md) | OWASP, tip güvenliği |
| cuopt-numerical-optimization-formulation | [SKILL.md](cuopt-numerical-optimization-formulation/SKILL.md) | Operatör optimizasyonu |
| data-designer | [SKILL.md](data-designer/SKILL.md) | Veri model tasarımı |
| data-designer-synthetic | [SKILL.md](data-designer-synthetic/SKILL.md) | Sentetik veri üretimi |
| data-quality-testing | [SKILL.md](data-quality-testing/SKILL.md) | Veri kalite testleri |
| dbt-testing | [SKILL.md](dbt-testing/SKILL.md) | dbt model test stratejileri |
| enterprise-data-classification | [SKILL.md](enterprise-data-classification/SKILL.md) | PII / DLP tespit |
| frontend-design | [SKILL.md](frontend-design/SKILL.md) | Web dashboard UI |
| interactive-mentor | [SKILL.md](interactive-mentor/SKILL.md) | Türkçe kodlama mentoru |
| osint-web-scraping-toolkit | [SKILL.md](osint-web-scraping-toolkit/SKILL.md) | Web kazıma + Apify webhook |
| skill-card-generator | [SKILL.md](skill-card-generator/SKILL.md) | Skill kartı üretici |
| supabase | [SKILL.md](supabase/SKILL.md) | Supabase entegrasyonu |
| supabase-postgres-best-practices | [SKILL.md](supabase-postgres-best-practices/SKILL.md) | PostgreSQL best practices |

## Eklenenlar (v2 — 2026-09-12)

- `9router` — decolua/9router skills’inden uzaktan çekildi. Apify/webhook destekli.
- `osint-web-scraping-toolkit` — projeye özel, `osint_engine.py` + webhook entegrasyonu.
- `frontend-design`, `dbt-testing` — marketplace’ten uzaktan kopyalandı.

## Marketplace bağlantısı

- `.agents/marketplace/` → **submodule** olarak pin’li (`8254e9d`).
- `.agents/marketplace/SKILLS_INDEX.md` → 189 skill envanteri (otomatik güncel).
