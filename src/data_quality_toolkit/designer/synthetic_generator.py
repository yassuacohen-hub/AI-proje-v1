"""Sentetik Veri Üretici Motoru (Synthetic Data Generator).

NVIDIA NeMo Data Designer vizyonunda, tanımlanan şemaya ve iş senaryolarına göre
tamamen KVKK/GDPR uyumlu, yapay ama gerçekçi kurumsal büyük veri üretir.
"""

from datetime import datetime, timedelta
import random
import string
import unicodedata
from typing import Any, Dict, List
import uuid

from .schema_builder import FieldDefinition, FieldType, SyntheticSchema


class SyntheticDataGenerator:
    """Kurumsal Sentetik Veri Üreticisi."""

    # Gerçekçi Türkçe mock veri havuzları
    FIRST_NAMES = [
        "Ahmet", "Mehmet", "Mustafa", "Ali", "Hüseyin", "Hasan", "İbrahim", "İsmail", "Osman", "Yusuf",
        "Fatma", "Ayşe", "Emine", "Hatice", "Zeynep", "Elif", "Meryem", "Şerife", "Zehra", "Sultan",
        "Burak", "Can", "Deniz", "Ege", "Kerem", "Selin", "Derya", "Cem", "Berk", "Yasemin"
    ]
    
    LAST_NAMES = [
        "Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Yıldırım", "Öztürk", "Aydın", "Özdemir",
        "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt", "Özkan", "Şimşek"
    ]

    DOMAINS = ["sirket.com.tr", "kurumsal.com", "banka.com.tr", "techcorp.io", "holding.com.tr"]

    @staticmethod
    def generate_valid_mock_tckn() -> str:
        """Algoritmik olarak geçerli sahte TCKN üretir."""
        first_digit = random.randint(1, 9)
        mid_digits = [random.randint(0, 9) for _ in range(8)]
        digits = [first_digit] + mid_digits

        odd_sum = digits[0] + digits[2] + digits[4] + digits[6] + digits[8]
        even_sum = digits[1] + digits[3] + digits[5] + digits[7]

        tenth = ((odd_sum * 7) - even_sum) % 10
        digits.append(tenth)

        eleventh = sum(digits) % 10
        digits.append(eleventh)

        return "".join(map(str, digits))

    @staticmethod
    def generate_valid_mock_credit_card() -> str:
        """Luhn algoritmasına uygun sahte Kredi Kartı numarası üretir (Mastercard/Visa başlangıçlı)."""
        prefix = random.choice(["4", "51", "52", "53", "54", "55"])
        length = 16
        needed = length - len(prefix) - 1
        payload = prefix + "".join(str(random.randint(0, 9)) for _ in range(needed))

        digits = [int(d) for d in payload]
        total = 0

        for index, digit in enumerate(reversed(digits)):
            if index % 2 == 0:
                doubled = digit * 2
                total += (doubled - 9) if doubled > 9 else doubled
            else:
                total += digit

        check_digit = (10 - (total % 10)) % 10
        card_num = payload + str(check_digit)
        return f"{card_num[:4]} {card_num[4:8]} {card_num[8:12]} {card_num[12:]}"

    @staticmethod
    def generate_mock_iban() -> str:
        """Geçerli formatta sahte TR IBAN üretir."""
        bank_code = f"{random.randint(10, 99):02d}00"
        account_no = "".join(str(random.randint(0, 9)) for _ in range(16))
        return f"TR{random.randint(10, 99):02d}{bank_code}0{account_no}"

    def generate_field_value(self, field_def: FieldDefinition) -> Any:
        """Tek bir alan tanımı için sentetik değer üretir."""
        # Boşluk (Null) olasılığı kontrolü
        if field_def.null_probability > 0 and random.random() < field_def.null_probability:
            return None

        ft = field_def.field_type

        if ft == FieldType.UUID:
            return str(uuid.uuid4())[:8]

        elif ft == FieldType.NAME:
            return f"{random.choice(self.FIRST_NAMES)} {random.choice(self.LAST_NAMES)}"

        elif ft == FieldType.EMAIL:
            first = random.choice(self.FIRST_NAMES)
            last = random.choice(self.LAST_NAMES)
            # Türkçe karakterleri email uyumlu ASCII'ye dönüştür (NFD normalization + ASCII encoding)
            first = unicodedata.normalize("NFKD", first.lower()).encode("ascii", "ignore").decode("ascii")
            last = unicodedata.normalize("NFKD", last.lower()).encode("ascii", "ignore").decode("ascii")
            return f"{first}.{last}{random.randint(1, 99)}@{random.choice(self.DOMAINS)}"

        elif ft == FieldType.PHONE:
            d1 = random.randint(0, 9)
            d2 = random.randint(0, 9)
            r1 = random.randint(100000, 999999)  # 6 hane
            return f"+90 5{d1}{d2} {r1}"

        elif ft == FieldType.TCKN_MOCK:
            return self.generate_valid_mock_tckn()

        elif ft == FieldType.CREDIT_CARD_MOCK:
            return self.generate_valid_mock_credit_card()

        elif ft == FieldType.IBAN_MOCK:
            return self.generate_mock_iban()

        elif ft == FieldType.CATEGORICAL:
            if field_def.choices:
                if field_def.weights and len(field_def.weights) == len(field_def.choices):
                    return random.choices(field_def.choices, weights=field_def.weights, k=1)[0]
                return random.choice(field_def.choices)
            return "STANDART"

        elif ft == FieldType.NUMERIC:
            min_v = field_def.min_value if field_def.min_value is not None else 0.0
            max_v = field_def.max_value if field_def.max_value is not None else 1000.0
            
            if field_def.mean is not None and field_def.std_dev is not None:
                val = random.gauss(field_def.mean, field_def.std_dev)
                val = max(min_v, min(max_v, val))
            else:
                val = random.uniform(min_v, max_v)
            return round(val, 2)

        elif ft == FieldType.DATETIME:
            start = datetime.fromisoformat(field_def.start_date) if field_def.start_date else datetime.now() - timedelta(days=365)
            end = datetime.fromisoformat(field_def.end_date) if field_def.end_date else datetime.now()
            delta_seconds = int((end - start).total_seconds())
            random_second = random.randint(0, max(delta_seconds, 1))
            return (start + timedelta(seconds=random_second)).strftime("%Y-%m-%d %H:%M:%S")

        return "N/A"

    def generate(self, schema: SyntheticSchema, row_count: int = 100) -> Dict[str, List[Any]]:
        """Şemaya uygun olarak belirtilen satır sayısında sentetik veri kümesi oluşturur."""
        dataset: Dict[str, List[Any]] = {f.name: [] for f in schema.fields}

        for _ in range(row_count):
            # Anomali enjeksiyonu kontrolü
            is_anomaly = random.random() < schema.scenario.anomaly_rate

            for f in schema.fields:
                val = self.generate_field_value(f)

                if is_anomaly and f.field_type == FieldType.NUMERIC:
                    lower = f.min_value if f.min_value is not None else 0.0
                    upper = f.max_value if f.max_value is not None else lower + 1.0
                    val = round(random.uniform(max(lower, upper * 0.8), upper), 2)

                dataset[f.name].append(val)

        return dataset
