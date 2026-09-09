"""Platform Birim Testleri (Unit Tests).

Tüm modüllerin (Sınıflandırma, Sentetik Üretici ve Kalite Motoru) doğruluğunu test eder.
"""

import os
import sys
import unittest

# src dizinini python path'ine ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from data_quality_toolkit.classifier import PIIScanner, SensitivityLevel
from data_quality_toolkit.classifier.schema_profiler import SchemaProfiler
from data_quality_toolkit.designer.schema_builder import FieldDefinition, FieldType, ScenarioConfig, SyntheticSchema
from data_quality_toolkit.designer.synthetic_generator import SyntheticDataGenerator
from data_quality_toolkit.validator.quality_engine import DataQualityEngine
from data_quality_toolkit.validator.rules import NotNullRule, RangeRule, UniqueRule


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
        self.assertFalse(self.scanner.validate_luhn_credit_card("1111 2222 3333 4445"))

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

    # ===========================================
    # YENI TESTLER - GENİŞLETİLMİŞ COVERAGE
    # ===========================================

    def test_email_validation(self):
        """E-posta doğrulama testi."""
        valid_emails = [
            "user@example.com",
            "test.user+tag@domain.co.uk",
            "name_123@subdomain.example.com",
        ]
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
        ]
        
        for email in valid_emails:
            result = self.scanner.classify_value(email)
            self.assertEqual(result, "EMAIL", f"E-posta doğrulanmalı: {email}")
        
        for email in invalid_emails:
            result = self.scanner.classify_value(email)
            self.assertNotEqual(result, "EMAIL", f"Geçersiz e-posta: {email}")

    def test_phone_validation(self):
        """Telefon numarası doğrulama testi."""
        valid_phones = [
            "+90 500 123456",  # Türkiye: +90 5XX XXXXXX
            "0500123456",      # Türkiye: 0 5XX XXXXXX
            "+1 2025551234",   # Uluslararası
        ]
        invalid_phones = [
            "123",
            "555-1234",
            "+90 400 123456",  # Türkiye'de geçersiz (4 ile başlayan)
            "+90 600 123456",  # Türkiye'de geçersiz (6 ile başlayan)
        ]
        
        for phone in valid_phones:
            result = self.scanner.classify_value(phone)
            self.assertEqual(result, "PHONE", f"Telefon doğrulanmalı: {phone}")
        
        for phone in invalid_phones:
            result = self.scanner.classify_value(phone)
            self.assertNotEqual(result, "PHONE", f"Geçersiz telefon: {phone}")

    def test_iban_validation(self):
        """IBAN doğrulama testi."""
        valid_iban = self.generator.generate_mock_iban()
        self.assertEqual(self.scanner.classify_value(valid_iban), "IBAN")
        
        # Geçersiz IBAN'lar
        self.assertFalse(self.scanner.classify_value("DE89370400440532013000"))  # Türkiye değil
        self.assertFalse(self.scanner.classify_value("TR123"))  # Çok kısa

    def test_synthetic_email_generation(self):
        """Sentetik e-posta üretimi testi."""
        schema = SyntheticSchema(schema_name="EmailTest")
        schema.add_field(FieldDefinition("email", FieldType.EMAIL))
        
        data = self.generator.generate(schema, row_count=10)
        self.assertEqual(len(data["email"]), 10)
        
        # Tüm e-postaları doğrula
        for email in data["email"]:
            if email is not None:
                result = self.scanner.classify_value(email)
                self.assertEqual(result, "EMAIL", f"Üretilen e-posta doğrulanmalı: {email}")

    def test_synthetic_phone_generation(self):
        """Sentetik telefon numarası üretimi testi."""
        schema = SyntheticSchema(schema_name="PhoneTest")
        schema.add_field(FieldDefinition("phone", FieldType.PHONE))
        
        data = self.generator.generate(schema, row_count=10)
        self.assertEqual(len(data["phone"]), 10)
        
        # Tüm telefon numaralarını doğrula
        for phone in data["phone"]:
            if phone is not None:
                result = self.scanner.classify_value(phone)
                self.assertEqual(result, "PHONE", f"Üretilen telefon doğrulanmalı: {phone}")

    def test_synthetic_iban_generation(self):
        """Sentetik IBAN üretimi testi."""
        schema = SyntheticSchema(schema_name="IbanTest")
        schema.add_field(FieldDefinition("iban", FieldType.IBAN_MOCK))
        
        data = self.generator.generate(schema, row_count=10)
        self.assertEqual(len(data["iban"]), 10)
        
        # Tüm IBAN'ları doğrula
        for iban in data["iban"]:
            if iban is not None:
                result = self.scanner.classify_value(iban)
                self.assertEqual(result, "IBAN", f"Üretilen IBAN doğrulanmalı: {iban}")

    def test_column_classification_email(self):
        """E-posta sütunu sınıflandırma testi."""
        emails = [
            "user1@example.com",
            "user2@domain.com",
            "user3@mail.org",
            "user4@company.tr",
            "user5@site.net",
        ]
        result = self.scanner.scan_column("customer_email", emails)
        self.assertEqual(result.detected_type, "EMAIL")
        self.assertEqual(result.sensitivity_level, SensitivityLevel.INTERNAL)

    def test_column_classification_phone(self):
        """Telefon sütunu sınıflandırma testi."""
        phones = [
            "+90 500 123 45 67",
            "+90 501 234 56 78",
            "+90 502 345 67 89",
            "+90 503 456 78 90",
            "+90 504 567 89 01",
        ]
        result = self.scanner.scan_column("contact_phone", phones)
        self.assertEqual(result.detected_type, "PHONE")
        self.assertEqual(result.sensitivity_level, SensitivityLevel.INTERNAL)

    def test_mixed_pii_detection(self):
        """Karışık PII türü tespiti testi."""
        mixed_data = [
            self.generator.generate_valid_mock_tckn(),
            self.generator.generate_valid_mock_credit_card(),
            self.generator.generate_mock_iban(),
            "user@example.com",
            "+90 500 123456",
        ]
        
        # Her bir değerin doğru şekilde tespit edildiğini kontrol et
        results = [self.scanner.classify_value(val) for val in mixed_data]
        expected = ["TCKN", "CREDIT_CARD", "IBAN", "EMAIL", "PHONE"]
        
        for result, expected_type in zip(results, expected):
            self.assertEqual(result, expected_type)

    def test_null_handling(self):
        """Null/None değer işleme testi."""
        # None değer
        self.assertIsNone(self.scanner.classify_value(None))
        
        # Boş string
        self.assertIsNone(self.scanner.classify_value(""))
        
        # Sütun boşsa
        result = self.scanner.scan_column("empty_col", [None, None, None])
        self.assertEqual(result.detected_type, "EMPTY")

    def test_synthetic_data_with_null_probability(self):
        """Null olasılığı ile sentetik veri testi."""
        schema = SyntheticSchema(schema_name="NullTest")
        schema.add_field(
            FieldDefinition("optional_field", FieldType.EMAIL, null_probability=0.5)
        )
        
        data = self.generator.generate(schema, row_count=100)
        
        # Yaklaşık %50'si None olmalı (tolerance: %30-%70)
        none_count = sum(1 for val in data["optional_field"] if val is None)
        null_ratio = none_count / len(data["optional_field"])
        
        self.assertTrue(0.3 <= null_ratio <= 0.7, 
                       f"Null oranı: {null_ratio}, beklenen: ~0.5")


if __name__ == "__main__":
    unittest.main()
