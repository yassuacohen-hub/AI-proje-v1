import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scripts.recalculate_quality_scores import recalculate
from scripts.generate_kpi_report import main as generate_report

print("=== Kalite Skorlari Yeniden Hesaplaniyor ===")
updated = recalculate()
print(f"Guncellenen kayit: {updated}")

print("\n=== KPI Rapor Uretiliyor ===")
generate_report()