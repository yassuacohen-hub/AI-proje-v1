import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Import the post_scrape_workflow module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import post_scrape_workflow


def test_run_step_success():
    """Test that run_step executes successfully when script returns 0."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        rc = post_scrape_workflow.run_step("Test Step", "dummy_script.py")
        assert rc == 0
        mock_run.assert_called_once()


def test_run_step_failure():
    """Test that run_step returns error code when script fails."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        rc = post_scrape_workflow.run_step("Test Step", "dummy_script.py")
        assert rc == 1


def test_run_vkn_validation_disabled():
    """Test VKN validation when disabled in config."""
    with patch('company_master.engine.quality_gate.load_quality_config') as mock_load_config, \
         patch('subprocess.run') as mock_run:
        mock_load_config.return_value = {
            "post_scrape": {
                "validate_vkn": False
            }
        }
        
        rc = post_scrape_workflow.run_vkn_validation()
        assert rc == 0  # Should skip and return 0
        mock_run.assert_not_called()


def test_run_vkn_validation_enabled():
    """Test VKN validation when enabled in config."""
    with patch('company_master.engine.quality_gate.load_quality_config') as mock_load_config, \
         patch('subprocess.run') as mock_run:
        
        mock_load_config.return_value = {
            "post_scrape": {
                "validate_vkn": True,
                "dedup": True,
                "dedup_fields": ["legal_name", "trade_name", "tax_number", "vergi_no"],
            },
            "quality_gate": {
                "min_score": 30
            }
        }
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        rc = post_scrape_workflow.run_vkn_validation()
        assert rc == 0
        
        # Verify subprocess was called with correct arguments
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == sys.executable
        assert "validate_vkn_duplicate.py" in args[1]
        assert "--dedup" in args
        assert "--min-score" in args
        assert "30" in args


def test_main_calls_vkn_validation():
    """Test that main() calls run_vkn_validation first."""
    with patch('post_scrape_workflow.run_vkn_validation') as mock_vkn, \
         patch('post_scrape_workflow.run_step') as mock_step:
        
        mock_vkn.return_value = 0
        mock_step.return_value = 0
        
        rc = post_scrape_workflow.main()
        assert rc == 0
        
        # Verify run_vkn_validation was called first
        mock_vkn.assert_called_once()
        
        # Verify other steps were called after
        assert mock_step.call_count >= 3  # At least quality gate, VKN dedup, recalc, KPI


def test_main_returns_early_on_vkn_failure():
    """Test that main returns early if VKN validation fails."""
    with patch('post_scrape_workflow.run_vkn_validation') as mock_vkn, \
         patch('post_scrape_workflow.run_step') as mock_step:
        
        mock_vkn.return_value = 1  # Failure
        mock_step.return_value = 0
        
        rc = post_scrape_workflow.main()
        assert rc == 1
        
        # Verify VKN validation was called
        mock_vkn.assert_called_once()
        
        # Verify other steps were NOT called
        mock_step.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])