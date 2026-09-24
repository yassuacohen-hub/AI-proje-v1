import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

from data_quality_toolkit.validator import (
    DataQualityEngine, NotNullRule, UniqueRule, RangeRule
)


def test_not_null_rule_pass():
    rule = NotNullRule("id")
    res = rule.evaluate([1, 2, 3])
    assert res.passed is True
    assert res.failed_records == 0


def test_not_null_rule_fail():
    rule = NotNullRule("id")
    res = rule.evaluate([1, None, 3])
    assert res.passed is False
    assert res.failed_records == 1


def test_unique_rule_pass():
    rule = UniqueRule("id")
    res = rule.evaluate([1, 2, 3])
    assert res.passed is True


def test_unique_rule_fail():
    rule = UniqueRule("id")
    res = rule.evaluate([1, 1, 2])
    assert res.passed is False
    assert res.failed_records == 1


def test_range_rule():
    rule = RangeRule("amount", min_val=0, max_val=100)
    res = rule.evaluate([10, 50, 200])
    assert res.passed is False
    assert res.failed_records == 1


def test_engine_aggregates_score():
    engine = DataQualityEngine()
    engine.add_rule(NotNullRule("a"))
    engine.add_rule(UniqueRule("a"))
    dataset = {"a": [1, 2, 3]}
    report = engine.validate(dataset)
    assert report.data_quality_score == 100.0
