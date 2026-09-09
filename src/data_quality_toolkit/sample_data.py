"""Örnek Kurumsal Veri Setleri Üreteci (Sample Corporate Data Generator).

Test ve sınıflandırma modüllerini doğrulamak için gerçekçi kurumsal bankacılık
ve müşteri veri setleri oluşturur.
"""

from typing import Any, Dict, List
import random

from data_quality_toolkit.classifier.pii_scanner import PIIScanner
from data_quality_toolkit.designer.synthetic_generator import SyntheticDataGenerator


def create_sample_banking_dataset(row_count: int = 50) -> Dict[str, List[Any]]:
    """Gerçekçi kurumsal bankacılık işlem verisi üretir (Hassas PII ve anomaliler içerir)."""
    dataset: Dict[str, List[Any]] = {
        "transaction_id": [],
        "customer_tckn": [],
        "card_number": [],
        "customer_email": [],
        "customer_phone": [],
        "city": [],
        "amount_tl": [],
        "status": [],
    }

    cities = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"]
    statuses = ["COMPLETED", "COMPLETED", "COMPLETED", "PENDING", "FAILED"]

    for i in range(1, row_count + 1):
        dataset["transaction_id"].append(f"TXN-{1000 + i}")
        
        # %90 geçerli TCKN, %10 eksik/hatalı
        if random.random() < 0.90:
            dataset["customer_tckn"].append(SyntheticDataGenerator.generate_valid_mock_tckn())
        else:
            dataset["customer_tckn"].append(None if random.random() < 0.5 else "11111111110")

        # %95 geçerli kart, %5 maskeli
        dataset["card_number"].append(SyntheticDataGenerator.generate_valid_mock_credit_card())

        # Email & Telefon
        name = random.choice(SyntheticDataGenerator.FIRST_NAMES).lower()
        dataset["customer_email"].append(f"{name}{i}@kurumsal.com" if random.random() < 0.92 else "gecersiz_email")
        dataset["customer_phone"].append(f"+90 532 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}")

        # Şehir
        dataset["city"].append(random.choice(cities))

        # Tutar (Arada negatif veya olağandışı tutar anomalisi)
        if random.random() < 0.05:
            dataset["amount_tl"].append(-150.0)  # Kural ihlali (Negatif tutar)
        elif random.random() < 0.03:
            dataset["amount_tl"].append(1_500_000.0)  # Fraud anomali
        else:
            dataset["amount_tl"].append(round(random.uniform(50.0, 15000.0), 2))

        dataset["status"].append(random.choice(statuses))

    return dataset
