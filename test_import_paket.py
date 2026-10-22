import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "Huginn Data Insights"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from web_dashboard.tabs.paketler import _features
print("Import OK")

# Test
paket = {"features": ["test"]}
print(_features(paket))