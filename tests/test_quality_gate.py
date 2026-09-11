import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from company_master.engine.quality_gate import QualityGate, load_quality_config


def test_load_quality_config():
    """Test that quality config loads correctly."""
    config = load_quality_config()
    assert config is not None
    assert "quality_gate" in config
    assert config["quality_gate"]["min_score"] == 30.0
    assert config["quality_gate"]["db_weight"] == 0.7
    assert config["quality_gate"]["dqt_weight"] == 0.3


def test_quality_gate_init_with_config():
    """Test QualityGate init uses config values."""
    gate = QualityGate()
    # Should use config min_score (30.0)
    assert gate.min_score == 30.0
    # Should have db_weights from config
    assert isinstance(gate.db_weights, dict)
    assert "tax_number" in gate.db_weights
    assert gate.db_weights["tax_number"] == 15


def test_quality_gate_init_override_min_score():
    """Test that explicit min_score overrides config."""
    gate = QualityGate(min_score=50.0)
    assert gate.min_score == 50.0


def test_quality_gate_default_rules():
    """Test that default rules are set correctly."""
    gate = QualityGate()
    assert hasattr(gate, 'DEFAULT_RULES')
    assert len(gate.DEFAULT_RULES) > 0
    # Check that rules are tuples of (column_name, rule_class, kwargs)
    for rule_tuple in gate.DEFAULT_RULES:
        assert len(rule_tuple) == 3
        assert isinstance(rule_tuple[0], str)  # column name
        assert isinstance(rule_tuple[1], type)  # rule class
        assert isinstance(rule_tuple[2], dict)  # kwargs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])