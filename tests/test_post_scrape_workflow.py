import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Import the post_scrape_workflow module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import post_scrape_workflow


@pytest.fixture(autouse=True)
def izole_pano(tmp_path, monkeypatch):
    """TEST-ISO-02: ``main()`` must never write the real orchestration board.

    ``post_scrape_workflow.main()`` closes task ``P0-2`` and appends a
    handoff entry (script lines 124-131). Those constants are frozen at
    import time (``STATE_DIR / "task_board.json"`` etc.), so a test that
    only mocks ``run_step`` still rewrites the tracked
    ``data/orchestrator/task_board.json`` and ``handoffs.json`` files.
    All board targets are redirected to ``tmp_path``.
    """
    from company_master.orchestrator import task_board as tb

    monkeypatch.setattr(tb, "AUTO_SYNC", False)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    for ad, dosya in (
        ("TASK_BOARD", "task_board.json"),
        ("STATE_JSON", "state.json"),
        ("FILE_LOCKS", "file_locks.json"),
        ("TASK_MD", "gorev_panosu.md"),
        ("HANDOFF_FILE", "handoffs.json"),
        ("AGENT_SYNC_MD", "AGENT_SYNC.md"),
        ("AGENT_SYNC_MD_KOPYA", "AGENT_SYNC_kopya.md"),
    ):
        monkeypatch.setattr(tb, ad, tmp_path / dosya, raising=False)
    yield tmp_path


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