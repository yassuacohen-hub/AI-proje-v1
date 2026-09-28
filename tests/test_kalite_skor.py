"""KALITE-SKOR-01 / D-249 mandali: 'veri yok' ile '0 puan' ayrilir."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from company_master.etl.quality_metrics import (  # noqa: E402
    calculate_employee_count_score,
    calculate_job_postings_score,
    calculate_source_diversity_score,
)


def test_veri_yok_none_doner():
    assert calculate_source_diversity_score(None) is None
    assert calculate_source_diversity_score(0) is None
    assert calculate_employee_count_score(None) is None
    assert calculate_job_postings_score(None) is None


def test_veri_var_sifir_puan_none_degil():
    assert calculate_source_diversity_score(1) == 0
    assert calculate_employee_count_score(0) == 0
    assert calculate_job_postings_score(0) == 0


def test_kademeler_bozulmadi():
    assert calculate_source_diversity_score(2) == 2
    assert calculate_source_diversity_score(5) == 5
    assert calculate_employee_count_score(75) == 4
    assert calculate_job_postings_score(25) == 8


if __name__ == "__main__":
    test_veri_yok_none_doner()
    test_veri_var_sifir_puan_none_degil()
    test_kademeler_bozulmadi()
    print("3 mandal gecti")
