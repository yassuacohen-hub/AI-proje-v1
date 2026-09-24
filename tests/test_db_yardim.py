"""UI-ADMIN-SAHTE-KPI-01: tablo_var_mi() için assert tabanlı test."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, text
from web_dashboard.tabs._db_yardim import tablo_var_mi


def test_tablo_var_mi_var_olan_tablo():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE ornek_tablo (id INTEGER)"))
        conn.commit()
    assert tablo_var_mi("ornek_tablo", engine) is True


def test_tablo_var_mi_olmayan_tablo():
    engine = create_engine("sqlite:///:memory:")
    assert tablo_var_mi("olmayan_tablo", engine) is False


if __name__ == "__main__":
    test_tablo_var_mi_var_olan_tablo()
    test_tablo_var_mi_olmayan_tablo()
    print("OK")
