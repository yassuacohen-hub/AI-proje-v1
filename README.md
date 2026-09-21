[[Huginn Data Insights/data/skills/supabase/README.md]]

# Ankara B2B Company Master

## Overview
This is an OSINT (Open Source Intelligence) data collection and processing system for Ankara businesses.

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run OSINT Scraper Motoru

**Status Check:**
```bash
python scripts/osint_engine.py status
```

**Run Quality Gate (with production data):**
```bash
# Via module
python -m company_master.engine.osint_engine quality ostim-detail --min-score 30

# Or via CLI wrapper
python scripts/osint_engine.py quality ostim-detail --min-score 30
```

### Wiki Automation

The system includes automated wiki maintenance for the internal knowledge base:

**Individual Scripts:**
```bash
# Ingest new/updated wiki pages
python wiki_automation/wiki_ingest.py

# Sync agent/task data to wiki
python wiki_automation/wiki_sync_agents.py

# Lint wiki health
python wiki_automation/wiki_lint.py          # Health check
python wiki_automation/wiki_lint.py --fix    # Auto-fix issues
python wiki_automation/wiki_lint.py --ci     # CI mode (exits 1 on errors)

# Update wiki index
python wiki_automation/wiki_index.py
```

**Full Automation:**
```bash
# Run all steps and commit changes
python wiki_automation/run_all.py --fix --commit
```

## Project Structure

```
src/
├── company_master/
│   ├── engine/
│   │   ├── osint_engine.py          # Main CLI (status, check, run, pipeline, quality)
│   │   ├── quality_gate.py          # Data quality filtering (DB + DQT scoring)
│   │   └── source_registry.py       # Data source definitions
│   └── utils/
│       └── scraping_permission_router.py  # robots.txt, KVKK, rate limiting
scripts/
├── osint_engine.py                  # CLI wrapper with PYTHONPATH
├── post_scrape_workflow.py          # Quality gate -> ingest -> VKN -> quality -> KPI
└── scrape_watcher.py                # File-system based workflow trigger
wiki_automation/
├── wiki_ingest.py                   # Detect new/updated wiki pages
├── wiki_sync_agents.py              # Sync task_board to agent wiki pages
├── wiki_lint.py                     # Wiki health checker (--fix available)
├── wiki_index.py                    # Generate wiki index
└── run_all.py                       # Orchestrator for full automation
docs/
└── OSINT_SCRAPER_MOTORU.md          # Detailed documentation
```

## Data Flow

1. **Scrape**: Data collected from sources (respecting robots.txt/KVKK)
2. **Quality Gate**: Filters records using combined DB score (0-100) + DQT rules
3. **Post-Process**: VKN enrichment, footer updates, KPI calculation
4. **Wiki Sync**: Automated updates to internal knowledge base
5. **Dashboard**: Streamlit interface for data exploration

## Admin Panel Faz 2

Admin dashboard sekmeleri `web_dashboard/tabs/` altında bulunur:

- `admin_auth.py`: Admin oturumu ve token kontrolü
- `admin_kpi.py`: Firma, kullanıcı, API, sinyal ve kalite KPI'ları
- `admin_performance.py`: Sorgu gecikmesi, cache ve Prometheus metrikleri
- `admin_audit.py`: Karar, dosya kilidi, handoff ve trigger kayıtları
- `admin_panel.py`: Karar defteri görünümü
- `admin_extras.py`: API kullanımı ve kullanıcı yönetimi
- `webhook_monitor.py`: Webhook sağlık durumu, olaylar ve DLQ

Dashboard'ı çalıştırmak için:

```bash
streamlit run app.py
```

Sekme testlerini çalıştırmak için:

```bash
python -m pytest tests/test_web_dashboard_tabs.py tests/test_admin_extras.py
```

## Configuration

- Minimum quality score: Adjustable via `--min-score` (default: 30)
- Task board: `data/orchestrator/task_board.json`
- Wiki location: `AI proje v1/V10/wiki/`

## Development

Run tests:
```bash
python -m pytest tests/
```

Lint Python code:
```bash
# Using existing wiki_lint as example
python wiki_automation/wiki_lint.py --ci
```

## İlgili Nodlar (GRAPH-FIX-02 Backlink)

- [[Huginn Data Insights/data_worktree/orchestrator/gorev_panosu]]
- [[Huginn Data Insights/data/orchestrator/gorev_panosu]]
- [[VAULT_AUTOMATION_TEMPLATE]]
- [[Huginn Data Insights/AI proje v1/V10/CHANGELOG]]
