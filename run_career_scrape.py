import sys, os, logging, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
logging.getLogger("urllib3").setLevel(logging.ERROR)
ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://huginn:huginn_local_dev@localhost:5433/huginn")
from company_master.intelligence.job_intelligence.sources.company_career import CompanyCareerSource
src = CompanyCareerSource()
jobs = src.run_full_scrape(max_pages=500, output_file="data/job_intelligence/company_career_jobs.jsonl")
print("Scrape complete:", len(jobs), "jobs found from ~500 companies")
for j in jobs[:5]:
    print("  -", j.raw_data.get("company_name"), "(", j.raw_data.get("job_cards_found", 0), "cards):", j.title)
