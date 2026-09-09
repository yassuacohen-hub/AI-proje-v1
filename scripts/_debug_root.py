"""Debug: _find_root testi."""
from pathlib import Path

here = Path("AI proje v1/src/company_master/db/connection.py").resolve()
print("here:", here)
for c in [here, *here.parents]:
    print("  cand:", c, "has_env:", (c / ".env").exists())