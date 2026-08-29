"""Platform Birim Testleri (Unit Tests).

Tüm modüllerin (Sınıflandırma, Sentetik Üretici ve Kalite Motoru) doğruluğunu test eder.
"""

import os
import sys
import unittest

# src dizinini python path'ine ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from classifier.pii_scanner import PIIScanner, SensitivityLevel
from classifier.schema_profiler import SchemaProfiler
from designer.schema_builder import FieldDefinition, FieldType, ScenarioConfig, SyntheticSchema
from designer.synthetic_generator import SyntheticDataGenerator
from validator.quality_engine import DataQualityEngine
from validator.rules import NotNullRule, RangeRule, UniqueRule


class TestEnterpriseDataPlatform(unittest.TestCase):
    """Platformun temel bileşenlerinin birim testleri."""

    def setUp(self):
        self.scanner = PIIScanner()
        self.profiler = SchemaProfiler()
        self.generator = SyntheticDataGenerator()
        self.engine = DataQualityEngine()

    def test_tckn_algorithm(self):
        """TCKN algoritması doğrulama testi."""
        # Geçerli sahte TCKN üret ve doğrula
        valid_tckn = self.generator.generate_valid_mock_tckn()
        self.assertTrue(self.scanner.validate_tckn(valid_tckn))

        # Geçersiz TCKN'ler
        self.assertFalse(self.scanner.validate_tckn("01234567890"))  # İlk hane 0
        self.assertFalse(self.scanner.validate_tckn("12345678901"))  # Algoritma tutarsız
        self.assertFalse(self.scanner.validate_tckn("123"))          # Kısa

    def test_luhn_credit_card(self):
        """Kredi kartı Luhn algoritması testi."""
        valid_card = self.generator.generate_valid_mock_credit_card()
        self.assertTrue(self.scanner.validate_luhn_credit_card(valid_card))
        self.assertFalse(self.scanner.validate_luhn_credit_card("1111 2222 3333 4444"))

    def test_pii_scanner_column(self):
        """Sütun sınıflandırma ve güvenlik seviyesi testi."""
        cards = [self.generator.generate_valid_mock_credit_card() for _ in range(10)]
        res = self.scanner.scan_column("kredi_karti", cards)
        self.assertEqual(res.detected_type, "CREDIT_CARD")
        self.assertEqual(res.sensitivity_level, SensitivityLevel.RESTRICTED)

    def test_synthetic_data_generation(self):
        """Sentetik veri üretimi testi."""
        schema = SyntheticSchema(schema_name="TestSchema")
        schema.add_field(FieldDefinition("id", FieldType.UUID))
        schema.add_field(FieldDefinition("name", FieldType.NAME))
        schema.add_field(FieldDefinition("balance", FieldType.NUMERIC, min_value=100.0, max_value=500.0))

        data = self.generator.generate(schema, row_count=20)
        self.assertEqual(len(data["id"]), 20)
        self.assertEqual(len(data["name"]), 20)
        self.assertEqual(len(data["balance"]), 20)
        for b in data["balance"]:
            self.assertTrue(100.0 <= b <= 500.0)

    def test_quality_engine_rules(self):
        """Veri kalitesi motoru ve kuralları testi."""
        test_dataset = {
            "user_id": [1, 2, 3, 4, 5],
            "age": [25, 30, 45, -5, 150],  # 2 geçersiz yaş
            "email": ["a@b.com", "c@d.com", None, "e@f.com", "g@h.com"],  # 1 boş email
        }

        self.engine.add_rule(NotNullRule("user_id"))
        self.engine.add_rule(UniqueRule("user_id"))
        self.engine.add_rule(NotNullRule("email"))
        self.engine.add_rule(RangeRule("age", min_val=0, max_val=120))

        report = self.engine.validate(test_dataset)

        self.assertEqual(report.total_rules_evaluated, 4)
        self.assertEqual(report.passed_rules_count, 2)  # user_id not_null ve unique geçti
        self.assertEqual(report.failed_rules_count, 2)  # email not_null ve age range kaldı
        self.assertTrue(0.0 <= report.data_quality_score <= 100.0)


if __name__ == "__main__":
    unittest.main()
